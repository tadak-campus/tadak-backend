from fastapi import FastAPI

from app.database import Base, SessionLocal, engine
from app.routers import auth, practice, shop, users
from app.services.shop_service import seed_default_shop_items
from dotenv import load_dotenv
from fastapi.middleware.cors import CORSMiddleware


load_dotenv()


def create_app() -> FastAPI:
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    try:
        seed_default_shop_items(db)
    finally:
        db.close()

    app = FastAPI(title="타닥캠퍼스 API", version="0.1.0")
    app.include_router(auth.router)
    app.include_router(users.router)
    app.include_router(practice.router)
    app.include_router(shop.router)

    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_methods=["*"],
        allow_headers=["*"],
    )
    return app


app = create_app()
