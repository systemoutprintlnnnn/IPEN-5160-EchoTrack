# EchoTrack - 评论分析跟踪系统

EchoTrack是一个自动化评论分析系统，能够根据用户设定的关键词爬取哔哩哔哩平台的评论数据，通过大语言模型对评论进行标签分类，并通过可视化界面展示分析结果。

## 系统架构

系统分为三个主要模块：

1. **爬虫模块（scrape）**：负责从哔哩哔哩定时爬取最新评论
2. **标注模块（label）**：调用OpenAI API为评论打上用户定义的标签
3. **前端模块（frontend）**：提供用户界面，展示评论分析结果

## 功能特性

- 支持多关键词评论爬取
- 支持用户自定义标签对
- 使用OpenAI API进行智能评论分类
- 直观的数据可视化展示
- 实时数据更新和监控

## 环境要求

- Python 3.8+
- MongoDB（用于存储爬虫数据）
- OpenAI API密钥
- 网络连接（用于API调用和网页爬取）

## 快速开始

### 1. 安装依赖

```bash
pip install -r requirements.txt
```

### 2. 配置环境变量

在项目根目录创建`.env`文件，内容如下：

```
# OpenAI配置
OPENAI_API_KEY=your_api_key_here
OPENAI_MODEL=gpt-3.5-turbo

# MongoDB配置
MONGO_URI=mongodb://localhost:27017/
MONGO_DB_NAME=bilibili
MONGO_COLLECTION=video_comments_ipen_5160
```

### 3. 启动系统

```bash
python run.py
```

启动后，访问 http://localhost:5000 打开前端界面

## 配置选项

启动脚本支持以下命令行参数：

- `--no-scraper`：不启动爬虫服务
- `--no-labeler`：不启动标注服务
- `--no-bridge`：不启动数据桥接服务
- `--no-frontend`：不启动前端服务

示例：

```bash
# 只启动前端和标注服务
python run.py --no-scraper --no-bridge
```

## 目录结构

```
IPEN-5160-EchoTrack/
├── run.py              # 主启动脚本
├── requirements.txt    # 项目依赖
├── .env                # 环境配置文件
├── env_config.py       # 环境配置加载模块
├── data/               # 数据存储目录
├── scrape/             # 爬虫模块
├── label/              # 标注模块
└── frontend/           # 前端模块
```

## 使用方法

1. 在设置页面添加关键词和标签对
2. 爬虫会自动从哔哩哔哩获取相关评论
3. 标注服务会为评论自动添加标签
4. 在主页查看数据分析结果

## 许可证

[MIT License](LICENSE) 