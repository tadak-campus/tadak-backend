from fastapi import APIRouter, Depends

from app.dependencies import get_current_user
from app.models import User
from app.response_helpers import to_equipped_items_response
from app.schemas import UserMeResponse


router = APIRouter(prefix="/api/users", tags=["users"])


@router.get("/me", response_model=UserMeResponse)
def get_me(current_user: User = Depends(get_current_user)):
    return UserMeResponse(
        id=current_user.id,
        kakao_id=current_user.kakao_id,
        profile_nickname=current_user.profile_nickname,
        point=current_user.point,
        equipped_items=to_equipped_items_response(current_user),
    )
