"""
淘宝/天猫 1:64 车模数据爬虫
Taobao/Tmall 1:64 Car Model Scraper

使用方法:
    python taobao_scraper.py [--max-pages N] [--output FILE] [--platform taobao|tmall|all]

注意: 淘宝/天猫有较强的反爬机制,建议配合代理池使用或降低请求频率
"""

import asyncio
import json
import math
import re
import sqlite3
import argparse
import time
import hashlib
import random
from dataclasses import dataclass, asdict
from pathlib import Path
from typing import Optional

import httpx
from bs4 import BeautifulSoup

# ========== 配置 ==========
TAOBAO_BASE_URL = "https://www.taobao.com"
TAOBAO_SEARCH_URL = "https://s.taobao.com/search"
TAOBAO_ITEM_URL = "https://item.taobao.com/item.htm"

TMALL_BASE_URL = "https://www.tmall.com"
TMALL_SEARCH_URL = "https://list.tmall.com/search_product.htm"
TMALL_ITEM_URL = "https://detail.tmall.com/item.htm"

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8",
    "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8",
    "Accept-Encoding": "gzip, deflate, br",
    "DNT": "1",
    "Connection": "keep-alive",
    "Upgrade-Insecure-Requests": "1",
    "Referer": "https://www.taobao.com/",
}

COOKIES = {
    "t": "0",  # 淘宝登录token,需要填写真实cookie
    "tracknick": "",
    "lgc": "",
    "cookie2": "",
    "_tb_token_": "",
}

TIMEOUT = 30.0
DELAY = 3.0  # 请求间隔(秒),避免被封禁
MAX_RETRIES = 3

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
    description: str       # 描述
    scale: str             # 比例 (1:64)
    brand: str             # 品牌
    condition: str         # 新旧程度
    category: str          # 分类
    view_count: int        # 浏览量
    like_count: int        # 收藏数
    comment_count: int     # 评论数
    sales_count: int       # 销量
    url: str               # 商品链接
    platform: str          # 平台 (taobao/tmall)
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
            sales_count INTEGER DEFAULT 0,
            url TEXT,
            platform TEXT,
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
            INSERT OR REPLACE INTO car_models VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
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
            item.sales_count,
            item.url,
            item.platform,
            item.scraped_at,
        ))
    conn.commit()


