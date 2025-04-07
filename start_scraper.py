#!/usr/bin/env python3
"""
B站爬虫启动脚本
"""
import os
import sys
from scrape.Bilibili import start_scheduled_task

if __name__ == "__main__":
    print("启动B站爬虫任务...")
    try:
        start_scheduled_task()
    except KeyboardInterrupt:
        print("\n爬虫任务已停止")
        sys.exit(0)
    except Exception as e:
        print(f"爬虫任务发生错误: {e}")
        sys.exit(1) 