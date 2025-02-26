import mysql.connector
from typing import Dict, Any
import logging

# 配置日志记录
logger = logging.getLogger(__name__)

class Database:
    """数据库连接类，用于管理与 MySQL 数据库的连接和操作。"""
    
    def __init__(self):
        """初始化数据库连接并确保必要的全文索引存在。"""
        self.conn = mysql.connector.connect(
            host='localhost',
            user='root',
            password='Cyl200124@',
            database='movie_search',
            buffered=True
        )
        self.cursor = self.conn.cursor(dictionary=True)
        self._ensure_fulltext_indexes()

    def close(self):
        """关闭数据库连接和游标。"""
        self.cursor.close()
        self.conn.close()

    def _ensure_fulltext_indexes(self):
        """确保必要的全文索引存在，以提高搜索性能。"""
        try:
            # 检查 movies 表的全文索引
            self.cursor.execute("""
                SELECT INDEX_NAME 
                FROM information_schema.STATISTICS 
                WHERE TABLE_SCHEMA = 'movie_search' 
                AND TABLE_NAME = 'movies' 
                AND INDEX_NAME = 'idx_title_plot'
            """)
            
            if not self.cursor.fetchone():
                # 如果不存在，则创建全文索引
                self.cursor.execute("""
                    ALTER TABLE movies 
                    ADD FULLTEXT INDEX idx_title_plot (title, plot)
                """)
                
            # 检查 actors 表的全文索引
            self.cursor.execute("""
                SELECT INDEX_NAME 
                FROM information_schema.STATISTICS 
                WHERE TABLE_SCHEMA = 'movie_search' 
                AND TABLE_NAME = 'actors' 
                AND INDEX_NAME = 'idx_actor_name'
            """)
            
            if not self.cursor.fetchone():
                # 如果不存在，则创建全文索引
                self.cursor.execute("""
                    ALTER TABLE actors 
                    ADD FULLTEXT INDEX idx_actor_name (name)
                """)
                
            self.conn.commit()
        except mysql.connector.Error as err:
            logger.error(f"创建索引时出错: {err}") 