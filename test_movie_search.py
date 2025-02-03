import unittest
from movie_search import MovieDatabase

class TestMovieSearch(unittest.TestCase):
    def setUp(self):
        """在每个测试方法之前运行"""
        self.db = MovieDatabase()
        
        # 确保有测试数据
        try:
            self.cursor = self.db.conn.cursor()
            
            # 检查是否已经有数据
            self.cursor.execute("SELECT COUNT(*) FROM movies")
            count = self.cursor.fetchone()[0]
            
            if count == 0:
                # 插入测试数据，使用字符串格式的ID
                self.cursor.execute("""
                    INSERT INTO movies (id, title, director, plot, score) 
                    VALUES 
                    ('tt9999999', 'Test Movie', 'Test Director', 'Test Plot', 5.0)
                """)
                self.db.conn.commit()
        except Exception as e:
            print(f"设置测试数据时出错: {e}")

    def tearDown(self):
        """在每个测试方法之后运行"""
        try:
            # 清理测试数据，使用字符串格式的ID
            self.cursor.execute("DELETE FROM movies WHERE id = 'tt9999999'")
            self.db.conn.commit()
        finally:
            if hasattr(self, 'cursor'):
                self.cursor.close()
            self.db.close()

    def test_parse_query(self):
        """测试查询字符串解析功能"""
        # 测试完整的查询字符串
        query = "title: Avatar director: James Cameron actor: Sam Worthington plot: blue people"
        result = self.db.parse_query(query)
        self.assertEqual(result['title'], 'Avatar')
        self.assertEqual(result['director'], 'James Cameron')
        self.assertEqual(result['actor'], 'Sam Worthington')
        self.assertEqual(result['plot'], 'blue people')

        # 测试部分字段的查询
        query = "title: Inception director: Nolan"
        result = self.db.parse_query(query)
        self.assertEqual(result['title'], 'Inception')
        self.assertEqual(result['director'], 'Nolan')
        self.assertEqual(result['actor'], '')
        self.assertEqual(result['plot'], '')

        # 测试无字段前缀的查询
        query = "Avatar"
        result = self.db.parse_query(query)
        self.assertEqual(result['title'], 'Avatar')
        self.assertEqual(result['director'], '')
        self.assertEqual(result['actor'], '')
        self.assertEqual(result['plot'], '')

    def test_search_movies(self):
        """测试电影搜索功能"""
        # 测试基本搜索
        result = self.db.search_movies("Avatar")
        self.assertIsInstance(result, dict)
        self.assertIn('total', result)
        self.assertIn('results', result)
        self.assertIn('page', result)
        self.assertIn('page_size', result)
        self.assertIn('total_pages', result)

        # 测试多字段搜索 - 使用更通用的测试数据
        test_queries = [
            "title: Star",  # 只测试标题
            "director: Chris",  # 只测试导演
            "actor: Tom",  # 只测试演员
            "plot: love"  # 只测试剧情
        ]
        
        # 至少有一个查询应该返回结果
        found_results = False
        for query in test_queries:
            result = self.db.search_movies(query)
            if len(result['results']) > 0:
                found_results = True
                break
        self.assertTrue(found_results, "没有找到任何匹配的电影，请检查数据库中是否有测试数据")
        
        # 测试分页
        result = self.db.search_movies("a", page=1, page_size=5)  # 使用更通用的查询词
        self.assertLessEqual(len(result['results']), 5)

        # 测试空查询
        result = self.db.search_movies("")
        self.assertIsInstance(result, dict)
        self.assertIn('results', result)

    def test_search_results_structure(self):
        """测试搜索结果的数据结构"""
        result = self.db.search_movies("Avatar")
        if result['results']:
            movie = result['results'][0]
            # 验证返回的电影数据包含所有必要字段
            required_fields = ['id', 'title', 'director', 'plot', 'score', 
                             'release_date', 'poster', 'actors', 'genres']
            for field in required_fields:
                self.assertIn(field, movie)

    def test_edge_cases(self):
        """测试边界情况"""
        # 测试特殊字符
        result = self.db.search_movies("title: Star Wars: Episode IV")
        self.assertIsInstance(result, dict)

        # 测试超大页码
        result = self.db.search_movies("Avatar", page=9999)
        self.assertEqual(len(result['results']), 0)

        # 测试非法页码
        with self.assertRaises(Exception):
            self.db.search_movies("Avatar", page=0)

