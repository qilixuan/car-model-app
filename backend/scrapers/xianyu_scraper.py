"""
闲鱼 1:64 车模数据爬虫
Xianyu 1:64 Car Model Scraper

使用方法:
    python xianyu_scraper.py [--max-pages N] [--output FILE]
"""

import asyncio
import json
import math
import re
import sqlite3
import argparse
import time
from dataclasses import dataclass, asdict
from pathlib import Path
from typing import Optional

import httpx
from bs4 import BeautifulSoup

# ========== 配置 ==========
BASE_URL = "https://www.xianyu.cn"
SEARCH_URL = "https://www.xianyu.cn/search"
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
    "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8",
    "Accept-Encoding": "gzip, deflate, br",
    "DNT": "1",
    "Connection": "keep-alive",
    "Upgrade-Insecure-Requests": "1",
}
TIMEOUT = 30.0
DELAY = 2.0  # 请求间隔(秒)，避免被封

# ========== 数据模型 ==========
@dataclass
class CarModelItem:
    """车模数据结构"""
    item_id: str           # 商品ID
    title: str             # 标题
    price: float           # 价格
    original_price: Optional[float]  # 原价
    seller: str            # 卖家昵称
    seller_level: Optional[str]  # 卖家等级
    location: str          # 所在地
    images: list[str]      # 图片URL列表
    description: str      # 描述
    scale: str             # 比例 (1:64)
    brand: str             # 品牌
    condition: str        # 新旧程度
    category: str          # 分类
    view_count: int        # 浏览量
    like_count: int        # 想要数
    comment_count: int     # 评论数
    posted_time: str       # 发布时间
    url: str               # 商品链接
    scraped_at: str        # 爬取时间

