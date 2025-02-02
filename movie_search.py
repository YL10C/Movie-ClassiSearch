import mysql.connector
import re
from typing import List, Dict, Any

class MovieSearchEngine:
    def __init__(self):
        self.conn = mysql.connector.connect(
            host='localhost',
            user='root',
            password='Cyl200124@',
            database='movie_search'
        )
        self.cursor = self.conn.cursor(dictionary=True)
        self._ensure_fulltext_indexes()

    def _ensure_fulltext_indexes(self):
        """确保必要的全文索引存在"""
        try:
            # 为movies表添加全文索引
            self.cursor.execute("""
                ALTER TABLE movies 
                ADD FULLTEXT INDEX idx_movie_search (title, plot)
            """)
            
            # 为actors表添加全文索引
            self.cursor.execute("""
                ALTER TABLE actors 
                ADD FULLTEXT INDEX idx_actor_name (name)
            """)
            
            self.conn.commit()
        except mysql.connector.Error:
            # 索引可能已经存在，忽略错误
            pass

    def parse_query(self, query: str) -> Dict[str, str]:
        """解析用户输入的查询字符串"""
        fields = {
            'title': '',
            'director': '',
            'actor': '',
            'plot': ''
        }
        
        # 使用正则表达式匹配字段模式
        patterns = {
            'title': r'title:\s*([^:]+)(?=\s+\w+:|$)',
            'director': r'director:\s*([^:]+)(?=\s+\w+:|$)',
            'actor': r'actor:\s*([^:]+)(?=\s+\w+:|$)',
            'plot': r'plot:\s*([^:]+)(?=\s+\w+:|$)'
        }
        
        # 提取指定的字段
        for field, pattern in patterns.items():
            match = re.search(pattern, query, re.IGNORECASE)
            if match:
                fields[field] = match.group(1).strip()
                # 从查询字符串中移除已匹配的部分
                query = query.replace(match.group(0), '').strip()
        
        # 如果还有剩余的查询文本，将其作为title搜索
        if query and not any(fields.values()):
            fields['title'] = query
        
        return fields

    def search(self, query: str, limit: int = 50) -> List[Dict[str, Any]]:
        """执行搜索并返回结果"""
        parsed_query = self.parse_query(query)
        
        # 构建搜索SQL
        sql = """
            SELECT DISTINCT 
                m.id,
                m.title,
                m.director,
                m.plot,
                m.score,
                m.release_date,
                GROUP_CONCAT(DISTINCT a.name) as actors,
                GROUP_CONCAT(DISTINCT g.name) as genres,
                (
                    CASE 
                        WHEN MATCH(m.title) AGAINST(%s IN BOOLEAN MODE) THEN 4
                        ELSE 0 
                    END +
                    CASE 
                        WHEN m.director LIKE %s THEN 3
                        ELSE 0 
                    END +
                    CASE 
                        WHEN MATCH(m.plot) AGAINST(%s IN BOOLEAN MODE) THEN 2
                        ELSE 0 
                    END
                ) as relevance
            FROM movies m
            LEFT JOIN movie_cast mc ON m.id = mc.movie_id
            LEFT JOIN actors a ON mc.actor_id = a.id
            LEFT JOIN movie_genres mg ON m.id = mg.movie_id
            LEFT JOIN genres g ON mg.genre_id = g.id
            WHERE 1=1
        """
        
        params = []
        where_clauses = []
        
        # 添加标题搜索条件
        if parsed_query['title']:
            where_clauses.append("MATCH(m.title) AGAINST(%s IN BOOLEAN MODE)")
            params.append(f"*{parsed_query['title']}*")
        
        # 添加导演搜索条件
        if parsed_query['director']:
            where_clauses.append("m.director LIKE %s")
            params.append(f"%{parsed_query['director']}%")
        
        # 添加演员搜索条件
        if parsed_query['actor']:
            where_clauses.append("a.name LIKE %s")
            params.append(f"%{parsed_query['actor']}%")
        
        # 添加剧情搜索条件
        if parsed_query['plot']:
            where_clauses.append("MATCH(m.plot) AGAINST(%s IN BOOLEAN MODE)")
            params.append(f"*{parsed_query['plot']}*")
        
        # 添加WHERE子句
        if where_clauses:
            sql += " AND " + " AND ".join(where_clauses)
        
        # 添加分组和排序
        sql += """
            GROUP BY m.id
            ORDER BY relevance DESC, m.score DESC
            LIMIT %s
        """
        params.extend([parsed_query['title'] or '', 
                      f"%{parsed_query['director']}%" if parsed_query['director'] else '%',
                      parsed_query['plot'] or '',
                      limit])
        
        # 执行查询
        self.cursor.execute(sql, params)
        results = self.cursor.fetchall()
        
        return results

    def close(self):
        """关闭数据库连接"""
        self.cursor.close()
        self.conn.close()

# 使用示例
if __name__ == "__main__":
    search_engine = MovieSearchEngine()
    try:
        # 测试查询
        query = input("请输入搜索条件（例如 title: Avatar director: Cameron）: ")
        results = search_engine.search(query)
        
        print(f"\n找到 {len(results)} 个结果：")
        for movie in results:
            print(f"\n标题: {movie['title']}")
            print(f"导演: {movie['director']}")
            print(f"演员: {movie['actors']}")
            print(f"类型: {movie['genres']}")
            print(f"评分: {movie['score']}")
            print(f"上映日期: {movie['release_date']}")
            print(f"相关度: {movie['relevance']}")
            print("-" * 50)
            
    finally:
        search_engine.close() 