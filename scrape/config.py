"""
Bilibili爬虫配置文件
"""

# Bilibili API凭证信息
BILIBILI_CREDENTIALS = {
    "SESSIONDATA": "8de4b28e%2C1759379533%2C426c1%2A42CjCOME2savjXqodnd14Arv5y6q9rX2fhKHlbL6fTboeaVMD68P0o0pSXcfkpmEZQi3ISVm15SlEwZS1YQmhFbmJvUlY2RkVMamctNEdBSlQ4ekV2bGIyWFBnZHNLMlp0TzFXZGhWeFVzcjUzNzB2UFdIYWdvdGxJTTJZdE56czF2c0RyWUdXWDZRIIEC",
    "BILI_JCT": "120bf3765734ab46c7fb24726edef950",
    "BUVID3": "A2D4DF5D-8110-2AD2-712E-CB70E86E460D66077infoc",
    "DEDEUSERID": "35556285",
    "AC_TIME_VALUE": "88f211501d832c4b8685a028f94063c2"
}

# 数据库配置
DB_CONFIG = {
    "MONGO_URI": "mongodb://localhost:27017/",
    "DB_NAME": "bilibili",
    "VIDEO_COMMENTS_COLLECTION": "video_comments_0406",
    "FILTERED_VIDEO_COLLECTION": "filted_video"
}

# 爬取配置
SCRAPE_CONFIG = {
    # 爬取间隔时间（分钟）
    "SCRAPE_INTERVAL_MINUTES": 1,
    # 关键词列表
    "KEYWORDS": ["iPhone 15", "小米 15"],
    # 搜索页数范围
    "PAGE_RANGE": (1, 3),
    # 随机延迟范围（秒）
    "NORMAL_DELAY_RANGE": (1, 3),
    # 请求失败后的重试延迟范围（秒）
    "RETRY_DELAY_RANGE": (1800, 3000)
} 