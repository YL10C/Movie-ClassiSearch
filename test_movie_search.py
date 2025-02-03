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

if __name__ == '__main__':
    unittest.main(verbosity=2) 