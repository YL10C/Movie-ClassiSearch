from flask import Flask, request, jsonify
from flask_cors import CORS
import logging
from database import Database
from movie_search import MovieSearch
from movie_recommendations import MovieRecommendations

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)
CORS(app)

# 创建数据库连接和服务实例
db = Database()
movie_search = MovieSearch(db)
movie_recommendations = MovieRecommendations(db)

@app.route('/api/search', methods=['GET'])
def search():
    try:
        query = request.args.get('query', '')
        page = int(request.args.get('page', 1))
        page_size = int(request.args.get('page_size', 50))
        
        results = movie_search.search_movies(query, page, page_size)
        return jsonify(results)
    except Exception as e:
        logger.error(f"Search error: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/movies', methods=['GET'])
def get_movies():
    try:
        category = request.args.get('category')
        sort_by = request.args.get('sort_by', 'score')
        page = int(request.args.get('page', 1))
        page_size = int(request.args.get('page_size', 20))
        
        results = movie_recommendations.get_recommendations(category, sort_by, page, page_size)
        return jsonify(results)
    except Exception as e:
        logger.error(f"Get movies error: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/genres', methods=['GET'])
def get_genres():
    try:
        genres = movie_recommendations.get_genres()
        return jsonify({'genres': genres})
    except Exception as e:
        logger.error(f"Get genres error: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.errorhandler(404)
def not_found(error):
    return jsonify({'error': 'Not found'}), 404

@app.errorhandler(500)
def internal_error(error):
    return jsonify({'error': 'Internal server error'}), 500

if __name__ == '__main__':
    app.run(debug=True, port=5000) 