class TestMovieRecommendations(unittest.TestCase):
    def setUp(self):
        """在每个测试方法之前运行"""
        self.db = MovieDatabase()
        
        # 确保有测试数据
        try:
            self.cursor = self.db.conn.cursor()
            
            # 插入测试电影
            self.cursor.execute("""
                INSERT INTO movies (id, title, director, plot, score, release_date) 
                VALUES 
                ('tt9999991', 'Test Action Movie', 'Test Director 1', 'Test Plot 1', 8.5, '2023-01-01'),
                ('tt9999992', 'Test Drama Movie', 'Test Director 2', 'Test Plot 2', 7.5, '2023-02-01')
            """)
            
            # 插入测试类型
            self.cursor.execute("INSERT IGNORE INTO genres (name) VALUES ('Action'), ('Drama')")
            
            # 获取类型ID
            self.cursor.execute("SELECT id FROM genres WHERE name = 'Action'")
            action_id = self.cursor.fetchone()[0]
            self.cursor.execute("SELECT id FROM genres WHERE name = 'Drama'")
            drama_id = self.cursor.fetchone()[0]
            
            # 关联电影和类型
            self.cursor.execute("""
                INSERT INTO movie_genres (movie_id, genre_id) VALUES 
                ('tt9999991', %s),
                ('tt9999992', %s)
            """, (action_id, drama_id))
            
            self.db.conn.commit()
            
        except Exception as e:
            print(f"设置测试数据时出错: {e}")
            self.db.conn.rollback()

    def tearDown(self):
        """在每个测试方法之后运行"""
        try:
            # 清理测试数据
            self.cursor.execute("DELETE FROM movie_genres WHERE movie_id IN ('tt9999991', 'tt9999992')")
            self.cursor.execute("DELETE FROM movies WHERE id IN ('tt9999991', 'tt9999992')")
            self.db.conn.commit()
        except Exception as e:
            print(f"清理测试数据时出错: {e}")
        finally:
            if hasattr(self, 'cursor'):
                self.cursor.close()
            self.db.close()

    def test_basic_recommendations(self):
        """测试基本推荐功能"""
        result = self.db.get_movie_recommendations()
        self.assertIsInstance(result, dict)
        self.assertIn('total', result)
        self.assertIn('results', result)
        self.assertIn('page', result)
        self.assertIn('page_size', result)
        self.assertIn('total_pages', result)

    def test_category_filter(self):
        """测试类型筛选"""
        # 测试 Action 类型
        result = self.db.get_movie_recommendations(category='Action')
        self.assertTrue(any('Action' in movie['genres'] 
                          for movie in result['results'] if movie['genres']))
        
        # 测试 Drama 类型
        result = self.db.get_movie_recommendations(category='Drama')
        self.assertTrue(any('Drama' in movie['genres'] 
                          for movie in result['results'] if movie['genres']))
        
        # 测试不存在的类型
        result = self.db.get_movie_recommendations(category='NonExistent')
        self.assertEqual(len(result['results']), 0)

    def test_sorting(self):
        """测试排序功能"""
        # 测试按评分排序
        result = self.db.get_movie_recommendations(sort_by='score')
        scores = [movie['score'] for movie in result['results'] if movie['score'] is not None]
        self.assertEqual(scores, sorted(scores, reverse=True))
        
        # 测试按日期排序
        result = self.db.get_movie_recommendations(sort_by='date')
        dates = [movie['release_date'] for movie in result['results'] if movie['release_date']]
        self.assertEqual(dates, sorted(dates, reverse=True))
        
        # 测试组合排序
        result = self.db.get_movie_recommendations(sort_by='score,date')
        self.assertIsInstance(result, dict)

    def test_pagination(self):
        """测试分页功能"""
        # 测试第一页
        result = self.db.get_movie_recommendations(page=1, page_size=1)
        self.assertLessEqual(len(result['results']), 1)
        
        # 测试第二页
        result = self.db.get_movie_recommendations(page=2, page_size=1)
        self.assertLessEqual(len(result['results']), 1)
        
        # 测试页大小
        result = self.db.get_movie_recommendations(page_size=5)
        self.assertLessEqual(len(result['results']), 5)

    def test_result_structure(self):
        """测试返回结果的数据结构"""
        result = self.db.get_movie_recommendations()
        if result['results']:
            movie = result['results'][0]
            required_fields = ['id', 'title', 'director', 'plot', 'score', 
                             'release_date', 'poster', 'actors', 'genres']
            for field in required_fields:
                self.assertIn(field, movie)

if __name__ == '__main__':
    unittest.main(verbosity=2) 