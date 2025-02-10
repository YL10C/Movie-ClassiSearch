import React, { useState, useEffect } from "react";
import { Select, Pagination, Card } from "antd";
import "./index.css";

const { Option } = Select;

const Movies = () => {
  const [genres, setGenres] = useState([]); // 保存电影类型
  const [movies, setMovies] = useState([]); // 保存电影数据
  const [total, setTotal] = useState(0); // 总电影数量
  const [currentPage, setCurrentPage] = useState(1); // 当前页码
  const [total_pages, setTotalPages] = useState(0); // 总页数
  const [showPagination, setShowPagination] = useState(false);
  const [pageSize, setPageSize] = useState(20); // 每页显示电影数
  const [selectedGenre, setSelectedGenre] = useState(""); // 当前选择的类型
  const [sortBy, setSortBy] = useState("score"); // 当前排序方式

  // 获取电影类型列表
  useEffect(() => {
    const fetchGenres = async () => {
      try {
        const response = await fetch("http://localhost:5000/api/genres");
        const data = await response.json();
        setGenres(data.genres);
      } catch (error) {
        console.error("Failed to fetch genres:", error);
      }
    };

    fetchGenres();
  }, []);

  // 获取电影列表
  const fetchMovies = async (page = 1, genre = "", sort = "score") => {
    try {
      const response = await fetch(
        `http://localhost:5000/api/movies?category=${genre}&sort_by=${sort}&page=${page}&page_size=${pageSize}`
      );
      const data = await response.json();
      setMovies(data.results);
      setTotal(data.total);
      setTotalPages(data.total_pages);
      setCurrentPage(page);
    } catch (error) {
      console.error("Failed to fetch movies:", error);
    }
  };

  // 初次加载电影数据
  useEffect(() => {
    fetchMovies();
  }, []);

  // 处理类型筛选
  const handleGenreChange = (value) => {
    setSelectedGenre(value);
    fetchMovies(1, value, sortBy);
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
  const startIndex = (currentPage - 1) * pageSize;
  const endIndex = startIndex + pageSize;
  const currentMovies = movies.slice(startIndex, endIndex);

  return (
    <div className="movies-container">
      <h2>Todays Movies</h2>
      <div className="filters">
        <Select
          className="filter-select"
          placeholder="Generes"
          onChange={handleGenreChange}
          defaultValue="all"
        >
          <Option value="all">All</Option>
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
           defaultValue="none"
        >
            <Option value="none">None</Option>
          <Option value="score">Score</Option>
          <Option value="date">Date</Option>
        </Select>
      </div>

      <div className="movies-list">
        {currentMovies.map((movie, index) => (
                            <Card key={index} className='card'>
                                <img src={movie.poster} className="img" /><br/>
                                <div className="card-content">
                                    <a
                                        href={movie.url}
                                        target="_blank"
                                        rel="noopener noreferrer"
                                        className="card-title">
                                        {movie.title}
                                    </a>
                                    <p className="card-date">{movie.release_date}</p>
                                    <p className="card-plot">{movie.plot}</p>
                                </div>
                            </Card>
        ))}
      </div>

      <Pagination
                      className="movies-pagination"
                      current={currentPage}
                      pageSize={pageSize}
                      total={total_pages}
                      onChange={handlePageChange}
                      showSizeChanger={false}
                  />
    </div>
  );
};

export default Movies;