import React, { useState, useEffect } from 'react';
import { UserOutlined } from '@ant-design/icons';
import { Button, Input, Card, AutoComplete} from 'antd';
import './index.css';
import { fetchMovies, searchTrie } from '../../util/trie_auto';



const Search = () => {
    const [query, setQuery] = useState('');
    const [results, setResults] = useState([]);
    const [suggestions, setSuggestions] = useState([]);

    useEffect(() => {
        const loadData = async () => {
        await fetchMovies(); 
        };
        loadData();
    }, []);

    const handleSearch = async () => {
        console.log(query);
        const response = await fetch(`http://127.0.0.1:5000/search?query=${query}`);
        const data = await response.json();
        setResults(data);
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
    }
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

            <Button type="primary" onClick={handleSearch}>TMD Search</Button><br/>

            <ul>
                {results.map((movie, index) => (
                    <Card key={index} className='card'>
                        <img src={movie.poster} className="img" /><br/>
                        <div className="card-content">
                            <a
                            href={movie.url}
                            target="_blank"
                            rel="noopener noreferrer"
                            className="card-title">
                            {movie.title}</a>
                            <p className="card-date">{movie.release_date}</p>
                            <p className="card-plot">{movie.plot}</p>
                        </div>
                    </Card>
            ))}
            </ul>
        </div>
    );
};

export default Search;
