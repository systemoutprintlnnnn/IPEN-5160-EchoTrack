# IPEN-5160-EchoTrack
A real-time comment monitoring tool designed to collect and analyze user sentiments

## 项目说明
这是一个B站视频评论爬虫工具，可以按关键词搜索视频并爬取视频下的所有评论数据，支持定时任务和断点续传功能。

## 功能特点
- 根据关键词搜索B站视频
- 抓取视频下所有评论数据
- 支持定时任务，可配置爬取频率
- 断点续传，避免重复爬取
- 数据自动存储到MongoDB数据库
- 多级重试机制，提高爬取成功率

## 安装与配置

### 1. 安装依赖
```bash
pip install -r requirements.txt
```

### 2. 配置MongoDB
确保您的计算机已安装并启动MongoDB服务，默认连接地址为`mongodb://localhost:27017/`。

### 3. 修改配置文件
配置文件位于`scrape/config.py`，您可以根据需要修改以下配置：
- `BILIBILI_CREDENTIALS`: B站API凭证信息
- `DB_CONFIG`: 数据库配置
- `SCRAPE_CONFIG`: 爬取配置，包括关键词、爬取间隔等

### 4. 启动爬虫
```bash
python start_scraper.py
```

## 配置说明

### 爬取间隔
在`scrape/config.py`中修改`SCRAPE_CONFIG["SCRAPE_INTERVAL_MINUTES"]`的值以调整爬虫执行频率。

### 关键词设置
在`scrape/config.py`中修改`SCRAPE_CONFIG["KEYWORDS"]`列表以设置要搜索的关键词。

### 搜索页数范围
在`scrape/config.py`中修改`SCRAPE_CONFIG["PAGE_RANGE"]`元组以设置要搜索的页数范围。

## 日志
爬虫运行日志保存在`scrape/scraper.log`文件中，可随时查看爬取状态。
