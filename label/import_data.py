"""
手动数据导入脚本 - 从MongoDB导入评论数据到SQLite
"""
import sys
import os
import argparse
import logging

# 设置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("import_data.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger("DataImport")

# 导入必要的模块
try:
    import models
    from data_bridge import import_comments_from_mongodb
except ImportError:
    # 处理相对导入
    sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    from label import models
    from label.data_bridge import import_comments_from_mongodb

def main():
    """执行数据导入"""
    parser = argparse.ArgumentParser(description="从MongoDB导入评论数据到SQLite")
    parser.add_argument("--reset", action="store_true", help="重置已处理ID，重新导入所有数据")
    args = parser.parse_args()
    
    # 初始化数据库
    logger.info("初始化数据库...")
    models.init_db()
    
    # 如果需要重置，删除处理记录文件
    if args.reset:
        import data_bridge
        processed_ids_file = data_bridge.PROCESSED_IDS_FILE
        if os.path.exists(processed_ids_file):
            os.remove(processed_ids_file)
            logger.info(f"已删除处理记录文件: {processed_ids_file}")
    
    # 执行导入
    logger.info("开始导入数据...")
    count = import_comments_from_mongodb()
    logger.info(f"导入完成，成功导入 {count} 条评论")

if __name__ == "__main__":
    main() 