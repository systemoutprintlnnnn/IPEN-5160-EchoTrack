import asyncio
import json
import time
import schedule
import logging
from datetime import datetime
from pprint import pprint
from pymongo import MongoClient

from bilibili_api.comment import OrderType
from scrape.BilibiliScraper import BilibiliScraper
from bilibili_api import Credential, search, topic, sync, comment
from scrape.config import BILIBILI_CREDENTIALS, SCRAPE_CONFIG

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("scrape/scraper.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger("BilibiliScraper")

class Bilibili:

    def __init__(self):
        # 使用配置文件中的凭证信息
        credential = Credential(
            BILIBILI_CREDENTIALS["SESSIONDATA"],
            BILIBILI_CREDENTIALS["BILI_JCT"],
            BILIBILI_CREDENTIALS["BUVID3"],
            BILIBILI_CREDENTIALS["DEDEUSERID"],
            BILIBILI_CREDENTIALS["AC_TIME_VALUE"]
        )
        self.credential = credential
        logger.info(f"凭证状态: {sync(credential.check_refresh())}")
        if sync(credential.check_refresh()):
            sync(credential.refresh())
            logger.info("凭证已刷新")

    async def scrape_task(self) -> None:
        """
        定时爬取任务，会在每次调度时运行
        """
        logger.info(f"开始爬取任务: {datetime.now()}")
        b = BilibiliScraper()
        keyword_list = SCRAPE_CONFIG["KEYWORDS"]
        start_page, end_page = SCRAPE_CONFIG["PAGE_RANGE"]

        # 一次20个视频
        for i in range(start_page, end_page):
            for keyword in keyword_list:
                logger.info(f"爬取关键词: {keyword}, 页码: {i}")
                await b.get_video_comments_by_keyword(keyword, i)

        logger.info(f"爬取任务完成: {datetime.now()}")
        return True

def start_scheduled_task():
    """
    启动定时任务
    """
    bilibili = Bilibili()
    
    # 立即运行一次
    logger.info("首次运行爬虫任务")
    asyncio.run(bilibili.scrape_task())
    
    # 设置定时任务
    interval_minutes = SCRAPE_CONFIG["SCRAPE_INTERVAL_MINUTES"]
    logger.info(f"设置定时任务，每 {interval_minutes} 分钟运行一次")
    
    # 使用schedule库设置定时任务
    schedule.every(interval_minutes).minutes.do(lambda: asyncio.run(bilibili.scrape_task()))
    
    # 持续运行定时任务
    while True:
        schedule.run_pending()
        time.sleep(1)

if __name__ == "__main__":
    # 使用定时任务启动爬虫
    start_scheduled_task()
