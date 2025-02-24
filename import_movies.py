import json
import mysql.connector
from datetime import datetime

# 解析日期
def parse_release_date(date_str):
    if date_str is None or date_str == '':
        return None
    try:
        # 去掉括号和额外文本
        date_str = date_str.split(' (')[0]
        # 解析日期
        date_obj = datetime.strptime(date_str, '%b %d, %Y')
        # 格式化为 YYYY-MM-DD
        return date_obj.strftime('%Y-%m-%d')
    except ValueError:
        return None  # 如果日期格式不合法，返回 None

# 解析 num_votes
def parse_num_votes(num_votes):
    if num_votes is None or num_votes == '':
        return None  # 或者返回 0
    num_votes = num_votes.upper()  # 转换为大写
    if 'K' in num_votes:
        return int(float(num_votes.replace('K', '')) * 1000)
    elif 'M' in num_votes:
        return int(float(num_votes.replace('M', '')) * 1000000)
    else:
        return int(num_votes)

try:
    # 读取 JSON 文件
    with open('./sample/2019_sample.json', 'r', encoding='utf-8') as file:
        data = json.load(file)

    # 连接到 MySQL 数据库
    conn = mysql.connector.connect(
        host='localhost',
        user='root',
        password='Cyl200124@',
        database='movie_search',
        buffered=True
    )
    cursor = conn.cursor()

    # 开始事务
    conn.start_transaction()

    for movie in data:
        try:
            # 首先检查电影是否已存在
            cursor.execute("SELECT id FROM movies WHERE id = %s", (movie.get('id'),))
            if cursor.fetchone():
                print(f"电影 '{movie.get('title')}' (ID: {movie.get('id')}) 已存在，跳过...")
                continue

            # 解析 release_date 和 num_votes
            release_date = parse_release_date(movie.get('release_date'))
            num_votes = parse_num_votes(movie.get('num_votes'))

            # 插入电影表
            cursor.execute("""
                INSERT INTO movies (id, title, poster, plot, score, num_votes, director, release_date, aka, quotes)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """, (
                movie.get('id'),
                movie.get('title'),
                movie.get('poster'),
                movie.get('plot'),
                movie.get('score'),
                num_votes,
                movie.get('director'),
                release_date,
                movie.get('aka'),
                movie.get('quotes')
            ))

            # 插入类型表
            for genre in movie.get('genres', []):
                if genre:  # 确保类型不为空
                    cursor.execute("INSERT IGNORE INTO genres (name) VALUES (%s)", (genre,))
                    cursor.execute("SELECT id FROM genres WHERE name = %s", (genre,))
                    genre_id = cursor.fetchone()[0]
                    # 检查电影-类型关联是否已存在
                    cursor.execute("INSERT IGNORE INTO movie_genres (movie_id, genre_id) VALUES (%s, %s)", 
                                 (movie['id'], genre_id))

            # 插入国家表
            for country in movie.get('countries', []):
                if country:  # 确保国家不为空
                    cursor.execute("INSERT IGNORE INTO countries (name) VALUES (%s)", (country,))
                    cursor.execute("SELECT id FROM countries WHERE name = %s", (country,))
                    country_id = cursor.fetchone()[0]
                    # 检查电影-国家关联是否已存在
                    cursor.execute("INSERT IGNORE INTO movie_countries (movie_id, country_id) VALUES (%s, %s)", 
                                 (movie['id'], country_id))

            # 插入语言表
            for language in movie.get('languages', []):
                if language:  # 确保语言不为空
                    cursor.execute("INSERT IGNORE INTO languages (name) VALUES (%s)", (language,))
                    cursor.execute("SELECT id FROM languages WHERE name = %s", (language,))
                    language_id = cursor.fetchone()[0]
                    # 检查电影-语言关联是否已存在
                    cursor.execute("INSERT IGNORE INTO movie_languages (movie_id, language_id) VALUES (%s, %s)", 
                                 (movie['id'], language_id))

            # 插入演员表
            for actor, character in movie.get('cast_character', {}).items():
                if actor and actor.strip():  # 确保演员名不为空
                    cursor.execute("INSERT IGNORE INTO actors (name) VALUES (%s)", (actor.strip(),))
                    cursor.execute("SELECT id FROM actors WHERE name = %s", (actor.strip(),))
                    actor_id = cursor.fetchone()[0]
                    # 检查电影-演员关联是否已存在
                    cursor.execute("""
                        INSERT IGNORE INTO movie_cast (movie_id, actor_id, character_name) 
                        VALUES (%s, %s, %s)
                    """, (movie['id'], actor_id, character.strip() if character else None))

            print(f"成功导入电影 '{movie.get('title')}' (ID: {movie.get('id')})")

        except mysql.connector.Error as err:
            print(f"处理电影 {movie.get('title')} 时出错: {err}")
            continue

    # 提交事务
    conn.commit()
    print("数据导入成功！")

except Exception as e:
    print(f"发生错误: {e}")
    if 'conn' in locals():
        conn.rollback()
        print("已回滚所有更改")

finally:
    # 关闭连接
    if 'cursor' in locals():
        cursor.close()
    if 'conn' in locals():
        conn.close()
    print("数据库连接已关闭")