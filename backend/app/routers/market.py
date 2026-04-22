from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, desc
from ..database import get_db
from ..models import PriceHistory
from pydantic import BaseModel
from datetime import datetime, timedelta
import random

router = APIRouter(prefix="/api/market", tags=["market"])

@router.get("/trending")
async def get_trending(db: AsyncSession = Depends(get_db)):
    # 返回热门品牌的价格趋势
    brands = ["AutoWorld", "ISO", "Tommy教父", "LCD", "合金变奏", "UTO"]
    trending = []
    for brand in brands:
        result = await db.execute(
            select(PriceHistory).where(PriceHistory.brand == brand).order_by(desc(PriceHistory.recorded_at)).limit(30)
        )
        history = result.scalars().all()
        if history:
            latest = history[0]
            prev = history[-1] if len(history) > 1 else latest
            change = ((latest.avg_price - prev.avg_price) / prev.avg_price * 100) if prev.avg_price else 0
            trending.append({
                "brand": brand,
                "avgPrice": latest.avg_price,
                "change": round(change, 1),
                "history": [{"date": h.recorded_at.isoformat()[:10], "price": h.avg_price} for h in history]
            })
        else:
            # 生成模拟数据
            base = random.randint(500, 2000)
            trending.append({
                "brand": brand,
                "avgPrice": base,
                "change": round(random.uniform(-5, 10), 1),
                "history": [
                    {"date": (datetime.now() - timedelta(days=30-i)).isoformat()[:10], "price": base + random.randint(-100, 200)}
                    for i in range(12)
                ]
            })
    return trending

@router.get("/price/{brand}")
async def get_brand_price(brand: str, db: AsyncSession = Depends(get_db)):
    result = await db.execute(
        select(PriceHistory).where(PriceHistory.brand == brand).order_by(desc(PriceHistory.recorded_at)).limit(30)
    )
    history = result.scalars().all()
    if not history:
        base = random.randint(500, 2000)
        return {
            "brand": brand,
            "history": [
                {"date": (datetime.now() - timedelta(days=30-i)).isoformat()[:10], "price": base + random.randint(-100, 200)}
                for i in range(12)
            ]
        }
    return {
        "brand": brand,
        "history": [{"date": h.recorded_at.isoformat()[:10], "price": h.avg_price} for h in reversed(history)]
    }