# ========== 爬虫核心 ==========
class TaobaoTmallScraper:
    """淘宝/天猫车模爬虫"""
    
    def __init__(self, db_path: str = "car_model.db"):
        self.db_path = db_path
        self.conn = None
        self.stats = {"success": 0, "failed": 0, "total": 0}
    
    async def fetch_page(self, client: httpx.AsyncClient, url: str, retries: int = MAX_RETRIES) -> Optional[str]:
        """获取页面HTML,带重试机制"""
        for attempt in range(retries):
            try:
                response = await client.get(url, headers=HEADERS, cookies=COOKIES, timeout=TIMEOUT)
                response.raise_for_status()
                # 淘宝返回gbk编码，尝试检测或使用默认
                try:
                    # 先尝试用gbk解码
                    return response.content.decode('gbk')
                except UnicodeDecodeError:
                    # 如果失败，使用response.text（httpx自动检测编码）
                    return response.text
            except Exception as e:
                print(f"请求失败 (尝试 {attempt + 1}/{retries}) [{url}]: {e}")
                if attempt < retries - 1:
                    await asyncio.sleep(DELAY * (attempt + 1))
        return None
    
    def parse_search_page(self, html: str, platform: str = "taobao") -> tuple[list[dict], int]:
        """解析搜索结果页面,返回(商品列表, 总页数)"""
        soup = BeautifulSoup(html, "html.parser")
        items = []
        total_pages = 100
        
        # 尝试从script标签提取JSON数据
        json_data = self._extract_json_from_script(soup)
        if json_data:
            items.extend(json_data)
        
        # 尝试从页面元素提取
        if not items:
            items = self._extract_from_elements(soup, platform)
        
        # 提取总页数
        page_elem = soup.select_one(".total, .page-info, [class*='page-total'], .totalPage")
        if page_elem:
            page_text = page_elem.get_text(strip=True)
            pages = re.findall(r"(\d+)", page_text)
            if pages:
                total_pages = min(int(pages[0]), 100)  # 限制最大页数
        
        return items, total_pages
    
    def _extract_json_from_script(self, soup: BeautifulSoup) -> list[dict]:
        """从script标签提取JSON数据"""
        items = []
        scripts = soup.find_all("script")
        
        for script in scripts:
            text = script.string or ""
            # 淘宝搜索结果数据通常在g_page_config或类似的全局变量中
            if "g_page_config" in text or "itemList" in text or "auctions" in text:
                # 尝试提取JSON对象
                patterns = [
                    r'g_page_config\s*=\s*(\{.*?\});',
                    r'"auctions"\s*:\s*(\[.*?\])',
                    r'"itemList"\s*:\s*(\[.*?\])',
                ]
                for pattern in patterns:
                    matches = re.findall(pattern, text, re.DOTALL)
                    for match in matches:
                        try:
                            data = json.loads(match)
                            if isinstance(data, dict) and "itemList" in data:
                                items.extend(data["itemList"])
                            elif isinstance(data, list):
                                items.extend(data)
                        except (json.JSONDecodeError, TypeError):
                            continue
        
        # 也尝试查找独立的item数据
        for script in scripts:
            text = script.string or ""
            if '"nid"' in text or '"item_num"' in text:
                # 提取所有nid
                nids = re.findall(r'"nid"\s*:\s*"(\d+)"', text)
                for nid in nids:
                    items.append({"item_id": nid})
        
        return items
    
    def _extract_from_elements(self, soup: BeautifulSoup, platform: str) -> list[dict]:
        """从页面元素提取商品数据"""
        items = []
        
        # 淘宝商品选择器
        selectors = [
            ".item, .item-box, .product-item",
            "[class*='item']",
            ".goods-item, .goods-list-item",
            "[data-itemid]",
        ]
        
        for selector in selectors:
            elems = soup.select(selector)
            if elems:
                for elem in elems:
                    try:
                        item = self._extract_item_data(elem, platform)
                        if item and item.get("item_id"):
                            items.append(item)
                    except Exception:
                        continue
                if items:
                    break
        
        return items
    
    def _extract_item_data(self, elem, platform: str) -> Optional[dict]:
        """从页面元素提取商品数据"""
        item = {}
        
        # 商品ID - 淘宝使用nid
        item_id = elem.get("data-itemid") or elem.get("data-nid") or ""
        if not item_id:
            link = elem.select_one("a")
            if link:
                href = link.get("href", "")
                # 淘宝item id模式
                nid_match = re.search(r"id=(\d+)", href)
                if nid_match:
                    item_id = nid_match.group(1)
                elif href.startswith("//item.taobao.com") or href.startswith("//detail.tmall.com"):
                    # 从路径提取
                    path_match = re.search(r"/(\d+)\.htm", href)
                    if path_match:
                        item_id = path_match.group(1)
        
        item["item_id"] = item_id
        
        # 标题 - 淘宝通常在title属性或特定class中
        title_elem = elem.select_one("[class*='title'], .product-title, h3 a, .item-name a")
        if title_elem:
            item["title"] = title_elem.get("title") or title_elem.get_text(strip=True)
        else:
            link = elem.select_one("a")
            if link:
                item["title"] = link.get("title") or link.get_text(strip=True)
            else:
                item["title"] = ""
        
        # 价格 - 淘宝价格通常在特定class中
        price_elem = elem.select_one("[class*='price'], .product-price, .price, .real-price")
        if price_elem:
            price_text = price_elem.get_text(strip=True)
            prices = re.findall(r"[\d.]+", price_text)
            item["price"] = float(prices[0]) if prices else 0.0
        else:
            # 尝试从整个元素文本中提取价格
            text = elem.get_text()
            prices = re.findall(r"¥\s*([\d.]+)", text)
            if prices:
                item["price"] = float(prices[0])
            else:
                item["price"] = 0.0
        
        # 原价
        original_price_elem = elem.select_one("[class*='original'], .original-price, del")
        if original_price_elem:
            orig_text = original_price_elem.get_text(strip=True)
            orig_prices = re.findall(r"[\d.]+", orig_text)
            item["original_price"] = float(orig_prices[0]) if orig_prices else None
        else:
            item["original_price"] = None
        
        # 卖家
        seller_elem = elem.select_one("[class*='seller'], .shop-name, [class*='nick'], .seller-name")
        if seller_elem:
            item["seller"] = seller_elem.get_text(strip=True)
        else:
            item["seller"] = ""
        
        # 卖家等级
        level_elem = elem.select_one("[class*='icon-rank'], .seller-rank, [class*='level']")
        if level_elem:
            level_text = level_elem.get("class") or []
            item["seller_level"] = str(level_text)
        else:
            item["seller_level"] = None
        
        # 所在地
        loc_elem = elem.select_one("[class*='location'], .location, [class*='addr']")
        if loc_elem:
            item["location"] = loc_elem.get_text(strip=True)
        else:
            item["location"] = ""
        
        # 图片
        img_elem = elem.select_one("img")
        if img_elem:
            img_src = img_elem.get("src") or img_elem.get("data-src") or img_elem.get("data-original") or ""
            # 淘宝图片可能需要处理
            if img_src and not img_src.startswith("http"):
                img_src = "https:" + img_src if img_src.startswith("//") else img_src
            item["images"] = [img_src] if img_src else []
        else:
            item["images"] = []
        
        # 销量
        sales_elem = elem.select_one("[class*='sale'], .sales-count, [class*='deal']")
        if sales_elem:
            sales_text = sales_elem.get_text(strip=True)
            sales_nums = re.findall(r"(\d+)", sales_text)
            item["sales_count"] = int(sales_nums[0]) if sales_nums else 0
        else:
            item["sales_count"] = 0
        
        # 浏览量
        view_elem = elem.select_one("[class*='view'], .view-count")
        if view_elem:
            view_text = view_elem.get_text(strip=True)
            views = re.findall(r"(\d+)", view_text)
            item["view_count"] = int(views[0]) if views else 0
        else:
            item["view_count"] = 0
        
        # 收藏数
        like_elem = elem.select_one("[class*='like'], [class*='collect'], .favorite")
        if like_elem:
            like_text = like_elem.get_text(strip=True)
            likes = re.findall(r"(\d+)", like_text)
            item["like_count"] = int(likes[0]) if likes else 0
        else:
            item["like_count"] = 0
        
        # 评论数
        comment_elem = elem.select_one("[class*='comment'], .comment-count")
        if comment_elem:
            comment_text = comment_elem.get_text(strip=True)
            comments = re.findall(r"(\d+)", comment_text)
            item["comment_count"] = int(comments[0]) if comments else 0
        else:
            item["comment_count"] = 0
        
        return item if item.get("item_id") else None
    
    def parse_item_detail(self, html: str, item_id: str, platform: str = "taobao") -> Optional[CarModelItem]:
        """解析商品详情页"""
        soup = BeautifulSoup(html, "html.parser")
        
        # 获取标题
        title_elem = soup.select_one("#itemName, .product-title h1, h1.title, [class*='product-name']")
        if not title_elem:
            title_elem = soup.select_one("title")
        title = title_elem.get_text(strip=True) if title_elem else ""
        # 清理标题
        title = re.sub(r"\s+", " ", title)
        
        # 获取价格 - 详情页价格
        price = 0.0
        price_selectors = [
            ".price span, .price-show, [class*='price']",
            "#price, .product-price",
            "[class*='price'] span",
        ]
        for selector in price_selectors:
            price_elem = soup.select_one(selector)
            if price_elem:
                price_text = price_elem.get_text(strip=True)
                prices = re.findall(r"[\d.]+", price_text)
                if prices:
                    price = float(prices[0])
                    break
        
        # 获取原价
        original_price = None
        orig_elem = soup.select_one(".original-price, del, [class*='original']")
        if orig_elem:
            orig_text = orig_elem.get_text(strip=True)
            orig_prices = re.findall(r"[\d.]+", orig_text)
            if orig_prices:
                original_price = float(orig_prices[0])
        
        # 获取卖家信息
        seller = ""
        seller_elem = soup.select_one(".seller-name, .shop-name, [class*='seller'] a, #shopName")
        if seller_elem:
            seller = seller_elem.get_text(strip=True)
        
        # 卖家等级
        seller_level = None
        level_elem = soup.select_one("[class*='rank'], [class*='level'], .seller-rank")
        if level_elem:
            seller_level = level_elem.get_text(strip=True)
        
        # 所在地
        location = ""
        loc_elem = soup.select_one("[class*='location'], .item-location, [class*='addr']")
        if loc_elem:
            location = loc_elem.get_text(strip=True)
        
        # 获取描述
        description = ""
        desc_elem = soup.select_one(".description, .product-desc, [class*='desc'], #description")
        if desc_elem:
            description = desc_elem.get_text(strip=True)
        
        # 获取图片
        images = []
        for img in soup.select("img"):
            src = img.get("src") or img.get("data-src") or img.get("data-original") or ""
            if src:
                if not src.startswith("http"):
                    src = "https:" + src if src.startswith("//") else src
                if any(ext in src.lower() for ext in ['.jpg', '.jpeg', '.png', '.webp', '.gif']):
                    if "logo" not in src.lower() and "placeholder" not in src.lower():
                        images.append(src)
        
        # 获取销量
        sales_count = 0
        sales_elem = soup.select_one("[class*='sale'], .sales-count, #J_SellCounter, [class*='sold']")
        if sales_elem:
            sales_text = sales_elem.get_text(strip=True)
            sales_nums = re.findall(r"(\d+)", sales_text)
            if sales_nums:
                sales_count = int(sales_nums[0])
        
        # 获取评论数
        comment_count = 0
        comment_elem = soup.select_one("#J_RateCounter, [class*='rate-count'], [class*='comment'] span")
        if comment_elem:
            comment_text = comment_elem.get_text(strip=True)
            comments = re.findall(r"(\d+)", comment_text)
            if comments:
                comment_count = int(comments[0])
        
        # 获取浏览量
        view_count = 0
        view_elem = soup.select_one("[class*='view'], #JViewCounter")
        if view_elem:
            view_text = view_elem.get_text(strip=True)
            views = re.findall(r"(\d+)", view_text)
            if views:
                view_count = int(views[0])
        
        # 提取品牌和比例信息
        brand = ""
        scale = "1:64"
        condition = ""
        
        # 从标题或描述中提取
        text_content = f"{title} {description}"
        
        # 提取比例
        scale_match = re.search(r"1:(\d+)", text_content)
        if scale_match:
            scale = f"1:{scale_match.group(1)}"
        
        # 常见车模品牌
        brands = [
            "Inno", "Make", "Kyosho", "Minichamps", "Autoart", "Norev",
            "Spark", "Hot Wheels", "风火轮", "火柴盒", "多美卡", "Tomy",
            "绿地", "合金", "车标", "原厂", "定制", "京商", "Keng tai",
            "CM's", "One", "Liu", "Ming", "Pan", "Amalgam", "BBR",
            "CMC", "MR", "Neo", "V站", "AA", "LF", "纸盒", "原牌",
        ]
        for b in brands:
            if b.lower() in text_content.lower():
                brand = b
                break
        
        # 新旧程度判断
        condition_keywords = {
            "全新": "全新",
            "未拆封": "未拆封",
            "未拆": "未拆封",
            "轻微把玩": "轻微把玩",
            "有瑕疵": "有瑕疵",
            "拆盒": "拆盒",
            "展示品": "展示品",
            "二手": "二手",
            "95新": "95新",
            "9成新": "9成新",
            "8成新": "8成新",
        }
        for keyword, cond in condition_keywords.items():
            if keyword in text_content:
                condition = cond
                break
        
        # 构造URL
        if platform == "tmall":
            item_url = f"{TMALL_ITEM_URL}?id={item_id}"
        else:
            item_url = f"{TAOBAO_ITEM_URL}?id={item_id}"
        
        item = CarModelItem(
            item_id=item_id,
            title=title,
            price=price,
            original_price=original_price,
            seller=seller,
            seller_level=seller_level,
            location=location,
            images=images[:10],  # 限制图片数量
            description=description[:500],  # 限制描述长度
            scale=scale,
            brand=brand,
            condition=condition,
            category="1:64车模",
            view_count=view_count,
            like_count=0,
            comment_count=comment_count,
            sales_count=sales_count,
            url=item_url,
            platform=platform,
            scraped_at=time.strftime("%Y-%m-%d %H:%M:%S"),
        )
        
        return item
    
    async def search_taobao(self, keyword: str = "1:64车模", max_pages: int = 5) -> list[CarModelItem]:
        """搜索淘宝车模"""
        return await self.search(keyword, max_pages, platform="taobao")
    
    async def search_tmall(self, keyword: str = "1:64车模", max_pages: int = 5) -> list[CarModelItem]:
        """搜索天猫车模"""
        return await self.search(keyword, max_pages, platform="tmall")
    
    async def search(self, keyword: str = "1:64车模", max_pages: int = 5, platform: str = "all") -> list[CarModelItem]:
        """搜索车模商品"""
        self.conn = init_db(self.db_path)
        all_items = []
        
        platforms_to_search = []
        if platform == "all":
            platforms_to_search = ["taobao", "tmall"]
        else:
            platforms_to_search = [platform]
        
        async with httpx.AsyncClient(follow_redirects=True, timeout=TIMEOUT) as client:
            for plat in platforms_to_search:
                print(f"\n{'='*50}")
                print(f"开始爬取 {plat.upper()}...")
                print(f"{'='*50}")
                
                for page in range(1, max_pages + 1):
                    print(f"正在爬取 {plat.upper()} 第 {page}/{max_pages} 页...")
                    
                    # 构造搜索URL
                    if plat == "taobao":
                        url = self._build_taobao_url(keyword, page)
                    else:
                        url = self._build_tmall_url(keyword, page)
                    
                    html = await self.fetch_page(client, url)
                    if not html:
                        print(f"  获取页面失败")
                        continue
                    
                    raw_items, total_pages = self.parse_search_page(html, plat)
                    print(f"  找到 {len(raw_items)} 个商品 (总页数: {total_pages})")
                    
                    for raw_item in raw_items:
                        item_id = raw_item.get("item_id", "")
                        if not item_id:
                            continue
                        
                        # 获取详情
                        if plat == "tmall":
                            detail_url = f"{TMALL_ITEM_URL}?id={item_id}"
                        else:
                            detail_url = f"{TAOBAO_ITEM_URL}?id={item_id}"
                        
                        detail_html = await self.fetch_page(client, detail_url)
                        
                        if detail_html:
                            item = self.parse_item_detail(detail_html, item_id, plat)
                            if item:
                                all_items.append(item)
                                self.stats["success"] += 1
                                if self.stats["success"] % 10 == 0:
                                    print(f"  已成功爬取 {self.stats['success']} 个商品")
                        
                        self.stats["total"] += 1
                        await asyncio.sleep(DELAY + random.uniform(0, 1))  # 随机延时
                    
                    if page >= total_pages:
                        break
                    
                    await asyncio.sleep(DELAY + random.uniform(0, 2))
        
        # 保存到数据库
        if all_items:
            save_to_db(self.conn, all_items)
            print(f"\n已保存 {len(all_items)} 个商品到数据库")
        
        return all_items
    
    def _build_taobao_url(self, keyword: str, page: int) -> str:
        """构建淘宝搜索URL"""
        params = {
            "q": keyword,
            "sort": "sale",  # 按销量排序
            "style": "grid",
            "s": (page - 1) * 44,
            "filterReservedOnly": "true",
        }
        query = "&".join(f"{k}={v}" for k, v in params.items())
        return f"{TAOBAO_SEARCH_URL}?{query}"
    
    def _build_tmall_url(self, keyword: str, page: int) -> str:
        """构建天猫搜索URL"""
        params = {
            "q": keyword,
            "sort": "sale",  # 按销量排序
            "pageNo": page,
        }
        query = "&".join(f"{k}={v}" for k, v in params.items())
        return f"{TMALL_SEARCH_URL}?{query}"
    
    async def run(self, keyword: str = "1:64车模", max_pages: int = 5, platform: str = "all"):
        """运行爬虫"""
        print(f"{'='*50}")
        print(f"淘宝/天猫 1:64 车模数据爬虫")
        print(f"关键词: {keyword}")
        print(f"最大页数: {max_pages}")
        print(f"平台: {platform}")
        print(f"{'='*50}")
        
        start_time = time.time()
        items = await self.search(keyword, max_pages, platform)
        elapsed = time.time() - start_time
        
        print(f"\n{'='*50}")
        print(f"完成! 共爬取 {len(items)} 个商品")
        print(f"成功: {self.stats['success']}, 失败: {self.stats['failed']}")
        print(f"耗时: {elapsed:.2f} 秒")
        print(f"{'='*50}")
        
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
    parser = argparse.ArgumentParser(description="淘宝/天猫 1:64 车模数据爬虫")
    parser.add_argument("--keyword", "-k", default="1:64车模", help="搜索关键词")
    parser.add_argument("--max-pages", "-n", type=int, default=5, help="最大爬取页数")
    parser.add_argument("--output", "-o", default="car_models.json", help="输出文件路径")
    parser.add_argument("--format", "-f", choices=["json", "csv"], default="json", help="输出格式")
    parser.add_argument("--platform", "-p", choices=["taobao", "tmall", "all"], default="all", help="爬取平台")
    parser.add_argument("--db-path", default="car_model.db", help="数据库路径")
    
    args = parser.parse_args()
    
    scraper = TaobaoTmallScraper(db_path=args.db_path)
    items = asyncio.run(scraper.run(keyword=args.keyword, max_pages=args.max_pages, platform=args.platform))
    
    if items:
        if args.format == "json":
            export_to_json(items, args.output)
        else:
            export_to_csv(items, args.output.replace(".json", ".csv"))


if __name__ == "__main__":
    main()
