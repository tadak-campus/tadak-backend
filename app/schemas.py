from pydantic import BaseModel, Field

from app.models import ShopItemType


class KakaoLoginRequest(BaseModel):
    kakao_access_token: str


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"


class SoundFileResponse(BaseModel):
    id: int
    name: str
    file_url: str

    model_config = {"from_attributes": True}


class ShopItemResponse(BaseModel):
    id: int
    name: str
    type: ShopItemType
    price: int
    thumbnail_url: str | None
    asset_url: str | None
    is_owned: bool = False
    sound_files: list[SoundFileResponse] = []

    model_config = {"from_attributes": True}


class EquippedItemsResponse(BaseModel):
    keyboard: ShopItemResponse | None = None
    background: ShopItemResponse | None = None
    sound: ShopItemResponse | None = None
    decoration: ShopItemResponse | None = None


class UserMeResponse(BaseModel):
    id: int
    kakao_id: str
    profile_nickname: str
    point: int
    equipped_items: EquippedItemsResponse


class PracticeGenerateResponse(BaseModel):
    sentences: list[str]


class PracticeCompleteRequest(BaseModel):
    completed_count: int = Field(ge=0)
    accuracy: float = Field(ge=0, le=100)
    speed: float = Field(ge=0)


class PracticeCompleteResponse(BaseModel):
    earned_point: int
    total_point: int


class BuyItemResponse(BaseModel):
    message: str
    point: int
    item: ShopItemResponse


class EquipItemResponse(BaseModel):
    message: str
    equipped_items: EquippedItemsResponse
