from typing import Dict, Any, List
from database import Database

class MovieRecommendations:
    def __init__(self, db: Database):
        self.db = db

    def get_recommendations(self, 
                          category: str = None, 
                          sort_by: str = 'score', 
                          page: int = 1, 
                          page_size: int = 20) -> Dict[str, Any]:
        """获取电影推荐"""
        # ... (get_movie_recommendations 方法的实现保持不变)

    def get_genres(self) -> List[str]:
        """获取所有电影类型"""
        self.db.cursor.execute("SELECT DISTINCT name FROM genres ORDER BY name")
        return [row['name'] for row in self.db.cursor.fetchall()] 