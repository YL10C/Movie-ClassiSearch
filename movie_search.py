from flask import Flask, request, jsonify
from typing import List, Dict, Any
import mysql.connector
import re
from datetime import datetime
from flask_cors import CORS
import logging

app = Flask(__name__)
CORS(app)  # 启用CORS支持

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class MovieDatabase:
    def __init__(self):
        self.conn = mysql.connector.connect(
            host='localhost',
            user='root',
            password='Cyl200124@',
            database='movie_search'
        )
        self.cursor = self.conn.cursor(dictionary=True)

    def close(self):
        self.cursor.close()
        self.conn.close()

    def parse_query(self, query: str) -> Dict[str, str]:
        """解析用户输入的查询字符串"""
        fields = {
            'title': '',
            'director': '',
            'actor': '',
            'plot': ''
        }
        
        patterns = {
            'title': r'title:\s*(.+?)(?=\s+director:|actor:|plot:|$)',
            'director': r'director:\s*(.+?)(?=\s+title:|actor:|plot:|$)',
            'actor': r'actor:\s*(.+?)(?=\s+director:|title:|plot:|$)',
            'plot': r'plot:\s*(.+?)(?=\s+director:|title:|actor:|$)'
        }
        
        for field, pattern in patterns.items():
            match = re.search(pattern, query, re.IGNORECASE)
            if match:
                fields[field] = match.group(1).strip()
                query = query.replace(match.group(0), '').strip()
        
        if query and not any(fields.values()):
            fields['title'] = query
        
        return fields


    def search_movies(self, query: str, page: int = 1, page_size: int = 50) -> Dict[str, Any]:
        """
        搜索电影
        query: 用户输入的查询字符串
        page: 当前页码
        page_size: 每页显示的电影数量
        return: 包含电影列表和分页信息的字典
        """
        parsed_query = self.parse_query(query)
        offset = (page - 1) * page_size
        


        base_sql = """
            SELECT DISTINCT 
                movies.id,
                movies.title,
                movies.director,
                movies.plot,
                movies.score,
                movies.release_date,
                movies.poster,
                GROUP_CONCAT(DISTINCT actors.name) as actors,
                GROUP_CONCAT(DISTINCT genres.name) as genres,
                (
                    CASE 
                        WHEN movies.title LIKE %s THEN 4
                        ELSE 0 
                    END +
                    CASE 
                        WHEN movies.director LIKE %s THEN 3
                        ELSE 0 
                    END +
                    CASE 
                        WHEN movies.plot LIKE %s THEN 2
                        ELSE 0 
                    END
                ) as relevance
            FROM movies
            LEFT JOIN movie_cast ON movies.id = movie_cast.movie_id
            LEFT JOIN actors ON movie_cast.actor_id = actors.id
            LEFT JOIN movie_genres ON movies.id = movie_genres.movie_id
            LEFT JOIN genres ON movie_genres.genre_id = genres.id
            WHERE 1=1
        """
        
        params = []
        where_clauses = []
        
        if parsed_query['title']:
            where_clauses.append("movies.title LIKE %s")
            params.append(f"%{parsed_query['title']}%")
        
        if parsed_query['director']:
            where_clauses.append("movies.director LIKE %s")
            params.append(f"%{parsed_query['director']}%")
        
        if parsed_query['actor']:
            where_clauses.append("actors.name LIKE %s")
            params.append(f"%{parsed_query['actor']}%")
        
        if parsed_query['plot']:
            where_clauses.append("movies.plot LIKE %s")
            params.append(f"%{parsed_query['plot']}%")
        
        if where_clauses:
            base_sql += " AND " + " AND ".join(where_clauses)
        
        # 计算总数的SQL
        count_sql = """
            SELECT COUNT(DISTINCT movies.id) as total 
            FROM movies
            LEFT JOIN movie_cast ON movies.id = movie_cast.movie_id
            LEFT JOIN actors ON movie_cast.actor_id = actors.id
            LEFT JOIN movie_genres ON movies.id = movie_genres.movie_id
            LEFT JOIN genres ON movie_genres.genre_id = genres.id
            WHERE 1=1
        """
        
        if where_clauses:
            count_sql += " AND " + " AND ".join(where_clauses)
        
        # 添加分组和排序
        base_sql += """
            GROUP BY movies.id
            ORDER BY relevance DESC, movies.score DESC
            LIMIT %s OFFSET %s
        """
        
        # 添加评分参数
        score_params = [
            f"%{parsed_query['title']}%" if parsed_query['title'] else '%',
            f"%{parsed_query['director']}%" if parsed_query['director'] else '%',
            f"%{parsed_query['plot']}%" if parsed_query['plot'] else '%'
        ]
        
        # 执行计数查询
        self.cursor.execute(count_sql, params)
        total = self.cursor.fetchone()['total']
        
        # 执行主查询
        all_params = score_params + params + [page_size, offset]
        self.cursor.execute(base_sql, all_params)
        results = self.cursor.fetchall()
        
        # 处理日期格式
        for movie in results:
            if movie['release_date']:
                movie['release_date'] = movie['release_date'].strftime('%Y-%m-%d')
        
        return {
            'total': total,
            'page': page,
            'page_size': page_size,
            'total_pages': (total + page_size - 1) // page_size,
            'results': results
        }

    def get_movie_recommendations(self, 
                                category: str = None, 
                                sort_by: str = 'score', 
                                page: int = 1, 
                                page_size: int = 20) -> Dict[str, Any]:
        """获取电影推荐"""
        offset = (page - 1) * page_size
        
        base_sql = """
            SELECT DISTINCT 
                movies.id,
                movies.title,
                movies.director,
                movies.plot,
                movies.score,
                movies.release_date,
                movies.poster,
                GROUP_CONCAT(DISTINCT actors.name) as actors,
                GROUP_CONCAT(DISTINCT genres.name) as genres
            FROM movies
            LEFT JOIN movie_cast ON movies.id = movie_cast.movie_id
            LEFT JOIN actors ON movie_cast.actor_id = actors.id
            LEFT JOIN movie_genres ON movies.id = movie_genres.movie_id
            LEFT JOIN genres ON movie_genres.genre_id = genres.id
            WHERE 1=1
        """
        
        params = []
        
        if category:
            base_sql += " AND genres.name = %s"
            params.append(category)
        
        # 构建排序条件
        sort_conditions = []
        for sort_field in sort_by.split(','):
            if sort_field == 'score':
                sort_conditions.append('movies.score DESC')
            elif sort_field == 'date':
                sort_conditions.append('movies.release_date DESC')
        
        if not sort_conditions:
            sort_conditions = ['movies.score DESC']
        
        # 计算总数
        count_sql = """
            SELECT COUNT(DISTINCT movies.id) as total 
            FROM movies
            LEFT JOIN movie_cast ON movies.id = movie_cast.movie_id
            LEFT JOIN actors ON movie_cast.actor_id = actors.id
            LEFT JOIN movie_genres ON movies.id = movie_genres.movie_id
            LEFT JOIN genres ON movie_genres.genre_id = genres.id
            WHERE 1=1
        """
        
        if category:
            count_sql += " AND genres.name = %s"
        
        # 执行计数查询
        self.cursor.execute(count_sql, params)
        total = self.cursor.fetchone()['total']
        
        # 添加分组和排序
        base_sql += f"""
            GROUP BY movies.id
            ORDER BY {', '.join(sort_conditions)}
            LIMIT %s OFFSET %s
        """
        
        # 执行主查询
        all_params = params + [page_size, offset]
        self.cursor.execute(base_sql, all_params)
        results = self.cursor.fetchall()
        
        # 处理日期格式
        for movie in results:
            if movie['release_date']:
                movie['release_date'] = movie['release_date'].strftime('%Y-%m-%d')
        
        return {
            'total': total,
            'page': page,
            'page_size': page_size,
            'total_pages': (total + page_size - 1) // page_size,
            'results': results
        }

    def get_genres(self) -> List[str]:
        """获取所有电影类型"""
        self.cursor.execute("SELECT DISTINCT name FROM genres ORDER BY name")
        return [row['name'] for row in self.cursor.fetchall()]

    def _ensure_fulltext_indexes(self):
        """确保必要的全文索引存在"""
        try:
            # 检查索引是否存在
            self.cursor.execute("""
                SELECT INDEX_NAME 
                FROM information_schema.STATISTICS 
                WHERE TABLE_SCHEMA = 'movie_search' 
                AND TABLE_NAME = 'movies' 
                AND INDEX_NAME = 'idx_title_plot'
            """)
            
            if not self.cursor.fetchone():
                # 为movies表添加全文索引
                self.cursor.execute("""
                    ALTER TABLE movies 
                    ADD FULLTEXT INDEX idx_title_plot (title, plot)
                """)
                
            self.cursor.execute("""
                SELECT INDEX_NAME 
                FROM information_schema.STATISTICS 
                WHERE TABLE_SCHEMA = 'movie_search' 
                AND TABLE_NAME = 'actors' 
                AND INDEX_NAME = 'idx_actor_name'
            """)
            
            if not self.cursor.fetchone():
                # 为actors表添加全文索引
                self.cursor.execute("""
                    ALTER TABLE actors 
                    ADD FULLTEXT INDEX idx_actor_name (name)
                """)
                
            self.conn.commit()
        except mysql.connector.Error as err:
            logger.error(f"创建索引时出错: {err}")

