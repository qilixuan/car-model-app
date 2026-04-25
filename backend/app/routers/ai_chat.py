from fastapi import APIRouter, Depends
from sqlalchemy import select, or_
from ..database import get_db
from ..models import Product, Brand, Series
import re

router = APIRouter(prefix="/api/chat", tags=["ai_chat"])

def extract_keywords(text: str) -> list:
    """提取中文/英文关键词"""
    keywords = re.findall(r'[\u4e00-\u9fff]+|[a-zA-Z0-9]+', text.lower())
    return [k for k in keywords if len(k) > 1]

def build_response(question: str, products: list, brands: list) -> str:
    """构建星仔风格的回复"""
    if not products and not brands:
        return "宝～这个问题我正在学习中，让我结合你的情况给你一个合适的建议呀～"

    parts = []
    
    if products:
        parts.append(f"找到 {len(products)} 款相关车模哒！")
        for p in products[:5]:
            name = p.get('name', '')
            brand = p.get('brand', '')
            price = p.get('price', 0)
            rarity = p.get('rarity', '')
            trend = p.get('price_trend', '')
            low = p.get('market_price_low', 0) or price
            high = p.get('market_price_high', 0) or price
            
            info = f"【{brand} {name}】"
            if rarity:
                info += f" {rarity}级"
            if price:
                info += f" 官价¥{price}"
            if low and high:
                info += f" 市场价¥{int(low)}-{int(high)}"
            if trend and trend != '未知':
                info += f" 📈{trend}"
            parts.append(info)
    
    if brands:
        for b in brands[:3]:
            name = b.get('name', '')
            country = b.get('country', '')
            desc = b.get('description', '')
            if desc and len(desc) > 60:
                desc = desc[:60] + '...'
            info = f"【{name}】{country}品牌 | {desc}"
            parts.append(info)
    
    return '；'.join(parts) + '。还有什么想知道的哒？'

@router.get("/ai")
async def ai_chat(q: str = "", db=Depends(get_db)):
    """
    星仔 AI 问答接口
    
    根据用户问题搜索车模数据库，返回相关产品/品牌信息
    
    示例：
    GET /api/chat/ai?q=丰田AE86
    GET /api/chat/ai?q=Hot Wheels限量
    GET /api/chat/ai?q=日产GTR价格
    """
    try:
        if not q or len(q.strip()) < 2:
            return {"reply": "宝～你想问什么呀？告诉我车型、品牌或系列，我来帮你找找哒！"}
        
        keywords = extract_keywords(q)
        if not keywords:
            return {"reply": "宝～我没听懂你说的什么呢，能换个方式问吗？"}
        
        # 搜索品牌
        brand_results = []
        brand_query = select(Brand)
        # 同时搜索中英文名
        name_conditions = []
        for k in keywords:
            k_pattern = f"%{k}%"
            name_conditions.append(Brand.name_zh.ilike(k_pattern))
            name_conditions.append(Brand.name_en.ilike(k_pattern))
        brand_query = brand_query.where(or_(*name_conditions))
        result = await db.execute(brand_query)
        for b in result.scalars().all():
            brand_results.append({
                "name": b.name_zh or b.name_en,
                "country": getattr(b, 'country', ''),
                "description": getattr(b, 'description', '')[:100] if getattr(b, 'description', '') else ''
            })
        
        # 搜索产品
        product_results = []
        
        # 多条件匹配：品牌/系列/车型/编号
        conditions = []
        for k in keywords:
            k_pattern = f"%{k}%"
            conditions.append(Product.name.ilike(k_pattern))
            conditions.append(Product.brand.ilike(k_pattern))
            conditions.append(Product.series.ilike(k_pattern))
            conditions.append(Product.make.ilike(k_pattern))
            conditions.append(Product.model.ilike(k_pattern))
            conditions.append(Product.model_code.ilike(k_pattern))
            conditions.append(Product.category.ilike(k_pattern))
        
        product_query = (
            select(Product)
            .where(or_(*conditions))
            .where(Product.is_sold == 0)
            .limit(8)
        )
        result = await db.execute(product_query)
        for p in result.scalars().all():
            product_results.append({
                "name": p.name,
                "brand": p.brand,
                "series": p.series,
                "price": p.price,
                "rarity": p.rarity,
                "price_trend": getattr(p, 'price_trend', '未知'),
                "market_price_low": getattr(p, 'market_price_low', None),
                "market_price_high": getattr(p, 'market_price_high', None),
                "collector_value": getattr(p, 'collector_value', None)
            })
        
        reply = build_response(q, product_results, brand_results)
        return {"reply": reply}
    except Exception as e:
        import traceback
        traceback.print_exc()
        return {"reply": f"宝～出错了: {str(e)}"}
