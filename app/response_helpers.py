from app.models import ShopItem, User
from app.schemas import EquippedItemsResponse, ShopItemResponse


def to_shop_item_response(item: ShopItem, owned_item_ids: set[int] | None = None) -> ShopItemResponse:
    owned_item_ids = owned_item_ids or set()
    return ShopItemResponse(
        id=item.id,
        name=item.name,
        type=item.type,
        price=item.price,
        thumbnail_url=item.thumbnail_url,
        asset_url=item.asset_url,
        is_owned=item.id in owned_item_ids,
        sound_files=item.sound_files,
    )


def to_equipped_items_response(user: User) -> EquippedItemsResponse:
    return EquippedItemsResponse(
        keyboard=to_shop_item_response(user.equipped_keyboard_item) if user.equipped_keyboard_item else None,
        background=to_shop_item_response(user.equipped_background_item)
        if user.equipped_background_item
        else None,
        sound=to_shop_item_response(user.equipped_sound_item) if user.equipped_sound_item else None,
        decoration=to_shop_item_response(user.equipped_decoration_item)
        if user.equipped_decoration_item
        else None,
    )
