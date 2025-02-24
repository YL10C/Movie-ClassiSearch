def load_index(self, file_path):
    """
    从文件加载倒排索引
    :param file_path: 文件路径
    """
    with open(file_path, 'r', encoding='utf-8') as file:
        current_field = None
        current_term = None
        for line in file:
            line = line.strip()
            if line and not line.startswith('\t'):  # 处理字段和术语行
                parts = line.split(':', 1)  # 只分割第一个冒号
                current_field = parts[0].strip()
                current_term = parts[1].strip()
                print(f"Loaded field: {current_field}, term: {current_term}")  # Debugging line
            elif line.startswith('\t') and current_field is not None and current_term is not None:  # 处理文档ID和位置行
                doc_id, positions_str = line.split(':', 1)
                positions = list(map(int, positions_str.split(',')))
                print(f"Loaded doc_id: {doc_id.strip()}, positions: {positions}")  # Debugging line
                self.index[current_field][current_term][doc_id.strip()].extend(positions)  # 合并位置列表