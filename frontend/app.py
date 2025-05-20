"""
前端Web应用 - 展示评论分析结果
"""
import os
from flask import Flask, render_template, request, jsonify
import requests
import json

app = Flask(__name__)

# 从环境变量获取标注服务地址
LABEL_SERVICE_URL = os.getenv('LABEL_SERVICE_URL', 'http://localhost:5001')

@app.route('/')
def index():
    """首页 - 展示数据可视化界面"""
    return render_template('index.html')

@app.route('/settings')
def settings():
    """设置页面 - 管理关键词和标签"""
    return render_template('settings.html')

# API代理 - 转发请求到标注服务
@app.route('/api/<path:subpath>', methods=['GET', 'POST'])
def api_proxy(subpath):
    """API代理 - 转发请求到标注服务"""
    url = f"{LABEL_SERVICE_URL}/api/{subpath}"
    
    if request.method == 'GET':
        resp = requests.get(url, params=request.args)
    else:  # POST
        resp = requests.post(url, json=request.json)
    
    return jsonify(resp.json()), resp.status_code

if __name__ == '__main__':
    # 获取端口
    port = int(os.getenv('FRONTEND_SERVICE_PORT', 5000))
    
    # 启动Flask应用
    app.run(host='0.0.0.0', port=port, debug=True) 