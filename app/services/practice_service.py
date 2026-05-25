from app.models import User


def generate_sentences_from_pdf_mock(_: bytes) -> list[str]:
    # TODO: PDF 텍스트 추출 및 LLM 기반 문장 생성 로직으로 교체한다.
    return [
        "타닥캠퍼스에서 짧은 문장을 연습합니다.",
        "정확하게 입력하면 더 많은 포인트를 얻습니다.",
        "PDF 원본과 생성 문장은 저장하지 않습니다.",
    ]


def calculate_practice_point(completed_count: int, accuracy: float, speed: float) -> int:
    base = completed_count * 10
    accuracy_bonus = int(base * (accuracy / 100))
    speed_bonus = int(speed // 50)
    return max(0, base + accuracy_bonus + speed_bonus)


def add_practice_point(user: User, earned_point: int) -> None:
    user.point += earned_point
