from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, desc
from ..database import get_db
from ..models import ChatRoom, ChatMessage, Product, User
from ..auth import get_current_user
from pydantic import BaseModel
from datetime import datetime

router = APIRouter(prefix="/api/chat", tags=["chat"])

@router.get("/rooms")
async def list_rooms(user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    result = await db.execute(
        select(ChatRoom).where(
            (ChatRoom.buyer_id == user.id) | (ChatRoom.seller_id == user.id)
        ).order_by(desc(ChatRoom.created_at))
    )
    rooms = result.scalars().all()
    return [
        {
            "id": r.id, "productId": r.product_id,
            "buyerId": r.buyer_id, "sellerId": r.seller_id,
            "productName": r.product.name if r.product else "",
            "otherUser": r.seller.name if r.buyer_id == user.id else r.buyer.name,
            "createdAt": r.created_at.isoformat() if r.created_at else ""
        }
        for r in rooms
    ]

class CreateRoomRequest(BaseModel):
    product_id: int

@router.post("/rooms")
async def create_room(
    req: CreateRoomRequest,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    # 检查是否已存在房间
    result = await db.execute(
        select(ChatRoom).where(
            ChatRoom.product_id == req.product_id,
            ChatRoom.buyer_id == user.id
        )
    )
    existing = result.scalar_one_or_none()
    if existing:
        return {"roomId": existing.id}
    
    # 获取商品卖家
    prod_result = await db.execute(select(Product).where(Product.id == req.product_id))
    product = prod_result.scalar_one_or_none()
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    
    room = ChatRoom(product_id=req.product_id, buyer_id=user.id, seller_id=product.seller_id)
    db.add(room)
    await db.commit()
    await db.refresh(room)
    return {"roomId": room.id}

@router.get("/rooms/{room_id}/messages")
async def get_messages(room_id: int, user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    result = await db.execute(
        select(ChatMessage).where(ChatMessage.room_id == room_id).order_by(ChatMessage.created_at)
    )
    messages = result.scalars().all()
    return [
        {
            "id": m.id, "content": m.content,
            "senderId": m.sender_id,
            "createdAt": m.created_at.isoformat() if m.created_at else "",
            "isMine": m.sender_id == user.id
        }
        for m in messages
    ]

class SendMessageRequest(BaseModel):
    content: str

@router.post("/rooms/{room_id}/messages")
async def send_message(
    room_id: int,
    req: SendMessageRequest,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    msg = ChatMessage(room_id=room_id, sender_id=user.id, content=req.content, created_at=datetime.utcnow())
    db.add(msg)
    await db.commit()
    await db.refresh(msg)
    return {"id": msg.id, "content": msg.content, "senderId": msg.sender_id, "createdAt": msg.created_at.isoformat(), "isMine": True}
