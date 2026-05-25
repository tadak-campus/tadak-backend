from sqlalchemy.orm import Session

from app.models import ShopItem, ShopItemType, SoundFile, User, UserOwnedItem


# 서버 시작 시 상점에 기본 상품이 없으면 초기 상품 데이터를 넣는다.
def seed_default_shop_items(db: Session) -> None:
    if db.query(ShopItem).first():
        return

    # TODO: 실제 AWS S3 업로드가 붙으면 example URL 대신 S3 asset URL을 저장한다.
    keyboard = ShopItem(
        name="기본 키보드",
        type=ShopItemType.KEYBOARD,
        price=0,
        thumbnail_url="https://example.com/assets/default-keyboard-thumb.png",
        asset_url="https://example.com/assets/default-keyboard.png",
    )
    background = ShopItem(
        name="캠퍼스 배경",
        type=ShopItemType.BACKGROUND,
        price=300,
        thumbnail_url="https://example.com/assets/campus-bg-thumb.png",
        asset_url="https://example.com/assets/campus-bg.png",
    )
    sound = ShopItem(
        name="맑은 타건음",
        type=ShopItemType.SOUND,
        price=200,
        thumbnail_url="https://example.com/assets/clear-sound-thumb.png",
        asset_url=None,
    )
    decoration = ShopItem(
        name="책상 화분",
        type=ShopItemType.DECORATION,
        price=150,
        thumbnail_url="https://example.com/assets/plant-thumb.png",
        asset_url="https://example.com/assets/plant.png",
    )
    db.add_all([keyboard, background, sound, decoration])
    db.flush()
    db.add(SoundFile(item_id=sound.id, name="기본 클릭음", file_url="https://example.com/sounds/click.mp3"))
    db.commit()


# 사용자가 보유한 아이템 id 목록을 set으로 조회한다.
def get_owned_item_ids(db: Session, user_id: int) -> set[int]:
    rows = db.query(UserOwnedItem.item_id).filter(UserOwnedItem.user_id == user_id).all()
    return {row[0] for row in rows}


# 특정 사용자가 특정 아이템을 이미 보유했는지 확인한다.
def owns_item(db: Session, user_id: int, item_id: int) -> bool:
    return (
        db.query(UserOwnedItem)
        .filter(UserOwnedItem.user_id == user_id, UserOwnedItem.item_id == item_id)
        .first()
        is not None
    )


# 아이템 타입에 맞춰 사용자의 장착 아이템 컬럼을 변경한다.
def equip_item_by_type(user: User, item: ShopItem) -> None:
    if item.type == ShopItemType.KEYBOARD:
        user.equipped_keyboard_item_id = item.id
    elif item.type == ShopItemType.BACKGROUND:
        user.equipped_background_item_id = item.id
    elif item.type == ShopItemType.SOUND:
        user.equipped_sound_item_id = item.id
    elif item.type == ShopItemType.DECORATION:
        user.equipped_decoration_item_id = item.id
