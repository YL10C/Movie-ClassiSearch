from collections import defaultdict
from flask import Flask, request, jsonify
from flask_cors import CORS
import logging
from SearchModule.models import TFIDFRetrieval
from database import Database
from movie_search import MovieSearch
from SearchModule.search import QueryProcessor
from SearchModule.preprocessor import TextPreprocessor
from SearchModule.indexer import PositionalInvertedIndex

# 配置日志系统
# 设置日志级别为INFO，格式默认为：级别:日志器名称:消息
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)  # 获取当前模块的日志记录器

# 初始化Flask应用
app = Flask(__name__)
CORS(app)  # 启用CORS支持，允许跨域请求

# 初始化数据库和服务模块
db = Database()  # 创建数据库连接实例
movie_search = MovieSearch(db)  # 电影搜索服务

# 初始化搜索相关组件（在Flask应用初始化之后）
search_preprocessor = TextPreprocessor(remove_stop_words=True, apply_stemming=True)
index = PositionalInvertedIndex() 
index.load_index('D:\OneDrive\文档\Yilin\Edinburgh\Text Technologies\Movie-ClassiSearch\SearchModule\index.txt')
query_processor = QueryProcessor(
    preprocessor=search_preprocessor,
    index=index
)
# 创建统一的检索索引（合并所有字段）
retrieval_index = defaultdict(lambda: defaultdict(list))

# 遍历多字段索引结构 {field: {term: {docID: [positions]}}}
for field, terms in index.index.items():
    for term, doc_dict in terms.items():
        for doc_id, positions in doc_dict.items():
            # 将不同字段的相同term合并到统一索引
            retrieval_index[term][doc_id].extend(positions)

# 创建TF-IDF检索对象
retrieval = TFIDFRetrieval(retrieval_index, search_preprocessor)

@app.route('/api/search', methods=['GET'])
def search():
    """处理电影搜索请求
    参数：
    - query: 搜索关键词
    - page: 分页页码（默认1）
    - page_size: 每页结果数（默认50）
    """
    try:
        # 从URL参数获取请求参数
        query = request.args.get('query', '')
        page = int(request.args.get('page', 1))
        page_size = int(request.args.get('page_size', 50))
        
        # 调用搜索服务获取结果
        results = movie_search.search_movies(query, page, page_size)
        return jsonify(results)  # 将结果转换为JSON格式返回
    except Exception as e:
        logger.error(f"Search error: {str(e)}")
        return jsonify({'error': str(e)}), 500  # 返回错误信息和500状态码

@app.route('/api/movies', methods=['GET'])
def get_movies():
    """获取电影推荐列表
    参数：
    - category: 电影分类/类型
    - sort_by: 排序方式（默认按评分）
    - page: 分页页码（默认1）
    - page_size: 每页结果数（默认20）
    """
    try:
        category = request.args.get('category')
        sort_by = request.args.get('sort_by', 'score')
        page = int(request.args.get('page', 1))
        page_size = int(request.args.get('page_size', 20))
        
        # 调用推荐服务获取结果
        results = movie_search.get_movie_recommendations(category, sort_by, page, page_size)
        return jsonify(results)
    except Exception as e:
        logger.error(f"Get movies error: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/genres', methods=['GET'])
def get_genres():
    """获取所有电影类型列表"""
    try:
        genres = movie_search.get_genres()
        return jsonify({'genres': genres})  # 包装为JSON对象返回
    except Exception as e:
        logger.error(f"Get genres error: {str(e)}")
        return jsonify({'error': str(e)}), 500

# 在现有路由之后添加新的搜索端点
@app.route('/api/v2/search', methods=['GET'])
def advanced_search():
    """高级搜索接口"""
    try:
        query = request.args.get('query', '')
        if not query:
            return jsonify({'error': 'Missing required parameter: query'}), 400

        page = int(request.args.get('page', 1))
        page_size = int(request.args.get('page_size', 10))
        
        # 判断搜索类型
        has_advanced = any(
            field in query for field in ['title:', 'director:', 'plot:', 'cast:']
        ) or any(
            op in query.upper() for op in [' AND ', ' OR ']
        ) or '"' in query

        # 获取原始结果（ID列表）
        if has_advanced:
            raw_results = query_processor.query(query)  # 返回ID列表
        else:
            # 使用普通搜索获取ID列表
            retrieval_results = retrieval.compute_tfidf_scores(query)
            raw_results = [result[0] for result in retrieval_results]

        # 统一获取详细信息
        if raw_results:
            # 使用单个SQL查询获取所有详细信息
            placeholders = ','.join(['%s'] * len(raw_results))
            sql = f"""
                SELECT movies.*, 
                    GROUP_CONCAT(DISTINCT actors.name) as actors,
                    GROUP_CONCAT(DISTINCT genres.name) as genres
                FROM movies
                LEFT JOIN movie_cast ON movies.id = movie_cast.movie_id
                LEFT JOIN actors ON movie_cast.actor_id = actors.id
                LEFT JOIN movie_genres ON movies.id = movie_genres.movie_id
                LEFT JOIN genres ON movie_genres.genre_id = genres.id
                WHERE movies.id IN ({placeholders})
                GROUP BY movies.id
                ORDER BY movies.score DESC
            """
            db.cursor.execute(sql, tuple(raw_results))
            results = db.cursor.fetchall()
        else:
            results = []
        
        # 统一分页处理
        total = len(results)
        start = (page - 1) * page_size
        end = start + page_size
        paginated_results = results[start:end]

        # 处理日期格式
        for movie in paginated_results:
            if movie['release_date']:
                movie['release_date'] = movie['release_date'].strftime('%Y-%m-%d')

        return jsonify({
            'total': total,
            'page': page,
            'page_size': page_size,
            'total_pages': (total + page_size - 1) // page_size,
            'results': paginated_results
        })
        
    except Exception as e:
        logger.error(f"Advanced search error: {str(e)}")
        return jsonify({'error': str(e)}), 500

# 错误处理handler
@app.errorhandler(404)
def not_found(error):
    """处理404未找到错误"""
    return jsonify({'error': 'Not found'}), 404

@app.errorhandler(500)
def internal_error(error):
    """处理500服务器内部错误"""
    return jsonify({'error': 'Internal server error'}), 500

# 主程序入口
if __name__ == '__main__':
    # 启动Flask开发服务器
    # debug=True：启用调试模式（生产环境应关闭）
    # port=5000：指定监听端口
    app.run(debug=True, port=5000) 