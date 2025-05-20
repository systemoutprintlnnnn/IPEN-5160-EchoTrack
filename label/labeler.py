"""
评论标注模块 - 使用OpenAI API为评论打标签
"""
import os
import time
import json
import threading
import logging
from openai import OpenAI, AsyncOpenAI
from datetime import datetime
import models

# 设置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("labeler.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger("CommentLabeler")

# 从环境变量获取API配置
api_key = os.getenv("OPENAI_API_KEY", "7d3464591e024c049cb64f8d8b7cb59e.jPXkPyPuLuAx21j1")  # 必须在.env文件中提供
model_name = os.getenv("OPENAI_MODEL", "glm-4-flash")  # 默认模型
max_tokens_per_min = int(os.getenv("MAX_TOKENS_PER_MIN", "90000"))  # 默认90k tokens/min
max_requests_per_min = int(os.getenv("MAX_REQUESTS_PER_MIN", "3500"))  # 默认3500请求/min

class RateLimiter:
    """
    实现令牌桶算法进行速率限制
    """
    def __init__(self, max_tokens_per_min, max_requests_per_min):
        self.max_tokens_per_min = max_tokens_per_min
        self.max_requests_per_min = max_requests_per_min
        self.tokens_available = max_tokens_per_min
        self.requests_available = max_requests_per_min
        self.last_refill_time = time.time()
        self.lock = threading.Lock()
    
    def can_make_request(self, tokens_required):
        with self.lock:
            self._refill()
            if (self.tokens_available >= tokens_required and 
                self.requests_available >= 1):
                self.tokens_available -= tokens_required
                self.requests_available -= 1
                return True
            return False
    
    def _refill(self):
        now = time.time()
        elapsed = now - self.last_refill_time
        if elapsed > 0:
            # 按比例补充令牌
            new_tokens = int(elapsed * (self.max_tokens_per_min / 60))
            new_requests = int(elapsed * (self.max_requests_per_min / 60))
            
            self.tokens_available = min(
                self.max_tokens_per_min, 
                self.tokens_available + new_tokens
            )
            self.requests_available = min(
                self.max_requests_per_min,
                self.requests_available + new_requests
            )
            self.last_refill_time = now

# 创建速率限制器实例
rate_limiter = RateLimiter(max_tokens_per_min, max_requests_per_min)

