from sqlalchemy.orm import Session

from app.models import ShopItem, ShopItemType, SoundFile, User, UserOwnedItem


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


def get_owned_item_ids(db: Session, user_id: int) -> set[int]:
    rows = db.query(UserOwnedItem.item_id).filter(UserOwnedItem.user_id == user_id).all()
    return {row[0] for row in rows}


def owns_item(db: Session, user_id: int, item_id: int) -> bool:
    return (
        db.query(UserOwnedItem)
        .filter(UserOwnedItem.user_id == user_id, UserOwnedItem.item_id == item_id)
        .first()
        is not None
    )


def equip_item_by_type(user: User, item: ShopItem) -> None:
    if item.type == ShopItemType.KEYBOARD:
        user.equipped_keyboard_item_id = item.id
    elif item.type == ShopItemType.BACKGROUND:
        user.equipped_background_item_id = item.id
    elif item.type == ShopItemType.SOUND:
        user.equipped_sound_item_id = item.id
    elif item.type == ShopItemType.DECORATION:
        user.equipped_decoration_item_id = item.id
