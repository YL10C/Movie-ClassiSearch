from collections import defaultdict
import json

class PositionalInvertedIndex:
    def __init__(self):
        # 初始化倒排索引，支持多字段
        self.index = defaultdict(lambda: defaultdict(lambda: defaultdict(list)))

    def build_index(self, documents):
        """
        构建多字段的倒排索引
        :param documents: 预处理后的文档字典，格式为 {doc_id: {field: [tokens]}}
        """
        for doc_id, fields in documents.items():
            for field, tokens in fields.items():
                for pos, token in enumerate(tokens):
                    # {field: {token: {doc_id: [pos]}}}
                    self.index[field][token][doc_id].append(pos)

    def save_index(self, file_path):
        """
        将倒排索引保存到文件
        :param file_path: 文件路径
        """
        with open(file_path, 'a', encoding='utf-8') as file:  # 使用'a'模式追加内容
            # {field: {term: {doc_id: [pos]}}}
            for field, terms in self.index.items():
                for term, doc_dict in terms.items():
                    file.write(f"{field}:{term}\n")
                    for doc_id, positions in doc_dict.items():
                        positions_str = ','.join(map(str, positions))
                        file.write(f"\t{doc_id}: {positions_str}\n")

    def load_index(self, file_path):
        """
        从文件加载倒排索引
        :param file_path: 文件路径
        """
        with open(file_path, 'r', encoding='utf-8') as file:
            current_field = None
            current_term = None
            for line in file:
                if line and not line.startswith('\t'):  # 处理字段和术语行
                    parts = line.split(':', 1)  # 只分割第一个冒号
                    current_field = parts[0].strip()
                    current_term = parts[1].strip()
                elif line.startswith('\t'):  # 处理文档ID和位置行
                    doc_id, positions_str = line.split(':', 1)
                    positions = list(map(int, positions_str.split(',')))
                    self.index[current_field][current_term][doc_id.strip()].extend(positions)  # 合并位置列表 