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
    # 星仔扩展字段
    brand_id = Column(Integer, ForeignKey("brands.id"))
    series_id = Column(Integer)
    model_code = Column(String(50))
    make = Column(String(50))
    model = Column(String(50))
    category = Column(String(50))
    tags = Column(String(200))
    ip_series = Column(String(50))
    collaboration = Column(String(100))
    is_limited = Column(Integer, default=0)
    limited_count = Column(Integer)
    rarity = Column(String(20))
    collector_value = Column(Float)
    msrp = Column(Float)
    market_price_low = Column(Float)
    market_price_high = Column(Float)
    price_trend = Column(String(20))
    features = Column(Text)
    video_url = Column(String(255))
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

class Brand(Base):
    __tablename__ = "brands"
    id = Column(Integer, primary_key=True, index=True)
    name_zh = Column(String(100))
    name_en = Column(String(100))
    name_jp = Column(String(100))
    logo_url = Column(String(255))
    country = Column(String(50))
    parent_company = Column(String(100))
    tier = Column(String(10))
    description = Column(Text)
    founded_year = Column(Integer)
    official_site = Column(String(255))
    is_active = Column(Integer, default=1)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow)

class Series(Base):
    __tablename__ = "series"
    id = Column(Integer, primary_key=True, index=True)
    brand_id = Column(Integer, ForeignKey("brands.id"))
    name = Column(String(100))
    name_zh = Column(String(100))
    description = Column(Text)
    price_range_low = Column(Float)
    price_range_high = Column(Float)
    scale = Column(String(10))
    is_limited = Column(Integer, default=0)
    release_year = Column(Integer)
    total_models = Column(Integer)
    image_url = Column(String(255))
    is_active = Column(Integer, default=1)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow)
