import re
import json
from nltk.stem import PorterStemmer
from nltk.corpus import stopwords
from collections import defaultdict
import nltk

# 确保下载nltk的停用词数据集
# nltk.download('stopwords')

class TextPreprocessor:
    def __init__(self, remove_stop_words=True, apply_stemming=True):
        """
        初始化文本预处理器
        :param remove_stop_words: 是否移除停用词
        :param apply_stemming: 是否应用词干提取
        """
        self.remove_stop_words = remove_stop_words  # true or false
        self.apply_stemming = apply_stemming  # true or false
        # 使用nltk的停用词
        self.stop_words = set(stopwords.words('english')) if remove_stop_words else set()
        # 创建词干提取器
        self.stemmer = PorterStemmer() if apply_stemming else None

    def process_text(self, text):
        """
        处理文本，进行分词、去停用词和词干提取
        :param text: 输入文本
        :return: 处理后的词汇列表
        """
        if text is None:
            return "未读取到文本"  # 或者其他默认值
        
        text = re.sub(r'-', ' ', text)  # 替换连字符为空格
        tokens = re.findall(r'\b\w+\b', text.lower())  # 提取单词
        if self.remove_stop_words:
            tokens = [token for token in tokens if token not in self.stop_words]  # 去停用词
        if self.apply_stemming:
            tokens = [self.stemmer.stem(token) for token in tokens]  # 词干提取
        return tokens

    def process_file(self, file_path):
        """
        处理文件，根据文件类型调用相应的处理方法
        :param file_path: 文件路径
        :return: 处理后的文档字典
        """
        if file_path.endswith('.jsonl'):
            return self.process_jsonl_file(file_path)
        elif file_path.endswith('.json'):
            return self.process_json_file(file_path)
        else:
            raise ValueError("Unsupported file type. Use 'json' or 'jsonl'.")

    def process_jsonl_file(self, jsonl_file_path):
        """
        处理JSONL文件，提取文档信息
        :param jsonl_file_path: JSONL文件路径
        :return: 预处理后的文档字典，格式为 {doc_id: {field: [tokens]}}
        """
        documents = {}
        with open(jsonl_file_path, 'r', encoding='utf-8') as infile:
            for line in infile:
                document = json.loads(line.strip())  # 解析JSON行
                doc_id = document['id']  # 获取文档ID
                fields = {
                    'title': self.process_text(document['title']),  # 处理标题
                    'director': self.process_text(document['director']),  # 处理导演
                    'cast': self.process_text(', '.join(document['cast_character'].keys())),  # 处理演员
                    'plot': self.process_text(document['plot']),  # 处理剧情
                }
                documents[doc_id] = fields  # 将处理后的字段存入文档字典
        return documents 

    def process_json_file(self, json_file_path):
        """
        处理JSON文件，提取文档信息
        :param json_file_path: JSON文件路径
        :return: 预处理后的文档字典，格式为 {doc_id: {field: [tokens]}}
        """
        documents = {}
        with open(json_file_path, 'r', encoding='utf-8') as infile:
            data = json.load(infile)  # 解析整个JSON文件
            for document in data:
                doc_id = document['id']  # 获取文档ID
                fields = {
                    'title': self.process_text(document['title']),  # 处理标题
                    'director': self.process_text(document['director']),  # 处理导演
                    'cast': self.process_text(', '.join(document['cast_character'].keys())),  # 处理演员
                    'plot': self.process_text(document['plot']),  # 处理剧情
                }
                documents[doc_id] = fields  # 将处理后的字段存入文档字典
        return documents 