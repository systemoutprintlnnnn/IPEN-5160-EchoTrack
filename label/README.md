# EchoTrack 标注模块

标注模块负责使用OpenAI API为爬取的评论数据添加标签，并提供API服务供前端调用。

## 功能特性

- 对接OpenAI API实现评论智能分类
- 实现速率限制，避免API调用超限
- 提供RESTful API接口
- 数据持久化存储
- 数据桥接服务自动同步MongoDB数据

## 文件结构

```
label/
├── app.py             # Flask API服务
├── data_bridge.py     # MongoDB数据导入服务
├── labeler.py         # 评论标注核心逻辑
├── models.py          # 数据库模型
├── labeler.log        # 标注服务日志
└── data_bridge.log    # 数据桥接日志
```

## 实现原理

标注模块基于OpenAI API实现评论的智能分类，通过以下步骤处理数据：

1. 数据桥接服务从MongoDB读取爬虫爬取的评论数据
2. 标注服务使用OpenAI API为评论添加用户定义的标签
3. Flask API服务提供接口供前端查询标注结果

## 主要模块说明

### 1. models.py

定义数据库模型和相关操作，使用SQLite作为存储引擎。

主要表结构：
- `keywords`: 存储关键词信息
- `tags`: 存储标签对信息
- `comments`: 存储评论数据
- `labels`: 存储标签结果

主要方法：
- `init_db()`: 初始化数据库
- `add_keyword()`: 添加关键词
- `add_tag_pair()`: 添加标签对
- `add_comment()`: 添加评论
- `save_label_result()`: 保存标签结果

### 2. labeler.py

实现评论标注的核心逻辑，包括OpenAI API调用和速率限制。

主要类和方法：
- `RateLimiter`: 令牌桶算法实现API速率限制
- `CommentLabeler`: 评论标注器类
- `process_comments_batch()`: 批量处理评论
- `run_continuous_processing()`: 持续运行处理任务

### 3. app.py

提供RESTful API服务，支持前端查询和操作。

主要API接口：
- `/api/keywords`: 关键词管理
- `/api/tags`: 标签对管理
- `/api/comments`: 评论管理
- `/api/stats`: 标签统计数据

### 4. data_bridge.py

从MongoDB导入爬虫爬取的评论数据到SQLite数据库。

主要方法：
- `import_comments_from_mongodb()`: 导入评论数据
- `run_continuous_import()`: 持续运行导入任务

## 使用说明

1. 确保OpenAI API密钥已正确配置
2. 数据库表结构会在首次运行时自动创建
3. 标注服务会自动处理未标注的评论
4. API服务默认运行在5001端口

## 标注提示词设计

评论标注使用如下提示模板：

```
请仔细分析以下评论，判断它是否符合给定的标签对中的一个标签。
评论内容: "{评论内容}"

标签对:
- 正面标签: {正面标签}
- 负面标签: {负面标签}

请注意，评论最多只能符合一个标签（正面或负面），也可能两个都不符合。
请根据评论内容，判断它符合哪个标签，并给出相应的置信度。
```

返回格式为JSON，包含标签结果（positive/negative/none）和置信度。 