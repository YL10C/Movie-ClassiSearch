import os
from flask import Flask, request, jsonify
from flask_cors import CORS
import json


app = Flask(__name__)
CORS(app)


#DataBase
# json example
# json file path
base_dir = os.path.dirname(os.path.abspath(__file__))
file_path = os.path.join(base_dir, '../ttdsData', '2024_sample.json')

try:
    with open(file_path, 'r', encoding='utf-8') as file:
        data = json.load(file)
except FileNotFoundError:
    print(f"文件 {file_path} 未找到。")
except json.JSONDecodeError:
    print(f"文件 {file_path} 不是有效的JSON格式。")

@app.route('/api/search', methods=['GET'])
def search():
    query = request.args.get('query', '')
    results = {'results': []}
    for movie in data:
        if query in movie['title']:
            movie['url'] = 'https://www.imdb.com/title/' + movie['id']
            results['results'].append(movie)
    results['total'] = len(results['results'])
    results['page'] = 1
    results['page_size'] = 20
    results['total_pages'] = len(results['results']) // 20 + 1
    
    return results

@app.route('/api/movies', methods=['GET'])
def get_movies():
    query = request.args.get('query', '')
    results = {'results': []}
    for movie in data:
        if query in movie['title']:
            movie['url'] = 'https://www.imdb.com/title/' + movie['id']
            results['results'].append(movie)
    results['total'] = len(results['results'])
    results['page'] = 1
    results['page_size'] = 20
    results['total_pages'] = len(results['results']) // 20 + 1
    
    return results

@app.route('/api/genres', methods=['GET'])
def get_genres():
    results = {
            "genres": [
                "Action",
                "Comedy",
                "Drama",
            ]
            }
    
    return results

if __name__ == '__main__':
    app.run(debug=True)