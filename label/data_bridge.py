"""
数据桥接模块 - 将爬虫模块的数据导入到标注系统数据库
"""
import os
import json
import time
import logging
import sqlite3
import datetime
from pymongo import MongoClient
import models

# 设置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("data_bridge.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger("DataBridge")

# 从环境变量或配置文件获取MongoDB连接信息
MONGO_URI = os.getenv("MONGO_URI", "mongodb://localhost:27017/")
DB_NAME = os.getenv("MONGO_DB_NAME", "bilibili")
COLLECTION_NAME = os.getenv("MONGO_COLLECTION", "video_comments_ipen_5160")

# 用于记录已处理过的评论ID
PROCESSED_IDS_FILE = "data/processed_ids.json"

def load_processed_ids():
    """加载已处理过的评论ID列表"""
    try:
        if os.path.exists(PROCESSED_IDS_FILE):
            with open(PROCESSED_IDS_FILE, 'r', encoding='utf-8') as f:
                return set(json.load(f))
        else:
            return set()
    except Exception as e:
        logger.error(f"加载已处理ID失败: {e}")
        return set()

def save_processed_ids(processed_ids):
    """保存已处理过的评论ID列表"""
    try:
        # 确保数据目录存在
        os.makedirs(os.path.dirname(PROCESSED_IDS_FILE), exist_ok=True)
        
        with open(PROCESSED_IDS_FILE, 'w', encoding='utf-8') as f:
            json.dump(list(processed_ids), f)
    except Exception as e:
        logger.error(f"保存已处理ID失败: {e}")

def generate_comment_id(doc_id, comment_index, ctime):
    """生成唯一的评论ID"""
    return f"{doc_id}_{comment_index}_{ctime}"

def import_comments_from_mongodb():
    """从MongoDB导入评论数据到SQLite"""
    try:
        # 连接MongoDB
        client = MongoClient(MONGO_URI)
        db = client[DB_NAME]
        collection = db[COLLECTION_NAME]
        
        # 获取已处理过的评论ID
        processed_ids = load_processed_ids()
        
        # 查询文档
        cursor = collection.find({})
        
        new_processed_ids = set()
        imported_count = 0
        
        # 处理每个文档
        for doc in cursor:
            doc_id = str(doc["_id"])
            keyword = doc.get("keyword", "未知关键词")
            
            # 获取视频信息
            video_info = doc.get("video_info", {})
            video_title = video_info.get("title", doc.get("title", "未知视频"))
            video_url = f"https://www.bilibili.com/video/{video_info.get('bvid', '')}"
            
            # 确保关键词存在于数据库中
            keyword_id = models.add_keyword(keyword)
            
            # 处理评论数组
            comments_info = doc.get("commentsInfo", [])
            for index, comment in enumerate(comments_info):
                # 生成唯一评论ID
                uname = comment.get("uname", "匿名用户")
                content = comment.get("content", "")
                ctime = comment.get("ctime", 0)
                
                # 转换时间戳为可读格式
                if ctime:
                    comment_time = datetime.datetime.fromtimestamp(ctime)
                else:
                    comment_time = datetime.datetime.now()
                
                # 构建唯一标识符
                comment_unique_id = generate_comment_id(doc_id, index, ctime)
                
                # 如果已处理过该评论则跳过
                if comment_unique_id in processed_ids:
                    continue
                
                # 构建源URL
                source_url = f"{video_url}?#{uname}"
                
                # 跳过空评论
                if not content:
                    logger.warning(f"跳过空评论: {comment_unique_id}")
                    new_processed_ids.add(comment_unique_id)
                    continue
                
                # 添加评论
                try:
                    # 在内容前添加用户名和性别信息，方便后续分析
                    enriched_content = f"[用户:{uname} 性别:{comment.get('usex', '未知')}] {content}"
                    
                    models.add_comment(keyword_id, enriched_content, source_url, comment_time)
                    imported_count += 1
                    new_processed_ids.add(comment_unique_id)
                except sqlite3.Error as e:
                    logger.error(f"添加评论失败: {e}, 评论ID: {comment_unique_id}")
        
        # 更新已处理ID列表
        processed_ids.update(new_processed_ids)
        save_processed_ids(processed_ids)
        
        logger.info(f"导入完成，新增评论数: {imported_count}")
        return imported_count
    
    except Exception as e:
        logger.error(f"导入评论失败: {e}")
        return 0
    finally:
        # 关闭MongoDB连接
        if 'client' in locals():
            client.close()

def run_continuous_import(interval_seconds=60):
    """持续运行导入任务"""
    logger.info(f"启动持续导入任务，间隔: {interval_seconds}秒")
    
    # 确保数据库初始化
    models.init_db()
    
    while True:
        try:
            count = import_comments_from_mongodb()
            logger.info(f"本次导入完成，新增评论: {count}")
        except Exception as e:
            logger.error(f"导入过程出错: {e}")
        
        time.sleep(interval_seconds)

if __name__ == "__main__":
    # 启动持续导入任务
    run_continuous_import() 