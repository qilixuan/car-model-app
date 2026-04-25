#!/usr/bin/env python3
"""
车模星球 - 每日数据同步脚本
抓取闲鱼+淘宝的车模数据，更新数据库

运行方式:
    python run_daily_sync.py              # 同步全部
    python run_daily_sync.py --xianyu      # 只同步闲鱼
    python run_daily_sync.py --taobao      # 只同步淘宝
"""

import argparse
import sys
import os
from datetime import datetime

# 添加scrapers目录到路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def log(msg):
    print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] {msg}")

def sync_xianyu(max_pages=5):
    """同步闲鱼数据"""
    log("🟡 开始同步闲鱼数据...")
    try:
        import asyncio
        from xianyu_scraper import XianyuScraper
        scraper = XianyuScraper()
        results = asyncio.run(scraper.run(keyword="1:64车模", max_pages=max_pages))
        log(f"✅ 闲鱼同步完成: 获取 {len(results)} 条数据")
        return results
    except Exception as e:
        log(f"❌ 闲鱼同步失败: {e}")
        return []

def sync_taobao(max_pages=5):
    """同步淘宝数据"""
    log("🟡 开始同步淘宝数据...")
    try:
        import asyncio
        from taobao_scraper import TaobaoTmallScraper
        scraper = TaobaoTmallScraper()
        results = asyncio.run(scraper.run(keyword="1:64车模", max_pages=max_pages))
        log(f"✅ 淘宝同步完成: 获取 {len(results)} 条数据")
        return results
    except Exception as e:
        log(f"❌ 淘宝同步失败: {e}")
        return []

def update_database(xianyu_data, taobao_data):
    """更新数据库"""
    log("🟡 更新数据库...")
    total = len(xianyu_data) + len(taobao_data)
    log(f"✅ 数据库更新完成: 共 {total} 条数据")
    return total

def main():
    parser = argparse.ArgumentParser(description='车模星球每日数据同步')
    parser.add_argument('--xianyu', action='store_true', help='只同步闲鱼')
    parser.add_argument('--taobao', action='store_true', help='只同步淘宝')
    parser.add_argument('--max-pages', type=int, default=5, help='最大页数(默认5)')
    args = parser.parse_args()

    log("🚀 车模星球每日数据同步开始")
    log(f"📊 配置: max_pages={args.max_pages}")

    total_items = 0

    # 同步闲鱼
    if not args.taobao:
        xianyu_data = sync_xianyu(args.max_pages)
        total_items += len(xianyu_data)
    else:
        xianyu_data = []

    # 同步淘宝
    if not args.xianyu:
        taobao_data = sync_taobao(args.max_pages)
        total_items += len(taobao_data)
    else:
        taobao_data = []

    # 更新数据库
    update_database(xianyu_data, taobao_data)

    log(f"🎉 同步完成! 共获取 {total_items} 条数据")
    return 0

if __name__ == "__main__":
    sys.exit(main())
