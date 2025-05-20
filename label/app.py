"""
标注服务API - 提供标签和评论相关的HTTP接口
"""
import os
import threading
import time
from flask import Flask, request, jsonify
from flask_cors import CORS

import models
import labeler

# 初始化数据库
models.init_db()

app = Flask(__name__)
CORS(app)  # 允许跨域请求

# 启动后台处理线程
processing_thread = None

def start_processing_thread():
    """启动后台处理线程"""
    global processing_thread
    if processing_thread is None or not processing_thread.is_alive():
        processing_thread = threading.Thread(target=labeler.run_continuous_processing)
        processing_thread.daemon = True
        processing_thread.start()

# 关键词相关API
@app.route('/api/keywords', methods=['GET'])
def get_keywords():
    """获取所有关键词"""
    keywords = models.get_all_keywords()
    return jsonify([dict(keyword) for keyword in keywords])

@app.route('/api/keywords', methods=['POST'])
def add_keyword():
    """添加新关键词"""
    data = request.json
    if not data or 'keyword' not in data:
        return jsonify({"error": "缺少关键词"}), 400
    
    keyword = data['keyword']
    keyword_id = models.add_keyword(keyword)
    return jsonify({"id": keyword_id, "keyword": keyword})

# 标签对相关API
@app.route('/api/tags', methods=['GET'])
def get_tags():
    """获取所有标签对"""
    tags = models.get_all_tag_pairs()
    return jsonify([dict(tag) for tag in tags])

@app.route('/api/tags', methods=['POST'])
def add_tag():
    """添加新标签对"""
    data = request.json
    if not data or 'positive_tag' not in data or 'negative_tag' not in data:
        return jsonify({"error": "缺少标签信息"}), 400
    
    positive_tag = data['positive_tag']
    negative_tag = data['negative_tag']
    tag_id = models.add_tag_pair(positive_tag, negative_tag)
    return jsonify({
        "id": tag_id, 
        "positive_tag": positive_tag, 
        "negative_tag": negative_tag
    })

# 评论相关API
@app.route('/api/comments', methods=['POST'])
def add_comment():
    """添加新评论"""
    data = request.json
    if not data or 'content' not in data or 'keyword_id' not in data:
        return jsonify({"error": "缺少评论信息"}), 400
    
    keyword_id = data['keyword_id']
    content = data['content']
    source_url = data.get('source_url')
    comment_time = data.get('comment_time')
    
    comment_id = models.add_comment(keyword_id, content, source_url, comment_time)
    return jsonify({"id": comment_id})

# 统计数据API
@app.route('/api/stats', methods=['GET'])
def get_stats():
    """获取标签统计数据"""
    keyword_id = request.args.get('keyword_id', type=int)
    stats = models.get_label_stats(keyword_id)
    
    # 转换为前端易于使用的格式
    result = []
    for stat in stats:
        total = stat['positive_count'] + stat['negative_count'] + stat['none_count']
        if total > 0:
            positive_percent = round(stat['positive_count'] / total * 100, 1)
            negative_percent = round(stat['negative_count'] / total * 100, 1)
            none_percent = round(stat['none_count'] / total * 100, 1)
        else:
            positive_percent = negative_percent = none_percent = 0
            
        result.append({
            'id': stat['id'],
            'positive_tag': stat['positive_tag'],
            'negative_tag': stat['negative_tag'],
            'positive_count': stat['positive_count'],
            'negative_count': stat['negative_count'],
            'none_count': stat['none_count'],
            'positive_percent': positive_percent,
            'negative_percent': negative_percent,
            'none_percent': none_percent,
            'total': total
        })
    
    return jsonify(result)

# 健康检查API
@app.route('/health', methods=['GET'])
def health_check():
    """健康检查"""
    return jsonify({"status": "ok"})

if __name__ == '__main__':
    # 启动处理线程
    start_processing_thread()
    
    # 获取端口
    port = int(os.getenv('LABEL_SERVICE_PORT', 5001))
    
    # 启动Flask应用
    app.run(host='0.0.0.0', port=port, debug=False) 