from preprocessor import TextPreprocessor
from indexer import PositionalInvertedIndex
from search import QueryProcessor

#movie_search/
#│
#├── main.py                # 主程序入口
#├── indexer.py             # 索引构建模块
#├── search.py              # 搜索模块
#├── preprocessor.py        # 文本预处理模块
#├── models.py              # 检索模型（TF-IDF, BM25）
#└── utils.py               # 工具函数

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

    # documents = preprocessor.process_file(f'sample/2024_sample.json')
    # index.build_index(documents)
    # # 保存完整的索引到文件
    # index.save_index('Index&Search&Retrieval\\index.txt')
    # 加载现有索引
    index.load_index('Index&Search&Retrieval\\index.txt')

    # 创建查询处理对象
    query_processor = QueryProcessor(index, preprocessor)

    # # 简单普通查询示例
    # simple_query = r'title:Can\'t Escape AND "young artist becomes"'
    
    # # 判断查询语句是否包含字段限定符、布尔运算符或引号
    # if any(field in simple_query for field in ['title:', 'director:', 'plot:', 'cast:']) or \
    #    any(op in simple_query for op in ['AND', 'OR']) or \
    #    '"' in simple_query:
    #     simple_results = query_processor.query(simple_query)
    #     print("简单查询结果:", simple_results)
    # else:
    #     print("查询语句不包含有效的字段或运算符。")