import React, { useState, useEffect} from 'react';
import { Input, Button, Card, Pagination ,AutoComplete} from 'antd';
import { UserOutlined } from '@ant-design/icons';
import './index.css';
import { fetchMovies, searchTrie } from '../../util/trie_auto';

const Search = ({onSearch}) => {
    const [query, setQuery] = useState('');
    const [searchResults, setSearchResults] = useState({ results: [], total: 0, page_size: 10 });
    const [suggestions, setSuggestions] = useState([]);
    const [showPagination, setShowPagination] = useState(false);
    const [currentPage, setCurrentPage] = useState(1);


    useEffect(() => {
        const loadData = async () => {
        await fetchMovies(); 
        };
        loadData();
    }, []);

    const handleSearch = async (page = 1) => {
        const response = await fetch(`http://localhost:5000/api/search?query=${query}&page=${page}&page_size=${searchResults.page_size}`);
        if (query.trim()) {
            onSearch(); // when searching, hide Movies
          }

        const data = await response.json();
        setSearchResults(data);
        setCurrentPage(page);
        setShowPagination(true);
    };

    const handleAutoComplete = (value) => {
            const newQuery = value;
            setQuery(newQuery); 
            const trieResults = searchTrie(newQuery); 
            console.log(trieResults)
            const filteredSuggestions = trieResults.map(movie => (
                {   value: movie, 
                    label: (
                    <span>
                    {movie.split(new RegExp(`(${value})`, 'gi')).map((part, index) =>
                        part.toLowerCase() === value.toLowerCase() ? (
                        <span key={index} style={{ backgroundColor: 'yellow' }}>{part}</span>
                        ) : (
                        part
                        )
                    )}
                    </span>
            ), }));  
            setSuggestions(filteredSuggestions); 
          };
        
    const handleSelect = (value) =>{
        setQuery(value); 
    };

    const handlePageChange = (page) => {
        handleSearch(page);
    };

    // 计算当前页显示的结果
    const startIndex = (currentPage - 1) * searchResults.page_size;
    const endIndex = startIndex + searchResults.page_size;
    const currentResults = searchResults.results.slice(startIndex, endIndex);

    return (
        <div>
            <AutoComplete  type="text" 
                                style={{
                                    width: "80vw"
                                  }}
                                onSearch={handleAutoComplete}
                                onSelect={handleSelect}
                                options={suggestions}
                                placeholder="Search TMD Ed" 
                                prefix={<UserOutlined />} />
                        <br/><br/>

            <Button type="primary" onClick={() => handleSearch(1)}>TMD Search</Button><br/>

            <ul>
                {currentResults.map((movie, index) => (
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
            </ul>
            {showPagination && (<Pagination
                className="pagination-container"
                current={currentPage}
                pageSize={searchResults.page_size}
                total={searchResults.total}
                onChange={handlePageChange}
                showSizeChanger={false}
            />
            )}
        </div>
    );
};

export default Search;