from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, desc
from sqlalchemy.orm import selectinload
from ..database import get_db
from ..models import Product, User
from ..auth import get_current_user
from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime

router = APIRouter(prefix="/api/products", tags=["products"])

class ProductCreate(BaseModel):
    name: str
    brand: str
    series: str
    scale: str
    condition: str
    material: str
    price: int
    original_price: int
    description: str
    images: List[str]

@router.get("")
async def list_products(
    brand: Optional[str] = None,
    scale: Optional[str] = None,
    condition: Optional[str] = None,
    material: Optional[str] = None,
    min_price: Optional[int] = None,
    max_price: Optional[int] = None,
    sort: Optional[str] = "latest",
    db: AsyncSession = Depends(get_db)
):
    query = select(Product).options(selectinload(Product.seller)).where(Product.is_sold == False)
    if brand: query = query.where(Product.brand == brand)
    if scale: query = query.where(Product.scale == scale)
    if condition: query = query.where(Product.condition == condition)
    if material: query = query.where(Product.material == material)
    if min_price: query = query.where(Product.price >= min_price)
    if max_price: query = query.where(Product.price <= max_price)
    if sort == "price-low": query = query.order_by(Product.price.asc())
    elif sort == "price-high": query = query.order_by(Product.price.desc())
    elif sort == "popular": query = query.order_by(Product.likes.desc())
    else: query = query.order_by(desc(Product.posted_at))
    
    result = await db.execute(query)
    products = result.scalars().all()
    return [
        {
            "id": p.id, "name": p.name, "brand": p.brand, "series": p.series,
            "scale": p.scale, "condition": p.condition, "material": p.material,
            "price": p.price, "originalPrice": p.original_price,
            "description": p.description, "images": p.images,
            "likes": p.likes, "views": p.views, "postedAt": p.posted_at.isoformat() if p.posted_at else "",
            "seller": {"id": p.seller.id, "name": p.seller.name, "rating": p.seller.rating} if p.seller else None
        }
        for p in products
    ]

@router.get("/{product_id}")
async def get_product(product_id: int, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Product).where(Product.id == product_id))
    p = result.scalar_one_or_none()
    if not p: raise HTTPException(status_code=404, detail="Not found")
    # 每次查看+1浏览
    p.views = (p.views or 0) + 1
    await db.commit()
    return {
        "id": p.id, "name": p.name, "brand": p.brand, "series": p.series,
        "scale": p.scale, "condition": p.condition, "material": p.material,
        "price": p.price, "originalPrice": p.original_price,
        "description": p.description, "images": p.images,
        "likes": p.likes, "views": p.views, "postedAt": p.posted_at.isoformat() if p.posted_at else "",
        "seller": {"id": p.seller.id, "name": p.seller.name, "rating": p.seller.rating} if p.seller else None
    }

@router.post("")
async def create_product(
    req: ProductCreate,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    product = Product(**req.model_dump(), seller_id=user.id, posted_at=datetime.utcnow())
    db.add(product)
    await db.commit()
    await db.refresh(product)
    return {"id": product.id, "success": True}

@router.post("/{product_id}/like")
async def like_product(product_id: int, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Product).where(Product.id == product_id))
    p = result.scalar_one_or_none()
    if not p: raise HTTPException(status_code=404, detail="Not found")
    p.likes = (p.likes or 0) + 1
    await db.commit()
    return {"likes": p.likes}
