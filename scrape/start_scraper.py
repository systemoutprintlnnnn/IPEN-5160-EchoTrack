"""
B站爬虫启动脚本
"""

import sys
from Bilibili import start_scheduled_task

if __name__ == "__main__":
    print("启动B站爬虫任务...")
    try:
        start_scheduled_task()
    except KeyboardInterrupt:
        print("\n爬虫任务已停止")
        sys.exit(0)
