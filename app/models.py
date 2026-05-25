import enum

from sqlalchemy import Column, Enum, ForeignKey, Integer, String, UniqueConstraint
from sqlalchemy.orm import relationship

from app.database import Base


class ShopItemType(str, enum.Enum):
    KEYBOARD = "KEYBOARD"
    BACKGROUND = "BACKGROUND"
    SOUND = "SOUND"
    DECORATION = "DECORATION"


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    kakao_id = Column(String, unique=True, index=True, nullable=False)
    profile_nickname = Column(String, nullable=False)
    point = Column(Integer, nullable=False, default=0)
    equipped_keyboard_item_id = Column(Integer, ForeignKey("shop_items.id"), nullable=True)
    equipped_background_item_id = Column(Integer, ForeignKey("shop_items.id"), nullable=True)
    equipped_sound_item_id = Column(Integer, ForeignKey("shop_items.id"), nullable=True)
    equipped_decoration_item_id = Column(Integer, ForeignKey("shop_items.id"), nullable=True)

    equipped_keyboard_item = relationship("ShopItem", foreign_keys=[equipped_keyboard_item_id])
    equipped_background_item = relationship("ShopItem", foreign_keys=[equipped_background_item_id])
    equipped_sound_item = relationship("ShopItem", foreign_keys=[equipped_sound_item_id])
    equipped_decoration_item = relationship("ShopItem", foreign_keys=[equipped_decoration_item_id])
    owned_items = relationship("UserOwnedItem", back_populates="user")


class ShopItem(Base):
    __tablename__ = "shop_items"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    type = Column(Enum(ShopItemType), nullable=False)
    price = Column(Integer, nullable=False, default=0)
    thumbnail_url = Column(String, nullable=True)
    asset_url = Column(String, nullable=True)

    sound_files = relationship("SoundFile", back_populates="item")
    owned_by = relationship("UserOwnedItem", back_populates="item")


class UserOwnedItem(Base):
    __tablename__ = "user_owned_items"
    __table_args__ = (UniqueConstraint("user_id", "item_id", name="uq_user_owned_item"),)

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    item_id = Column(Integer, ForeignKey("shop_items.id"), nullable=False)

    user = relationship("User", back_populates="owned_items")
    item = relationship("ShopItem", back_populates="owned_by")


class SoundFile(Base):
    __tablename__ = "sound_files"

    id = Column(Integer, primary_key=True, index=True)
    item_id = Column(Integer, ForeignKey("shop_items.id"), nullable=False)
    name = Column(String, nullable=False)
    file_url = Column(String, nullable=False)

    item = relationship("ShopItem", back_populates="sound_files")