# 创建数据库连接池
db = MovieDatabase()

# 搜索电影
@app.route('/api/search', methods=['GET'])
def search():
    try:
        query = request.args.get('query', '')
        page = int(request.args.get('page', 1))
        page_size = int(request.args.get('page_size', 50))
        
        results = db.search_movies(query, page, page_size)
        return jsonify(results)
    except Exception as e:
        logger.error(f"Search error: {str(e)}")
        return jsonify({'error': str(e)}), 500

# 获取电影推荐
@app.route('/api/movies', methods=['GET'])
def get_movies():
    try:
        category = request.args.get('category')
        sort_by = request.args.get('sort_by', 'score')
        page = int(request.args.get('page', 1))
        page_size = int(request.args.get('page_size', 20))
        
        results = db.get_movie_recommendations(category, sort_by, page, page_size)
        return jsonify(results)
    except Exception as e:
        logger.error(f"Get movies error: {str(e)}")
        return jsonify({'error': str(e)}), 500

# 获取所有电影类型
@app.route('/api/genres', methods=['GET'])
def get_genres():
    try:
        genres = db.get_genres()
        return jsonify({'genres': genres})
    except Exception as e:
        logger.error(f"Get genres error: {str(e)}")
        return jsonify({'error': str(e)}), 500

# 错误处理
@app.errorhandler(404)
def not_found(error):
    return jsonify({'error': 'Not found'}), 404

# 内部服务器错误处理
@app.errorhandler(500)
def internal_error(error):
    return jsonify({'error': 'Internal server error'}), 500

if __name__ == '__main__':
    app.run(debug=True, port=5000) 