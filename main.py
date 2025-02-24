if __name__ == "__main__":
    # 创建文本预处理对象
    preprocessor = TextPreprocessor(
        remove_stop_words=True,  # 使用nltk的停用词
        apply_stemming=True
    )

    # 创建倒排索引对象
    index = PositionalInvertedIndex()

    # 加载现有索引
    index.load_index('Index&Search&Retrieval\\test_index.txt')
    print(index.index['title'])

    # 运行测试
    # test_load_index() 