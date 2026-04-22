from sqlalchemy import Column, Integer, String, Float, Text, DateTime, ForeignKey, Boolean, JSON
from sqlalchemy.orm import relationship
from datetime import datetime
from .database import Base

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    phone = Column(String(20), unique=True, index=True, nullable=True)
    username = Column(String(50), nullable=True)
    avatar = Column(String(255), nullable=True)
    rating = Column(Float, default=5.0)
    password_hash = Column(String(255), nullable=True)
    wechat_openid = Column(String(100), unique=True, nullable=True, index=True)
    created_at = Column(DateTime, default=datetime.utcnow)

class Product(Base):
    __tablename__ = "products"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(200))
    brand = Column(String(50), index=True)
    series = Column(String(100))
    scale = Column(String(10))
    condition = Column(String(20))
    material = Column(String(20))
    price = Column(Integer)
    original_price = Column(Integer)
    description = Column(Text)
    images = Column(JSON)
    seller_id = Column(Integer, ForeignKey("users.id"))
    likes = Column(Integer, default=0)
    views = Column(Integer, default=0)
    is_sold = Column(Boolean, default=False)
    posted_at = Column(DateTime, default=datetime.utcnow)
    seller = relationship("User")

class Collection(Base):
    __tablename__ = "collections"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    name = Column(String(200))
    brand = Column(String(50))
    scale = Column(String(10))
    image = Column(String(255))
    purchase_price = Column(Integer)
    current_value = Column(Integer)
    purchase_date = Column(DateTime)
    location = Column(String(100))
    notes = Column(Text)
    user = relationship("User")

class ChatRoom(Base):
    __tablename__ = "chat_rooms"
    id = Column(Integer, primary_key=True, index=True)
    product_id = Column(Integer, ForeignKey("products.id"))
    buyer_id = Column(Integer, ForeignKey("users.id"))
    seller_id = Column(Integer, ForeignKey("users.id"))
    created_at = Column(DateTime, default=datetime.utcnow)
    product = relationship("Product")
    buyer = relationship("User", foreign_keys=[buyer_id])
    seller = relationship("User", foreign_keys=[seller_id])

class ChatMessage(Base):
    __tablename__ = "chat_messages"
    id = Column(Integer, primary_key=True, index=True)
    room_id = Column(Integer, ForeignKey("chat_rooms.id"))
    sender_id = Column(Integer, ForeignKey("users.id"))
    content = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)
    sender = relationship("User")

class PriceHistory(Base):
    __tablename__ = "price_history"
    id = Column(Integer, primary_key=True, index=True)
    brand = Column(String(50), index=True)
    series = Column(String(100))
    model_name = Column(String(200))
    avg_price = Column(Integer)
    recorded_at = Column(DateTime, default=datetime.utcnow)
