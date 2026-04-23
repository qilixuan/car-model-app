from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from ..database import get_db
from ..models import Collection, User
from ..auth import get_current_user
from pydantic import BaseModel
from datetime import datetime

router = APIRouter(prefix="/api/collections", tags=["collections"])

@router.get("")
async def list_collections(user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Collection).where(Collection.user_id == user.id))
    items = result.scalars().all()
    return [
        {
            "id": c.id, "name": c.name, "brand": c.brand, "scale": c.scale,
            "image": c.image, "purchasePrice": c.purchase_price,
            "currentValue": c.current_value, "purchaseDate": c.purchase_date.isoformat() if c.purchase_date else "",
            "location": c.location, "notes": c.notes
        }
        for c in items
    ]

class CollectionCreate(BaseModel):
    name: str
    brand: str
    scale: str
    image: str
    purchase_price: int
    current_value: int
    purchase_date: str
    location: str = ""
    notes: str = ""

@router.post("")
async def create_collection(
    req: CollectionCreate,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    item = Collection(
        user_id=user.id,
        name=req.name, brand=req.brand, scale=req.scale,
        image=req.image, purchase_price=req.purchase_price,
        current_value=req.current_value,
        purchase_date=datetime.fromisoformat(req.purchase_date),
        location=req.location, notes=req.notes
    )
    db.add(item)
    await db.commit()
    await db.refresh(item)
    return {"id": item.id, "success": True}

@router.delete("/{id}")
async def delete_collection(id: int, user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Collection).where(Collection.id == id, Collection.user_id == user.id))
    item = result.scalar_one_or_none()
    if not item: return {"success": False}
    await db.delete(item)
    await db.commit()
    return {"success": True}
