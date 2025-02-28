import React, { useState } from "react";
import Search from "./component/Search";
import Movies from "./component/Movies";

import "./App.css";

const App = () => {
  const [showMovies, setShowMovies] = useState(true); // 控制 Movies 是否显示

  const isSearch = () => {
    setShowMovies(false); // 当搜索时隐藏 Movies
  };


  return (
    <div>
      <h1>Ed TMD </h1>
      <Search onSearch={isSearch} />
      {showMovies && <Movies />} {/* 根据 showMovies 显示或隐藏 Movies */}
    </div>
  );
};

export default App;