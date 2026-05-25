# 타닥캠퍼스 FastAPI 백엔드 MVP

PDF 학습자료 기반 타이핑 연습과 포인트 상점 기능을 위한 FastAPI MVP입니다.  
카카오 로그인, PDF/LLM 처리, AWS S3 업로드는 실제 연동하지 않고 교체 가능한 mock 함수로 분리했습니다.

## 기술 스택

- FastAPI
- SQLAlchemy
- SQLite
- pytest

## 설치

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

## 실행

```bash
uvicorn app.main:app --reload
```

서버 실행 후 Swagger 문서는 아래에서 확인할 수 있습니다.

```text
http://127.0.0.1:8000/docs
```

기본 DB는 프로젝트 루트의 `tadak.db` SQLite 파일입니다. 다른 DB 파일을 쓰려면 `DATABASE_URL`을 지정합니다.

```bash
DATABASE_URL=sqlite:///./local.db uvicorn app.main:app --reload
```

## 테스트

```bash
pytest
```

테스트는 다음 흐름을 확인합니다.

- mock 카카오 로그인으로 신규 유저 생성 및 JWT 반환
- JWT로 `/api/users/me` 호출
- 상점 아이템 목록 조회
- 아이템 구매 시 포인트 차감 및 보유 아이템 생성
- 보유 아이템 장착
- 연습 완료 API 호출 시 포인트 증가

## 구현된 API

```http
POST /api/auth/kakao/login
GET  /api/users/me
POST /api/practice/generate
POST /api/practice/complete
GET  /api/shop/items
GET  /api/shop/my-items
POST /api/shop/items/{item_id}/buy
POST /api/shop/items/{item_id}/equip
```

## mock 교체 지점

- `app/services/auth_service.py`
  - `verify_kakao_login_mock`: 추후 실제 카카오 access token 검증 API 호출로 교체
- `app/services/practice_service.py`
  - `generate_sentences_from_pdf_mock`: 추후 PDF 텍스트 추출 및 LLM 문장 생성으로 교체
- `app/services/shop_service.py`
  - seed 데이터의 `example.com` URL: 추후 AWS S3 URL로 교체

## 제외한 기능

MVP 범위에 맞춰 아래 기능과 테이블은 구현하지 않았습니다.

- 자체 username/password 로그인
- profile_image_url 저장
- PDF 원본 저장
- 생성 문장 저장
- 연습 기록 저장
- point_transactions, practice_sessions, uploaded_files, generated_sentences 테이블
- 관리자 기능, 랭킹, 통계, 자료 보관함, 정교한 어뷰징 방지
