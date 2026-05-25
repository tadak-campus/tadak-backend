import base64
import hashlib
import hmac
import json
import os
import time

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.models import User


JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY", "tadak-dev-secret")
JWT_EXPIRE_SECONDS = 60 * 60 * 24


def verify_kakao_login_mock(kakao_id: str, profile_nickname: str) -> dict[str, str]:
    # TODO: 실제 카카오 access token 검증 API 호출로 교체한다.
    return {"kakao_id": kakao_id, "profile_nickname": profile_nickname}


def get_or_create_user(db: Session, kakao_id: str, profile_nickname: str) -> User:
    user = db.query(User).filter(User.kakao_id == kakao_id).first()
    if user:
        user.profile_nickname = profile_nickname
        db.commit()
        db.refresh(user)
        return user

    user = User(kakao_id=kakao_id, profile_nickname=profile_nickname, point=1000)
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


def _b64url_encode(data: bytes) -> str:
    return base64.urlsafe_b64encode(data).rstrip(b"=").decode("utf-8")


def _b64url_decode(data: str) -> bytes:
    padding = "=" * (-len(data) % 4)
    return base64.urlsafe_b64decode(data + padding)


def create_access_token(user_id: int) -> str:
    header = {"alg": "HS256", "typ": "JWT"}
    payload = {"sub": str(user_id), "exp": int(time.time()) + JWT_EXPIRE_SECONDS}
    signing_input = ".".join(
        [
            _b64url_encode(json.dumps(header, separators=(",", ":")).encode()),
            _b64url_encode(json.dumps(payload, separators=(",", ":")).encode()),
        ]
    )
    signature = hmac.new(JWT_SECRET_KEY.encode(), signing_input.encode(), hashlib.sha256).digest()
    return f"{signing_input}.{_b64url_encode(signature)}"


def decode_access_token(token: str) -> int:
    try:
        header_part, payload_part, signature_part = token.split(".")
        signing_input = f"{header_part}.{payload_part}"
        expected_signature = hmac.new(
            JWT_SECRET_KEY.encode(), signing_input.encode(), hashlib.sha256
        ).digest()
        if not hmac.compare_digest(_b64url_decode(signature_part), expected_signature):
            raise ValueError("invalid signature")

        payload = json.loads(_b64url_decode(payload_part))
        if int(payload["exp"]) < int(time.time()):
            raise ValueError("expired token")
        return int(payload["sub"])
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="유효하지 않은 인증 토큰입니다.",
        ) from exc
