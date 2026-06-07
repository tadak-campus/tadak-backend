from sqlalchemy.orm import Session

from app.models import ShopItem, ShopItemType, SoundFile, User, UserOwnedItem


ASSET_BASE_URL = "https://cloud-computer-temp.s3.ap-northeast-2.amazonaws.com/assets"


DEFAULT_SHOP_ITEMS = [
    {
        "name": "키보드 1",
        "type": ShopItemType.KEYBOARD,
        "price": 100,
        "asset_url": None,
    },
    {
        "name": "키보드 2",
        "type": ShopItemType.KEYBOARD,
        "price": 150,
        "asset_url": None,
    },
    {
        "name": "키보드 3",
        "type": ShopItemType.KEYBOARD,
        "price": 200,
        "asset_url": None,
    },
    {
        "name": "키보드 4",
        "type": ShopItemType.KEYBOARD,
        "price": 250,
        "asset_url": None,
    },
    {
        "name": "키보드 5",
        "type": ShopItemType.KEYBOARD,
        "price": 300,
        "asset_url": None,
    },
    {
        "name": "사운드 1",
        "type": ShopItemType.SOUND,
        "price": 100,
        "asset_url": None,
    },
    {
        "name": "사운드 2",
        "type": ShopItemType.SOUND,
        "price": 120,
        "asset_url": None,
    },
    {
        "name": "사운드 3",
        "type": ShopItemType.SOUND,
        "price": 140,
        "asset_url": None,
    },
    {
        "name": "사운드 4",
        "type": ShopItemType.SOUND,
        "price": 160,
        "asset_url": None,
    },
    {
        "name": "사운드 5",
        "type": ShopItemType.SOUND,
        "price": 180,
        "asset_url": None,
    },
    {
        "name": "다크 배경",
        "type": ShopItemType.BACKGROUND,
        "price": 200,
        "asset_url": f"{ASSET_BASE_URL}/background/bg-dark.png",
    },
    {
        "name": "네온 배경",
        "type": ShopItemType.BACKGROUND,
        "price": 300,
        "asset_url": f"{ASSET_BASE_URL}/background/bg-neon.png",
    },
    {
        "name": "파스텔 배경",
        "type": ShopItemType.BACKGROUND,
        "price": 250,
        "asset_url": f"{ASSET_BASE_URL}/background/bg-pastel.png",
    },
    {
        "name": "우드 배경",
        "type": ShopItemType.BACKGROUND,
        "price": 250,
        "asset_url": f"{ASSET_BASE_URL}/background/bg-wood.png",
    },
    {
        "name": "화분 장식",
        "type": ShopItemType.DECORATION,
        "price": 150,
        "asset_url": f"{ASSET_BASE_URL}/decoration/deco-plant.png",
    },
    {
        "name": "별 장식",
        "type": ShopItemType.DECORATION,
        "price": 180,
        "asset_url": f"{ASSET_BASE_URL}/decoration/deco-stars.png",
    },
]


# 서버 시작 시 S3에 올라간 상점 상품이 없으면 추가하고, 있으면 최신 URL로 갱신한다.
def seed_default_shop_items(db: Session) -> None:
    legacy_items = (
        db.query(ShopItem)
        .filter(
            (ShopItem.thumbnail_url.like("https://example.com/%"))
            | (ShopItem.asset_url.like("https://example.com/%"))
        )
        .all()
    )
    for item in legacy_items:
        db.query(User).filter(User.equipped_keyboard_item_id == item.id).update(
            {User.equipped_keyboard_item_id: None}
        )
        db.query(User).filter(User.equipped_background_item_id == item.id).update(
            {User.equipped_background_item_id: None}
        )
        db.query(User).filter(User.equipped_sound_item_id == item.id).update(
            {User.equipped_sound_item_id: None}
        )
        db.query(User).filter(User.equipped_decoration_item_id == item.id).update(
            {User.equipped_decoration_item_id: None}
        )
        db.query(UserOwnedItem).filter(UserOwnedItem.item_id == item.id).delete()
        db.query(SoundFile).filter(SoundFile.item_id == item.id).delete()
        db.delete(item)

    for item_data in DEFAULT_SHOP_ITEMS:
        item = (
            db.query(ShopItem)
            .filter(ShopItem.name == item_data["name"], ShopItem.type == item_data["type"])
            .first()
        )
        if not item:
            item = ShopItem(name=item_data["name"], type=item_data["type"])
            db.add(item)

        item.price = item_data["price"]
        item.thumbnail_url = item_data.get("asset_url")
        item.asset_url = item_data.get("asset_url")

    db.commit()


# 사용자가 보유한 아이템 id 목록을 set으로 조회한다.
def get_owned_item_ids(db: Session, user_id: int) -> set[int]:
    rows = db.query(UserOwnedItem.item_id).filter(UserOwnedItem.user_id == user_id).all()
    return {row[0] for row in rows}


# 사용자가 현재 장착 중인 아이템 id 목록을 set으로 만든다.
def get_equipped_item_ids(user: User) -> set[int]:
    return {
        item_id
        for item_id in [
            user.equipped_keyboard_item_id,
            user.equipped_background_item_id,
            user.equipped_sound_item_id,
            user.equipped_decoration_item_id,
        ]
        if item_id is not None
    }


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
