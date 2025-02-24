def test_load_index():
    # 创建倒排索引对象
    index = PositionalInvertedIndex()
    
    # 加载现有索引
    index.load_index('Index&Search&Retrieval\\index.txt')
    
    # 检查索引是否成功加载
    title_index = index.index.get('title')
    plot_index = index.index.get('plot')
    
    # 打印结果以验证
    print("Title Index:", title_index)
    print("Plot Index:", plot_index)
    
    # 进行简单的断言检查
    assert title_index is not None, "Title index should not be None"
    assert plot_index is not None, "Plot index should not be None"
    
    # 检查特定术语是否存在
    assert 'taitoru' in title_index, "Expected term 'taitoru' not found in title index"
    assert 'kyozetsu' in title_index, "Expected term 'kyozetsu' not found in title index"
    assert 'some_plot_term' in plot_index, "Expected term 'some_plot_term' not found in plot index"  # 替换为实际的术语 