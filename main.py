def search(query: str, query_processor: QueryProcessor, page: int = 1, page_size: int = 10) -> list:
    """执行电影搜索的通用方法（更新版）
    参数:
        query (str): 用户输入的查询字符串
        query_processor (QueryProcessor): 查询处理器实例
        page (int): 当前页码
        page_size (int): 每页结果数
    返回:
        list: 分页后的搜索结果列表
    """
    # 判断查询类型
    if any(field in query for field in ['title:', 'director:', 'plot:', 'cast:']) or \
       any(op in query for op in ['AND', 'OR']) or \
       '"' in query:
        # 执行复杂查询
        full_results = query_processor.query(query)
    else:
        # 执行简单查询
        full_results = simple_search(query)
    
    # 执行分页
    start = (page - 1) * page_size
    end = start + page_size
    return full_results[start:end]

def simple_search(query: str) -> list:
    """处理简单查询（优化版）"""
    # 这里添加实际的数据库查询逻辑
    # 示例：return db.query("SELECT * FROM movies WHERE title LIKE %s", [f"%{query}%"])
    return [{"id": 1, "title": "示例电影", "score": 8.5}] 