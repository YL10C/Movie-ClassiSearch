from collections import defaultdict
from preprocessor import TextPreprocessor
from indexer import PositionalInvertedIndex
from search import QueryProcessor
from models import TFIDFRetrieval

#movie_search/
#│
#├── main.py                # 主程序入口
#├── indexer.py             # 索引构建模块
#├── search.py              # 搜索模块
#├── preprocessor.py        # 文本预处理模块
#├── models.py              # 检索模型（TF-IDF, BM25）
#└── utils.py               # 工具函数

def search(query: str, query_processor: QueryProcessor) -> list:
    """执行电影搜索的通用方法
    参数:
        query (str): 用户输入的查询字符串
        query_processor (QueryProcessor): 查询处理器
    返回:
        list: 搜索结果列表
    """
    
    # 判断查询类型
    if any(field in query for field in ['title:', 'director:', 'plot:', 'cast:']) or \
       any(op in query for op in ['AND', 'OR']) or \
       '"' in query:
        # 执行复杂查询
        return query_processor.query(query)
    else:
        # 执行retrieval
        return []



if __name__ == "__main__":
    # 创建文本预处理对象
    preprocessor = TextPreprocessor(
        remove_stop_words=True,  # 使用nltk的停用词
        apply_stemming=True
    )

    # 创建倒排索引对象
    index = PositionalInvertedIndex()

    # 依次处理2018-2024年的JSON文件
    # for year in range(2018, 2024):
    #     file_path = f'sample/{year}_sample.jsonl'
    #     try:
    #         # 处理每年的JSON文件
    #         documents = preprocessor.process_file(file_path)
    #         # 构建索引
    #         index.build_index(documents)
    #         print(f"已处理 {year} 年的数据")
    #     except FileNotFoundError:
    #         print(f"未找到 {year} 年的数据文件")
    #         continue

    documents = preprocessor.process_file(f'sample/2024_sample.json')
    # index.build_index(documents)
    # # 保存完整的索引到文件
    # index.save_index('SearchModule\\index.txt')
    # 加载现有索引
    index.load_index('SearchModule\\index.txt')

    # 创建统一的检索索引（合并所有字段）
    retrieval_index = defaultdict(lambda: defaultdict(list))
    
    # 遍历多字段索引结构 {field: {term: {docID: [positions]}}}
    for field, terms in index.index.items():
        for term, doc_dict in terms.items():
            for doc_id, positions in doc_dict.items():
                # 将不同字段的相同term合并到统一索引
                retrieval_index[term][doc_id].extend(positions)

    # 创建TF-IDF检索对象
    retrieval = TFIDFRetrieval(retrieval_index, preprocessor)

    # 创建查询处理对象
    query_processor = QueryProcessor(index, preprocessor)

    # 简单普通查询示例
    simple_query = r'Taitoru, kyozetsu Follows a group'
    
    # 判断查询语句是否包含字段限定符、布尔运算符或引号
    if any(field in simple_query for field in ['title:', 'director:', 'plot:', 'cast:']) or \
       any(op in simple_query for op in ['AND', 'OR']) or \
       '"' in simple_query:
        simple_results = query_processor.query(simple_query)
        print("简单查询结果:", simple_results)
    else:
        retrieval_results = retrieval.compute_tfidf_scores(simple_query)
        print("TF-IDF检索结果:", retrieval_results)

