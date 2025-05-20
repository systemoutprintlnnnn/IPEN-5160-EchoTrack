"""
Bilibili爬虫配置文件
"""

# Bilibili API凭证信息
BILIBILI_CREDENTIALS = {
    "SESSIONDATA": "1f6db115%2C1763291184%2Cbc533%2A52CjCYB760S0DBWUl2SQeiu3tdn7jX4vINvyc6K7c7h8bYqTl1jsydDI8a0F84Dx4X76USVjZFZVYxU05jMzFpQXQ5eE1rTjhjXzJlZlZMR0hsSmpXYm55QXh1eUxnMkxrOHQ5b3dEd2VZV3JxbmFQOHRmTUxvSW5OcmNYaEQxUk5yNkNBdHBYcC1nIIEC",
    "BILI_JCT": "2fac34dca980517024642ae74d6a1fa1",
    "BUVID3": "A2D4DF5D-8110-2AD2-712E-CB70E86E460D66077infoc",
    "DEDEUSERID": "35556285",
    "AC_TIME_VALUE": "361eef421780886d66ffb81c1e1d3152"
}

# 数据库配置
DB_CONFIG = {
    "MONGO_URI": "mongodb://localhost:27017/",
    "DB_NAME": "bilibili",
    "VIDEO_COMMENTS_COLLECTION": "video_comments_ipen_5160",
    "FILTERED_VIDEO_COLLECTION": "filted_video"
}

# 爬取配置
SCRAPE_CONFIG = {
    # 爬取间隔时间（分钟）
    "SCRAPE_INTERVAL_MINUTES": 1,
    # 关键词列表
    "KEYWORDS": ["特斯拉", "蔚来", "比亚迪", "极氪", "小鹏"],
    # 搜索页数范围
    "PAGE_RANGE": (1, 5),
    # 随机延迟范围（秒）
    "NORMAL_DELAY_RANGE": (1, 3),
    # 请求失败后的重试延迟范围（秒）
    "RETRY_DELAY_RANGE": (1800, 3000)
}
