from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database import get_db
from app.schemas import KakaoLoginRequest, TokenResponse
from app.services.auth_service import create_access_token, get_or_create_user, verify_kakao_login_mock


router = APIRouter(prefix="/api/auth", tags=["auth"])


@router.post("/kakao/login", response_model=TokenResponse)
def kakao_login(request: KakaoLoginRequest, db: Session = Depends(get_db)):
    kakao_profile = verify_kakao_login_mock(request.kakao_id, request.profile_nickname)
    user = get_or_create_user(
        db,
        kakao_id=kakao_profile["kakao_id"],
        profile_nickname=kakao_profile["profile_nickname"],
    )
    return TokenResponse(access_token=create_access_token(user.id))