class CommentLabeler:
    """
    评论标注器 - 使用OpenAI API为评论打标签
    单例模式实现，确保只初始化一次
    """
    _instance = None
    _initialized = False
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(CommentLabeler, cls).__new__(cls)
        return cls._instance
    
    def __init__(self):
        # 只在第一次初始化时执行
        if not CommentLabeler._initialized:
            if not api_key:
                raise ValueError("未设置OPENAI_API_KEY环境变量")
            
            # 创建客户端时不使用不支持的参数
            self.client = OpenAI(
                api_key=api_key,
                base_url="https://open.bigmodel.cn/api/paas/v4/"
            )
            self.model = model_name
            logger.info(f"CommentLabeler初始化完成，使用模型: {self.model}")
            CommentLabeler._initialized = True
    
    def label_comment(self, comment_text, tag_pair):
        """
        为单条评论添加标签
        
        Args:
            comment_text: 评论文本
            tag_pair: 标签对(positive_tag, negative_tag)
            
        Returns:
            label: 'positive', 'negative', 或 'none'
            confidence: 置信度(0-1)
        """
        positive_tag = tag_pair['positive_tag']
        negative_tag = tag_pair['negative_tag']
        
        # 构建提示模板
        prompt = f"""
        请仔细分析以下评论，判断它是否符合给定的标签对中的一个标签。
        评论内容: "{comment_text}"
        
        标签对:
        - 正面标签: {positive_tag}
        - 负面标签: {negative_tag}
        
        请注意，评论最多只能符合一个标签（正面或负面），也可能两个都不符合。
        请根据评论内容，判断它符合哪个标签，并给出相应的置信度。
        
        请使用以下JSON格式回答:
        {{
            "label": "positive" 或 "negative" 或 "none",
            "confidence": 0到1之间的数值,
            "reasoning": "简要说明你的判断理由"
        }}
        """
        
        # 估算令牌数量
        estimated_tokens = len(prompt.split()) * 1.5  # 简单估算
        
        # 等待速率限制器允许请求
        allowed = False
        while not allowed:
            allowed = rate_limiter.can_make_request(estimated_tokens)
            if not allowed:
                time.sleep(0.1)  # 短暂等待后重试
        
        try:
            # 调用OpenAI API
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "你是一个专业的评论分析助手，擅长根据给定标签判断评论的类别。"},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.1,  # 降低随机性，使结果更确定
                max_tokens=300
            )
            
            # 解析返回结果
            content = response.choices[0].message.content
            try:
                # 尝试解析JSON
                json_start = content.find('{')
                json_end = content.rfind('}') + 1
                if json_start != -1 and json_end != -1:
                    json_content = content[json_start:json_end]
                    result = json.loads(json_content)
                    label = result.get('label', 'none')
                    confidence = result.get('confidence', 0.0)
                    logger.info(f"标签结果: {label}, 置信度: {confidence}, 理由: {result.get('reasoning', '无')}")
                    return label, confidence
                else:
                    logger.warning(f"无法从响应中找到JSON: {content}")
                    return "none", 0.0
            except json.JSONDecodeError:
                logger.warning(f"JSON解析错误: {content}")
                return "none", 0.0
            
        except Exception as e:
            if "429" in str(e):  # 请求过多错误
                logger.warning(f"请求过多，等待后重试: {e}")
                time.sleep(60)  # 等待一分钟
                return self.label_comment(comment_text, tag_pair)  # 重试
            else:
                logger.error(f"API调用错误: {e}")
                return "none", 0.0

def process_comments_batch(batch_size=10):
    """
    处理一批未标注的评论
    """
    # 获取未处理评论
    unprocessed_comments = models.get_unprocessed_comments(limit=batch_size)
    
    if not unprocessed_comments:
        logger.info("没有未处理的评论")
        return
    
    logger.info(f"开始处理{len(unprocessed_comments)}条评论")
    
    # 获取所有标签对
    tag_pairs = models.get_all_tag_pairs()
    
    if not tag_pairs:
        logger.warning("没有标签对可用，请先添加标签对")
        return
    
    labeler = CommentLabeler()
    
    for comment in unprocessed_comments:
        comment_id = comment['id']
        content = comment['content']
        logger.info(f"处理评论ID: {comment_id}, 内容: {content[:50]}...")
        
        # 对每个标签对进行判断
        for tag_pair in tag_pairs:
            tag_id = tag_pair['id']
            logger.info(f"评估标签对ID: {tag_id} ({tag_pair['positive_tag']} / {tag_pair['negative_tag']})")
            
            label, confidence = labeler.label_comment(content, tag_pair)
            logger.info(f"标签结果: {label}, 置信度: {confidence}")
            
            # 保存标签结果
            models.save_label_result(comment_id, tag_id, label, confidence)
        
        # 标记评论为已处理
        models.mark_comment_as_processed(comment_id)
        logger.info(f"评论ID: {comment_id} 处理完成")
    
    logger.info(f"批处理完成，共处理{len(unprocessed_comments)}条评论")

def run_continuous_processing():
    """
    持续处理评论
    """
    while True:
        try:
            process_comments_batch()
            time.sleep(100)  # 短暂休息后继续处理下一批
        except Exception as e:
            logger.error(f"处理过程中出错: {e}")
            time.sleep(30)  # 出错后等待较长时间再重试

if __name__ == "__main__":
    # 确保数据库已初始化
    models.init_db()
    
    # 启动持续处理
    run_continuous_processing() 