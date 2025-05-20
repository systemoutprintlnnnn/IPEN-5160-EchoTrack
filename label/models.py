"""
数据库模型定义
"""
import sqlite3
import os
import datetime
from pathlib import Path

# 确保数据目录存在
data_dir = Path('data')
data_dir.mkdir(exist_ok=True)

DB_PATH = os.getenv('DATABASE_PATH', 'data/echotrack.db')

def get_db_connection():
    """获取数据库连接"""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    """初始化数据库"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # 创建关键词表
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS keywords (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        keyword TEXT NOT NULL UNIQUE,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    ''')
    
    # 创建标签对表
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS tags (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        positive_tag TEXT NOT NULL,
        negative_tag TEXT NOT NULL,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        UNIQUE(positive_tag, negative_tag)
    )
    ''')
    
    # 创建评论表
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS comments (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        keyword_id INTEGER,
        content TEXT NOT NULL,
        source_url TEXT,
        comment_time TIMESTAMP,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        processed BOOLEAN DEFAULT 0,
        FOREIGN KEY (keyword_id) REFERENCES keywords (id)
    )
    ''')
    
    # 创建标签结果表
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS labels (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        comment_id INTEGER,
        tag_id INTEGER,
        label TEXT CHECK(label IN ('positive', 'negative', 'none')),
        confidence REAL,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (comment_id) REFERENCES comments (id),
        FOREIGN KEY (tag_id) REFERENCES tags (id)
    )
    ''')
    
    conn.commit()
    conn.close()

# 关键词相关操作
def add_keyword(keyword):
    """添加关键词"""
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute('INSERT INTO keywords (keyword) VALUES (?)', (keyword,))
        conn.commit()
        return cursor.lastrowid
    except sqlite3.IntegrityError:
        # 如果关键词已存在，获取其ID
        cursor.execute('SELECT id FROM keywords WHERE keyword = ?', (keyword,))
        return cursor.fetchone()[0]
    finally:
        conn.close()

def get_all_keywords():
    """获取所有关键词"""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT id, keyword FROM keywords')
    result = cursor.fetchall()
    conn.close()
    return result

# 标签对相关操作
def add_tag_pair(positive_tag, negative_tag):
    """添加标签对"""
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute(
            'INSERT INTO tags (positive_tag, negative_tag) VALUES (?, ?)', 
            (positive_tag, negative_tag)
        )
        conn.commit()
        return cursor.lastrowid
    except sqlite3.IntegrityError:
        # 如果标签对已存在，获取其ID
        cursor.execute(
            'SELECT id FROM tags WHERE positive_tag = ? AND negative_tag = ?', 
            (positive_tag, negative_tag)
        )
        return cursor.fetchone()[0]
    finally:
        conn.close()

def get_all_tag_pairs():
    """获取所有标签对"""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT id, positive_tag, negative_tag FROM tags')
    result = cursor.fetchall()
    conn.close()
    return result

# 评论相关操作
def add_comment(keyword_id, content, source_url=None, comment_time=None):
    """添加评论"""
    conn = get_db_connection()
    cursor = conn.cursor()
    if comment_time is None:
        comment_time = datetime.datetime.now()
    cursor.execute(
        'INSERT INTO comments (keyword_id, content, source_url, comment_time) VALUES (?, ?, ?, ?)', 
        (keyword_id, content, source_url, comment_time)
    )
    last_id = cursor.lastrowid
    conn.commit()
    conn.close()
    return last_id

def get_unprocessed_comments(limit=10):
    """获取未处理的评论"""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(
        '''
        SELECT c.id, c.content, c.source_url, k.keyword 
        FROM comments c 
        JOIN keywords k ON c.keyword_id = k.id 
        WHERE c.processed = 0 
        LIMIT ?
        ''', 
        (limit,)
    )
    result = cursor.fetchall()
    conn.close()
    return result

def mark_comment_as_processed(comment_id):
    """标记评论为已处理"""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('UPDATE comments SET processed = 1 WHERE id = ?', (comment_id,))
    conn.commit()
    conn.close()

# 标签结果相关操作
def save_label_result(comment_id, tag_id, label, confidence=1.0):
    """保存标签结果"""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(
        'INSERT INTO labels (comment_id, tag_id, label, confidence) VALUES (?, ?, ?, ?)', 
        (comment_id, tag_id, label, confidence)
    )
    conn.commit()
    conn.close()

def get_label_stats(keyword_id=None):
    """获取标签统计数据"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    if keyword_id:
        query = '''
        SELECT t.id, t.positive_tag, t.negative_tag,
            SUM(CASE WHEN l.label = 'positive' THEN 1 ELSE 0 END) as positive_count,
            SUM(CASE WHEN l.label = 'negative' THEN 1 ELSE 0 END) as negative_count,
            SUM(CASE WHEN l.label = 'none' THEN 1 ELSE 0 END) as none_count
        FROM tags t
        LEFT JOIN labels l ON t.id = l.tag_id
        LEFT JOIN comments c ON l.comment_id = c.id
        WHERE c.keyword_id = ?
        GROUP BY t.id
        '''
        cursor.execute(query, (keyword_id,))
    else:
        query = '''
        SELECT t.id, t.positive_tag, t.negative_tag,
            SUM(CASE WHEN l.label = 'positive' THEN 1 ELSE 0 END) as positive_count,
            SUM(CASE WHEN l.label = 'negative' THEN 1 ELSE 0 END) as negative_count,
            SUM(CASE WHEN l.label = 'none' THEN 1 ELSE 0 END) as none_count
        FROM tags t
        LEFT JOIN labels l ON t.id = l.tag_id
        GROUP BY t.id
        '''
        cursor.execute(query)
    
    result = cursor.fetchall()
    conn.close()
    return result

if __name__ == "__main__":
    init_db() 