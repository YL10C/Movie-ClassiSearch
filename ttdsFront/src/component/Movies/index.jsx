import React, { useState, useEffect } from "react";
import { Select, Pagination, Card } from "antd";
import "./index.css";

const { Option } = Select;

const Movies = () => {
  // 修改genres为静态的5个常见类型
  const [genres] = useState(["Action", "Adventure", "Comedy", "Drama", "Horror"]);
  const [movies, setMovies] = useState([]); // 保存电影数据
  const [total, setTotal] = useState(0); // 总电影数量
  const [currentPage, setCurrentPage] = useState(1); // 当前页码
  const [total_pages, setTotalPages] = useState(0); // 总页数
  const [showPagination, setShowPagination] = useState(false);
  const [pageSize, setPageSize] = useState(20); // 每页显示电影数
  const [selectedGenre, setSelectedGenre] = useState(""); // 当前选择的类型
  const [sortBy, setSortBy] = useState("score"); // 当前排序方式

  // 获取电影列表
  const fetchMovies = async (page = 1, genre = "", sort = "score") => {
    try {
      const safeGenre = genre || "all";
      const safeSort = sort || "score";
      
      // 方式1：直接使用绝对路径
      const filePath = `/static/genre_movies/${safeGenre}_${safeSort}.json`;
      
      // 方式2：使用Vite环境变量
      // const filePath = `${import.meta.env.BASE_URL}static/genre_movies/${safeGenre}_${safeSort}.json`;

      const response = await fetch(filePath);
      
      if (!response.ok) throw new Error(`Failed to load ${filePath}`);
      
      const data = await response.json();
      
      // 分页切片逻辑
      const startIndex = (page - 1) * pageSize; // 计算起始索引
      const endIndex = startIndex + pageSize;   // 计算结束索引
      
      // 对results数组进行切片
      setMovies(data.results.slice(startIndex, endIndex));
      
      // 设置分页相关状态
      setTotal(data.results.length); // 总电影数为数组长度
      setCurrentPage(page);
      
    } catch (error) {
      console.error("Failed to fetch movies:", error);
      // 可以添加错误状态提示
      setMovies([]);
      setTotal(0);
    }
  };

  // 初次加载电影数据
  useEffect(() => {
    fetchMovies();
  }, []);

  // 处理类型筛选
  const handleGenreChange = (value) => {
    const actualValue = value === "all" ? "" : value; // 将"all"转换为空字符串
    setSelectedGenre(actualValue);
    fetchMovies(1, actualValue, sortBy);  // 传递转换后的值
  };

  // 处理排序方式更改
  const handleSortChange = (value) => {
    setSortBy(value);
    fetchMovies(1, selectedGenre, value);
  };

  // 处理页码更改
  const handlePageChange = (page) => {
    fetchMovies(page, selectedGenre, sortBy);
  };

  // 计算当前页显示的结果
  // const startIndex = (currentPage - 1) * pageSize;
  // const endIndex = startIndex + pageSize;
  // const currentMovies = movies.slice(startIndex, endIndex);

  return (
    <div className="movies-container">
      <h2>Todays Movies</h2>
      <div className="filters">
        <Select
          className="filter-select"
          placeholder="Generes"
          onChange={handleGenreChange}
          defaultValue=""
        >
          <Option value="">All</Option>
          {genres.map((genre) => (
            <Option key={genre} value={genre}>
              {genre}
            </Option>
          ))}
        </Select>
        <Select
          className="filter-select"
          placeholder="Sort By"
          onChange={handleSortChange}
           defaultValue="score"
        >
          <Option value="score">Score</Option>
          <Option value="date">Date</Option>
        </Select>
      </div>

      <div className="movies-list">
        {movies.map((movie, index) => (
                            <Card key={index} className='movie-card'>
                                <img src={movie.poster} className="movie-poster" /><br/>
                                <div className="movie-content">
                                    <a
                                        href={`https://www.imdb.com/title/${movie.id}/`}
                                        target="_blank"
                                        rel="noopener noreferrer"
                                        className="movie-title">
                                        {movie.title}
                                    </a>
                                    <p className="movie-date">{movie.release_date}</p>
                                    <p className="movie-plot">{movie.plot}</p>
                                </div>
                            </Card>
        ))}
      </div>

      <Pagination
                      className="movies-pagination"
                      current={currentPage}
                      pageSize={pageSize}
                      total={total}
                      onChange={handlePageChange}
                      showSizeChanger={false}
                  />
    </div>
  );
};

export default Movies;