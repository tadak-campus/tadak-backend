import os

import json
from google import genai
from google.genai import types
from app.models import User


def generate_sentences_from_pdf(pdf_file: bytes) -> list[str]:
    if not pdf_file:
        raise ValueError("PDF 파일 비어있습니다")


    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        raise ValueError("GEMINI_API_KEY 환경 변수가 설정되어 있지 않습니다")
    client = genai.Client(
        api_key = api_key,
    )

    response = client.models.generate_content(
        model="gemini-3.1-flash-lite",
        contents=[
            types.Part.from_bytes(
                data=pdf_file,
                mime_type='application/pdf',
            ),
            prompt
        ]
    )

    try:
        sentences = json.loads(response.text)
    except json.JSONDecodeError as exc:
        raise ValueError(f"AI 문장 생성 결과 해석 불가\n\n{response.text}")

    if not isinstance(sentences, list):
        raise ValueError("문장 생성 결과 형식이 올바르지 않습니다. JSON 배열이 필요합니다.")

    return [
        sentence.strip()
        for sentence in sentences
        if isinstance(sentence, str) and sentence.strip()
    ]


def calculate_practice_point(completed_count: int, accuracy: float, speed: float) -> int:
    base = completed_count * 10
    accuracy_bonus = int(base * (accuracy / 100))
    speed_bonus = int(speed // 50)
    return max(0, base + accuracy_bonus + speed_bonus)


def add_practice_point(user: User, earned_point: int) -> None:
    user.point += earned_point

prompt = """
업로드된 PDF 학습자료를 읽고 타이핑 연습에 적합한 한국어 문장만 골라줘.


- 결과는 JSON 배열만 반환한다.
- 배열 원소는 문자열이다.
- 10개에서 15개 정도만 반환한다.
- 너무 짧거나 너무 긴 문장은 제외한다.
- 표, 차트, 제목만 있는 내용은 자연스러운 문장으로 바꾸거나 출제하지 마라.
- 설명 문장, 마크다운, 코드블록은 절대 넣지 않는다.

예시:
["첫 번째 연습 문장입니다.", "두 번째 연습 문장입니다."]
"""