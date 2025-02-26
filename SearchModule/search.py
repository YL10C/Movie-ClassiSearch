import re
from collections import defaultdict
import unittest

class QueryProcessor:
    def __init__(self, index, preprocessor):
        self.index = index.index  # 多字段倒排索引结构 {field: {term: {doc_id: [pos]}}}
        self.preprocessor = preprocessor
        self.supported_fields = ['title', 'plot', 'cast', 'director']
        self.default_field = 'title'

    def query(self, query_str):
        """重构后的主查询方法"""
        clauses, operators = self.split_boolean_expression(query_str)
        
        # 没有运算符的情况
        if not operators:
            return self.parse_query(clauses[0])
        
        # 处理所有子查询
        results = [self.parse_query(clause) for clause in clauses]
        
        # 按运算符顺序合并结果
        while operators:
            op = operators.pop(0)
            a = results.pop(0)
            b = results.pop(0)
            results.insert(0, a & b if op == 'AND' else a | b)
        
        return results[0]

    def parse_query(self, query):
        """解析查询的入口方法"""
        # 处理字段限定的短语查询
        for field in self.supported_fields:
            pattern = re.compile(rf'{field}:\s*"([^"]+)"', flags=re.IGNORECASE)
            match = pattern.search(query)
            if match:
                phrase = match.group(1)
                return self.phrase_search(phrase, target_field=field)
        
        # 处理普通字段查询
        if ':' in query:
            field, term_part = query.split(':', 1)
            field = field.strip().lower()
            term_part = term_part.strip()
            if field in self.supported_fields:
                return self.process_field_query(field, term_part)
        
        # 处理未限定的短语查询
        if '"' in query:
            phrase = query.strip('"')
            return self.phrase_search(phrase)
        
        # 默认处理为普通查询
        return self.process_single_term(query)

    def split_boolean_expression(self, query):
        """精确分割布尔表达式为子查询和运算符"""
        # 使用正则表达式匹配运算符（区分大小写）
        pattern = re.compile(r'\s+(AND|OR)\s+')
        parts = pattern.split(query)
        
        # 分离子查询和运算符
        clauses = []
        operators = []
        for i, part in enumerate(parts):
            if i % 2 == 0:
                clauses.append(part.strip())
            else:
                operators.append(part.strip().upper())
        
        return clauses, operators

    def process_single_clause(self, clause):
        """处理单个查询子句"""
        # 处理字段限定的短语查询
        for field in self.supported_fields:
            pattern = re.compile(rf'{field}:\s*"([^"]+)"', flags=re.IGNORECASE)
            match = pattern.search(clause)
            if match:
                phrase = match.group(1)
                return self.phrase_search(phrase, target_field=field)
        
        # 处理普通字段查询
        if ':' in clause:
            field, term_part = clause.split(':', 1)
            field = field.strip().lower()
            term_part = term_part.strip()
            if field in self.supported_fields:
                return self.process_field_query(field, term_part)
        
        # 处理未限定的短语查询
        if '"' in clause:
            phrase = clause.strip('"')
            return self.phrase_search(phrase)
        
        # 处理简单的普通查询（没有字段和冒号）
        processed_terms = self.preprocessor.process_text(clause)
        results = set()
        
        # 在所有支持的字段中查找同时包含所有词项的文档
        for field in self.supported_fields:
            field_results = set()
            for term in processed_terms:
                if term in self.index[field]:
                    field_results.update(self.index[field][term].keys())
            # 只保留同时包含所有词项的文档
            if results:
                results.intersection_update(field_results)
            else:
                results = field_results
        
        return results

    def process_field_query(self, field, query_part):
        """处理字段限定的普通查询"""
        # 处理可能存在的AND/OR逻辑
        if ' AND ' in query_part:
            terms = query_part.split(' AND ')
            results = set()
            for term in terms:
                results.update(self.process_single_term(f"{field}:{term}"))
            return results
        elif ' OR ' in query_part:
            terms = query_part.split(' OR ')
            results = set()
            for term in terms:
                results.update(self.process_single_term(f"{field}:{term}"))
            return results
        else:
            return self.process_single_term(f"{field}:{query_part}")

    def process_single_term(self, term):
        """处理单个查询项（可能包含字段限定）"""
        if ':' in term:
            field, term = term.split(':', 1)
            field = field.strip().lower()
            term = term.strip()
        else:
            field = self.default_field
            term = term.strip()

        # 预处理查询词
        processed_terms = self.preprocessor.process_text(term)
        results = set()
        
        # 在指定字段中搜索所有处理后的词项
        for t in processed_terms:
            if field in self.index and t in self.index[field]:
                results.update(self.index[field][t].keys())
        return results

    def phrase_search(self, phrase, target_field=None):
        """增强的短语搜索，支持指定字段"""
        terms = self.preprocessor.process_text(phrase)
        if len(terms) < 1:
            return set()

        found_docs = set()
        # 如果指定了目标字段
        if target_field:
            candidates = self.get_phrase_candidates(target_field, terms)
            for doc_id, positions_list in candidates.items():
                if self.check_phrase_positions(positions_list):
                    found_docs.add(doc_id)
        else:
            # 跨所有字段搜索
            for field in self.supported_fields:
                candidates = self.get_phrase_candidates(field, terms)
                for doc_id, positions_list in candidates.items():
                    if self.check_phrase_positions(positions_list):
                        found_docs.add(doc_id)
        return found_docs

    def get_phrase_candidates(self, field, terms):
        """获取包含所有词项的候选文档"""
        candidates = defaultdict(list)
        
        # 检查第一个词项的存在性
        first_term = terms[0]
        if field not in self.index or first_term not in self.index[field]:
            return {}

        # 遍历包含第一个词项的文档
        for doc_id, positions in self.index[field][first_term].items():
            valid = True
            all_positions = [positions]
            
            # 检查后续词项
            for term in terms[1:]:
                if (field not in self.index or 
                    term not in self.index[field] or 
                    doc_id not in self.index[field][term]):
                    valid = False
                    break
                all_positions.append(self.index[field][term][doc_id])
            
            if valid:
                candidates[doc_id] = all_positions
        return candidates

    def check_phrase_positions(self, positions_list):
        """验证位置连续性"""
        # 计算词项的数量
        term_count = len(positions_list)
        
        # 创建一个集合来存储所有位置
        position_set = set()
        
        # 遍历每个词项的位置列表
        for i, positions in enumerate(positions_list):
            # 将每个位置调整并添加到集合中
            for pos in positions:
                position_set.add(pos + (term_count - 1 - i))
        
        # 如果集合的大小等于所有位置的总数，则说明有重叠
        return len(position_set) < sum(len(pos) for pos in positions_list)