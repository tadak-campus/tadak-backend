import os

os.environ["DATABASE_URL"] = "sqlite:///./test_tadak.db"

from fastapi.testclient import TestClient

from app.database import Base, engine
from app.main import app


client = TestClient(app)


def setup_function():
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    from app.database import SessionLocal
    from app.services.shop_service import seed_default_shop_items

    db = SessionLocal()
    try:
        seed_default_shop_items(db)
    finally:
        db.close()


def login() -> str:
    response = client.post(
        "/api/auth/kakao/login",
        json={"kakao_id": "kakao-1", "profile_nickname": "타닥이"},
    )
    assert response.status_code == 200
    data = response.json()
    assert data["access_token"]
    return data["access_token"]


def auth_headers(token: str) -> dict[str, str]:
    return {"Authorization": f"Bearer {token}"}


def test_login_me_shop_buy_equip_and_practice_complete():
    token = login()

    me_response = client.get("/api/users/me", headers=auth_headers(token))
    assert me_response.status_code == 200
    assert me_response.json()["profile_nickname"] == "타닥이"
    starting_point = me_response.json()["point"]

    items_response = client.get("/api/shop/items", headers=auth_headers(token))
    assert items_response.status_code == 200
    items = items_response.json()
    assert len(items) >= 4
    buy_target = next(item for item in items if item["price"] > 0)

    buy_response = client.post(
        f"/api/shop/items/{buy_target['id']}/buy",
        headers=auth_headers(token),
    )
    assert buy_response.status_code == 200
    assert buy_response.json()["point"] == starting_point - buy_target["price"]

    my_items_response = client.get("/api/shop/my-items", headers=auth_headers(token))
    assert my_items_response.status_code == 200
    assert any(item["id"] == buy_target["id"] for item in my_items_response.json())

    equip_response = client.post(
        f"/api/shop/items/{buy_target['id']}/equip",
        headers=auth_headers(token),
    )
    assert equip_response.status_code == 200
    equipped = equip_response.json()["equipped_items"]
    equipped_ids = [value["id"] for value in equipped.values() if value is not None]
    assert buy_target["id"] in equipped_ids

    practice_response = client.post(
        "/api/practice/complete",
        headers=auth_headers(token),
        json={"completed_count": 3, "accuracy": 90, "speed": 250},
    )
    assert practice_response.status_code == 200
    assert practice_response.json()["earned_point"] > 0
    assert practice_response.json()["total_point"] > buy_response.json()["point"]
