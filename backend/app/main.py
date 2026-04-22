from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from .database import init_db

@asynccontextmanager
async def lifespan(app: FastAPI):
    await init_db()
    await seed_data()
    yield

app = FastAPI(title="车模星球 API", version="0.0.1", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

from .routers import auth, products, collections, chat, market, wechat
app.include_router(auth.router)
app.include_router(products.router)
app.include_router(collections.router)
app.include_router(chat.router)
app.include_router(market.router)
app.include_router(wechat.router)

@app.get("/api/health")
async def health():
    return {"status": "ok", "app": "car-model-planet"}

async def seed_data():
    from sqlalchemy.ext.asyncio import AsyncSession
    from sqlalchemy import select
    from .database import async_session
    from .models import User, Product, PriceHistory
    from datetime import datetime
    import random

    async with async_session() as db:
        result = await db.execute(select(User).limit(1))
        if result.scalar_one_or_none():
            return

        users = [
            User(phone="13900000001", username="藏家小王", rating=4.8),
            User(phone="13900000002", username="车模老炮", rating=4.9),
            User(phone="13900000003", username="速度机器", rating=5.0),
            User(phone="13900000004", username="跃马收藏", rating=4.7),
        ]
        for u in users:
            db.add(u)
        await db.commit()

        products_data = [
            {"name": "AutoWorld 兰博基尼 Countach LPI 800-4", "brand": "AutoWorld", "series": "Countach", "scale": "1:18", "condition": "几乎全新", "material": "合金", "price": 1280, "original_price": 1580, "description": "2021年购入，仅摆放展示过一次，包装配件齐全。", "images": ["https://images.unsplash.com/photo-1544636331-e26879cd4d9b?w=400&h=400&fit=crop"], "likes": 234, "views": 1892, "seller_id": 2},
            {"name": "ISO  保时捷 911 GT3 RS", "brand": "ISO", "series": "911 GT3 RS", "scale": "1:18", "condition": "全新", "material": "树脂", "price": 2180, "original_price": 2180, "description": "现货全新未拆封，顺丰包邮。", "images": ["https://images.unsplash.com/photo-1503376780353-7e6692767b70?w=400&h=400&fit=crop"], "likes": 456, "views": 3201, "seller_id": 3},
            {"name": "合金变奏 保时捷 718 Cayman GT4", "brand": "合金变奏", "series": "718 Cayman", "scale": "1:18", "condition": "轻微瑕疵", "material": "合金", "price": 680, "original_price": 880, "description": "右后视镜有轻微松动，不影响整体美观。", "images": ["https://images.unsplash.com/photo-1558618666-fcd25c85cd64?w=400&h=400&fit=crop"], "likes": 89, "views": 567, "seller_id": 4},
            {"name": "Make A 奔驰 AMG GT3", "brand": "Make A", "series": "AMG GT", "scale": "1:43", "condition": "几乎全新", "material": "合金", "price": 420, "original_price": 520, "description": "赛车文化收藏，品相完美。", "images": ["https://images.unsplash.com/photo-1618843479313-40f8afb4b4d8?w=400&h=400&fit=crop"], "likes": 167, "views": 1102, "seller_id": 2},
            {"name": "Tommy教父 法拉利 F40", "brand": "Tommy教父", "series": "F40", "scale": "1:18", "condition": "全新", "material": "合金", "price": 1580, "original_price": 1580, "description": "法拉利官方授权，限量编号018。", "images": ["https://images.unsplash.com/photo-1592198084033-aade902d1aae?w=400&h=400&fit=crop"], "likes": 312, "views": 2567, "seller_id": 4},
            {"name": "LCD 迈凯伦 P1", "brand": "LCD", "series": "P1", "scale": "1:18", "condition": "全新", "material": "树脂", "price": 1880, "original_price": 1880, "description": "P1旗舰车型，细节还原极致。", "images": ["https://images.unsplash.com/photo-1544636331-e26879cd4d9b?w=400&h=400&fit=crop"], "likes": 278, "views": 2100, "seller_id": 3},
            {"name": "MiniGT 丰田 GR Supra", "brand": "MiniGT", "series": "GR Supra", "scale": "1:64", "condition": "几乎全新", "material": "合金", "price": 88, "original_price": 108, "description": "JDM经典车型，64比例精品。", "images": ["https://images.unsplash.com/photo-1626668893632-6f3a4466d22f?w=400&h=400&fit=crop"], "likes": 56, "views": 432, "seller_id": 2},
            {"name": "UTO 兰博基尼 Sián FKP 37", "brand": "UTO", "series": "Sián", "scale": "1:18", "condition": "全新", "material": "树脂", "price": 2680, "original_price": 2680, "description": "限量63台中的第21台，证书齐全。", "images": ["https://images.unsplash.com/photo-1544829099-b9a0c07fad1a?w=400&h=400&fit=crop"], "likes": 189, "views": 1567, "seller_id": 3},
        ]

        for pdata in products_data:
            pdata["posted_at"] = datetime.utcnow()
            p = Product(**pdata)
            db.add(p)

        from datetime import timedelta
        brands = ["AutoWorld", "ISO", "Tommy教父", "LCD", "合金变奏", "UTO"]
        for brand in brands:
            base_price = random.randint(800, 2000)
            for i in range(30):
                h = PriceHistory(
                    brand=brand, series="", model_name=brand,
                    avg_price=base_price + random.randint(-200, 300),
                    recorded_at=datetime.utcnow() - timedelta(days=29-i)
                )
                db.add(h)

        await db.commit()
        print("Seed data inserted!")