# ========== 数据库操作 ==========
def init_db(db_path: str = "car_model.db"):
    """初始化SQLite数据库"""
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS car_models (
            item_id TEXT PRIMARY KEY,
            title TEXT NOT NULL,
            price REAL,
            original_price REAL,
            seller TEXT,
            seller_level TEXT,
            location TEXT,
            images TEXT,
            description TEXT,
            scale TEXT,
            brand TEXT,
            condition TEXT,
            category TEXT,
            view_count INTEGER,
            like_count INTEGER,
            comment_count INTEGER,
            posted_time TEXT,
            url TEXT,
            scraped_at TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    conn.commit()
    return conn

def save_to_db(conn: sqlite3.Connection, items: list[CarModelItem]):
    """保存到数据库"""
    cursor = conn.cursor()
    for item in items:
        cursor.execute("""
            INSERT OR REPLACE INTO car_models VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            item.item_id,
            item.title,
            item.price,
            item.original_price,
            item.seller,
            item.seller_level,
            item.location,
            json.dumps(item.images, ensure_ascii=False),
            item.description,
            item.scale,
            item.brand,
            item.condition,
            item.category,
            item.view_count,
            item.like_count,
            item.comment_count,
            item.posted_time,
            item.url,
            item.scraped_at,
        ))
    conn.commit()

# ========== 爬虫核心 ==========
class XianyuScraper:
    """闲鱼车模爬虫"""
    
    def __init__(self, db_path: str = "car_model.db"):
        self.db_path = db_path
        self.conn = None
        self.stats = {"success": 0, "failed": 0, "total": 0}
    
    async def fetch_page(self, client: httpx.AsyncClient, url: str) -> Optional[str]:
        """获取页面HTML"""
        try:
            response = await client.get(url, headers=HEADERS, timeout=TIMEOUT)
            response.raise_for_status()
            return response.text
        except Exception as e:
            print(f"请求失败 [{url}]: {e}")
            return None
    
    def parse_search_page(self, html: str) -> tuple[list[dict], int]:
        """解析搜索结果页面，返回(商品列表, 总页数)"""
        soup = BeautifulSoup(html, "html.parser")
        items = []
        total_pages = 1
        
        # 尝试从页面提取商品数据
        # 闲鱼页面结构可能变化，这里先尝试多种选择器
        item_selector = ".item, .goods-item, [data-itemid], .search-result-item"
        
        for elem in soup.select(item_selector):
            try:
                item = self._extract_item_data(elem)
                if item:
                    items.append(item)
            except Exception:
                continue
        
        # 尝试从script标签提取JSON数据（闲鱼常用这种方式）
        script_data = self._extract_json_from_script(soup)
        if script_data:
            items.extend(script_data)
        
        # 提取总页数
        page_elem = soup.select_one(".pagination, .page-wrap, [class*='page']")
        if page_elem:
            page_text = page_elem.get_text()
            pages = re.findall(r"(\d+)", page_text)
            if pages:
                total_pages = max([int(p) for p in pages])
        
        return items, total_pages
    
    def _extract_json_from_script(self, soup: BeautifulSoup) -> list[dict]:
        """从script标签提取JSON数据"""
        items = []
        scripts = soup.find_all("script")
        for script in scripts:
            text = script.string or ""
            # 查找包含商品数据的JSON
            if "itemId" in text or "goodsId" in text:
                # 尝试提取JSON对象
                patterns = [
                    r'\{[^{}]*"itemId"[^{}]*\}',
                    r'\{[^{}]*"goodsId"[^{}]*\}',
                ]
                for pattern in patterns:
                    matches = re.findall(pattern, text)
                    for match in matches:
                        try:
                            data = json.loads(match)
                            if isinstance(data, dict):
                                items.append(data)
                        except:
                            continue
        return items
    
    def _extract_item_data(self, elem) -> Optional[dict]:
        """从页面元素提取商品数据"""
        item = {}
        
        # 商品ID
        item_id = elem.get("data-itemid") or elem.get("data-goods-id") or ""
        if not item_id:
            link = elem.select_one("a")
            if link:
                href = link.get("href", "")
                item_id = re.search(r"/(\d+)", href)
                item_id = item_id.group(1) if item_id else ""
        item["item_id"] = item_id
        
        # 标题
        title_elem = elem.select_one(".title, .goods-title, [class*='title']")
        item["title"] = title_elem.get_text(strip=True) if title_elem else ""
        
        # 价格
        price_elem = elem.select_one(".price, .goods-price, [class*='price']")
        if price_elem:
            price_text = price_elem.get_text(strip=True)
            price = re.findall(r"[\d.]+", price_text)
            item["price"] = float(price[0]) if price else 0.0
        else:
            item["price"] = 0.0
        
        # 原价
        item["original_price"] = None
        
        # 卖家
        seller_elem = elem.select_one(".seller, .nick, [class*='seller']")
        item["seller"] = seller_elem.get_text(strip=True) if seller_elem else ""
        
        # 卖家等级
        level_elem = elem.select_one("[class*='level'], .seller-level")
        item["seller_level"] = level_elem.get_text(strip=True) if level_elem else None
        
        # 所在地
        loc_elem = elem.select_one(".location, [class*='location']")
        item["location"] = loc_elem.get_text(strip=True) if loc_elem else ""
        
        # 图片
        img_elem = elem.select_one("img")
        item["images"] = [img_elem.get("src") or img_elem.get("data-src") or ""] if img_elem else []
        
        # 浏览量
        view_elem = elem.select_one("[class*='view']")
        if view_elem:
            view_text = view_elem.get_text(strip=True)
            views = re.findall(r"(\d+)", view_text)
            item["view_count"] = int(views[0]) if views else 0
        else:
            item["view_count"] = 0
        
        # 想要数
        like_elem = elem.select_one("[class*='like'], .want")
        if like_elem:
            like_text = like_elem.get_text(strip=True)
            likes = re.findall(r"(\d+)", like_text)
            item["like_count"] = int(likes[0]) if likes else 0
        else:
            item["like_count"] = 0
        
        # 评论数
        item["comment_count"] = 0
        
        # 发布时间
        time_elem = elem.select_one("[class*='time'], .posted-time")
        item["posted_time"] = time_elem.get_text(strip=True) if time_elem else ""
        
        return item if item.get("item_id") else None
    
    def parse_item_detail(self, html: str, item_id: str) -> Optional[CarModelItem]:
        """解析商品详情页"""
        soup = BeautifulSoup(html, "html.parser")
        
        # 获取标题
        title_elem = soup.select_one(".item-title, h1.title, [class*='title']")
        title = title_elem.get_text(strip=True) if title_elem else ""
        
        # 获取价格
        price_elem = soup.select_one(".price, .item-price, [class*='price']")
        price = 0.0
        if price_elem:
            price_text = price_elem.get_text(strip=True)
            price_match = re.findall(r"[\d.]+", price_text)
            price = float(price_match[0]) if price_match else 0.0
        
        # 获取卖家信息
        seller_elem = soup.select_one(".seller-nick, .nick-name, [class*='seller']")
        seller = seller_elem.get_text(strip=True) if seller_elem else ""
        
        # 获取描述
        desc_elem = soup.select_one(".description, .item-desc, [class*='desc']")
        description = desc_elem.get_text(strip=True) if desc_elem else ""
        
        # 获取图片
        images = []
        for img in soup.select("img"):
            src = img.get("src") or img.get("data-src") or ""
            if src and "xianyu" in src.lower():
                images.append(src)
        
        # 提取品牌和比例信息
        brand = ""
        scale = "1:64"
        condition = ""
        
        # 从标题或描述中提取
        text_content = f"{title} {description}"
        scale_match = re.search(r"1:(\d+)", text_content)
        if scale_match:
            scale = f"1:{scale_match.group(1)}"
        
        # 常见车模品牌
        brands = ["Inno", "Make", "Kyosho", "Minichamps", "Autoart", "Norev", 
                  "Spark", "Hot Wheels", "风火轮", "火柴盒", "多美卡", "Tomy",
                  "绿地", "合金", "车标", "原厂", "定制"]
        for b in brands:
            if b.lower() in text_content.lower():
                brand = b
                break
        
        # 新旧程度
        condition_keywords = ["全新", "未拆封", "轻微把玩", "有瑕疵", "拆盒", "展示品"]
        for ck in condition_keywords:
            if ck in text_content:
                condition = ck
                break
        
        item = CarModelItem(
            item_id=item_id,
            title=title,
            price=price,
            original_price=None,
            seller=seller,
            seller_level=None,
            location="",
            images=images,
            description=description,
            scale=scale,
            brand=brand,
            condition=condition,
            category="1:64车模",
            view_count=0,
            like_count=0,
            comment_count=0,
            posted_time="",
            url=f"{BASE_URL}/item/{item_id}",
            scraped_at=time.strftime("%Y-%m-%d %H:%M:%S"),
        )
        
        return item
    
    async def search_car_models(self, keyword: str = "1:64车模", max_pages: int = 5) -> list[CarModelItem]:
        """搜索车模商品"""
        self.conn = init_db(self.db_path)
        all_items = []
        
        async with httpx.AsyncClient(follow_redirects=True, timeout=TIMEOUT) as client:
            for page in range(1, max_pages + 1):
                print(f"正在爬取第 {page}/{max_pages} 页...")
                
                # 构造搜索URL
                params = {
                    "k": keyword,
                    "page": page,
                }
                url = f"{SEARCH_URL}?" + "&".join(f"{k}={v}" for k, v in params.items())
                
                html = await self.fetch_page(client, url)
                if not html:
                    continue
                
                raw_items, total_pages = self.parse_search_page(html)
                print(f"  找到 {len(raw_items)} 个商品")
                
                for raw_item in raw_items:
                    item_id = raw_item.get("item_id", "")
                    if not item_id:
                        continue
                    
                    # 获取详情
                    detail_url = f"{BASE_URL}/item/{item_id}"
                    detail_html = await self.fetch_page(client, detail_url)
                    
                    if detail_html:
                        item = self.parse_item_detail(detail_html, item_id)
                        if item:
                            all_items.append(item)
                            self.stats["success"] += 1
                    
                    self.stats["total"] += 1
                    await asyncio.sleep(DELAY)
                
                if page >= total_pages:
                    break
                
                await asyncio.sleep(DELAY)
        
        # 保存到数据库
        if all_items:
            save_to_db(self.conn, all_items)
            print(f"已保存 {len(all_items)} 个商品到数据库")
        
        return all_items
    
    async def run(self, keyword: str = "1:64车模", max_pages: int = 5):
        """运行爬虫"""
        print(f"=" * 50)
        print(f"闲鱼 1:64 车模数据爬虫")
        print(f"关键词: {keyword}")
        print(f"最大页数: {max_pages}")
        print(f"=" * 50)
        
        start_time = time.time()
        items = await self.search_car_models(keyword, max_pages)
        elapsed = time.time() - start_time
        
        print(f"\n完成! 共爬取 {len(items)} 个商品")
        print(f"成功: {self.stats['success']}, 失败: {self.stats['failed']}")
        print(f"耗时: {elapsed:.2f} 秒")
        
        return items

# ========== 导出函数 ==========
def export_to_json(items: list[CarModelItem], output_path: str = "car_models.json"):
    """导出到JSON文件"""
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump([asdict(item) for item in items], f, ensure_ascii=False, indent=2)
    print(f"已导出到 {output_path}")

def export_to_csv(items: list[CarModelItem], output_path: str = "car_models.csv"):
    """导出到CSV文件"""
    import csv
    if not items:
        return
    with open(output_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=asdict(items[0]).keys())
        writer.writeheader()
        for item in items:
            writer.writerow(asdict(item))
    print(f"已导出到 {output_path}")

# ========== 主入口 ==========
def main():
    parser = argparse.ArgumentParser(description="闲鱼 1:64 车模数据爬虫")
    parser.add_argument("--keyword", "-k", default="1:64车模", help="搜索关键词")
    parser.add_argument("--max-pages", "-n", type=int, default=5, help="最大爬取页数")
    parser.add_argument("--output", "-o", default="car_models.json", help="输出文件路径")
    parser.add_argument("--format", "-f", choices=["json", "csv"], default="json", help="输出格式")
    parser.add_argument("--db-path", default="car_model.db", help="数据库路径")
    
    args = parser.parse_args()
    
    scraper = XianyuScraper(db_path=args.db_path)
    items = asyncio.run(scraper.run(keyword=args.keyword, max_pages=args.max_pages))
    
    if items:
        if args.format == "json":
            export_to_json(items, args.output)
        else:
            export_to_csv(items, args.output.replace(".json", ".csv"))

if __name__ == "__main__":
    main()
