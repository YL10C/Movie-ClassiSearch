import math
from collections import defaultdict

class RankedRetrieval:
    def __init__(self, index, documents):
        """
        初始化排名检索对象
        :param index: 倒排索引对象
        :param documents: 文档字典，格式为 {doc_id: [tokens]}
        """
        self.index = index.index  # 获取倒排索引
        self.documents = documents  # 存储文档
        self.N = len(documents)  # 文档总数

    def compute_tfidf_scores(self, query):
        """
        计算给定查询的TF-IDF得分
        :param query: 查询字符串
        :return: 排序后的文档得分列表
        """
        query_terms = query.split()  # 将查询字符串分词
        doc_scores = defaultdict(float)  # 存储文档得分

        for term in query_terms:
            if term in self.index:  # 如果词在索引中
                postings = self.index[term]  # 获取该词的倒排列表
                for doc_id in postings.keys():
                    doc_scores[doc_id] += 1  # 简化的TF计算，统计词频

        # 按得分降序排序，返回得分前的文档
        sorted_doc_scores = sorted(doc_scores.items(), key=lambda x: x[1], reverse=True)
        return sorted_doc_scores 