from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.dependencies import get_current_user
from app.models import ShopItem, User, UserOwnedItem
from app.response_helpers import to_equipped_items_response, to_shop_item_response
from app.schemas import BuyItemResponse, EquipItemResponse, ShopItemResponse
from app.services.shop_service import equip_item_by_type, get_owned_item_ids, owns_item


router = APIRouter(prefix="/api/shop", tags=["shop"])


# 상점에 등록된 전체 아이템 목록과 현재 사용자의 보유 여부를 반환한다.
@router.get("/items", response_model=list[ShopItemResponse])
def get_shop_items(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    owned_item_ids = get_owned_item_ids(db, current_user.id)
    items = db.query(ShopItem).order_by(ShopItem.id).all()
    return [to_shop_item_response(item, owned_item_ids) for item in items]


# 현재 사용자가 구매하거나 지급받아 보유 중인 아이템 목록을 반환한다.
@router.get("/my-items", response_model=list[ShopItemResponse])
def get_my_items(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    owned_item_ids = get_owned_item_ids(db, current_user.id)
    items = (
        db.query(ShopItem)
        .join(UserOwnedItem, UserOwnedItem.item_id == ShopItem.id)
        .filter(UserOwnedItem.user_id == current_user.id)
        .order_by(ShopItem.id)
        .all()
    )
    return [to_shop_item_response(item, owned_item_ids) for item in items]


# 포인트를 차감하고 선택한 상점 아이템을 사용자 보유 목록에 추가한다.
@router.post("/items/{item_id}/buy", response_model=BuyItemResponse)
def buy_item(
    item_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    item = db.query(ShopItem).filter(ShopItem.id == item_id).first()
    if not item:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="아이템을 찾을 수 없습니다.")
    if owns_item(db, current_user.id, item.id):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="이미 보유한 아이템입니다.")
    if current_user.point < item.price:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="포인트가 부족합니다.")

    current_user.point -= item.price
    db.add(UserOwnedItem(user_id=current_user.id, item_id=item.id))
    db.commit()
    db.refresh(current_user)
    db.refresh(item)
    return BuyItemResponse(
        message="구매가 완료되었습니다.",
        point=current_user.point,
        item=to_shop_item_response(item, {item.id}),
    )


# 사용자가 보유한 아이템을 타입에 맞는 장착 슬롯에 설정한다.
@router.post("/items/{item_id}/equip", response_model=EquipItemResponse)
def equip_item(
    item_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    item = db.query(ShopItem).filter(ShopItem.id == item_id).first()
    if not item:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="아이템을 찾을 수 없습니다.")
    if not owns_item(db, current_user.id, item.id):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="보유한 아이템만 장착할 수 있습니다.")

    equip_item_by_type(current_user, item)
    db.commit()
    db.refresh(current_user)
    return EquipItemResponse(
        message="장착이 완료되었습니다.",
        equipped_items=to_equipped_items_response(current_user),
    )
