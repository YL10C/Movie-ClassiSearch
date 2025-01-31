import React, { useState } from 'react';
import { UserOutlined } from '@ant-design/icons';
import { Button, Input, Card} from 'antd';
import './index.css';



const Search = () => {
    const [query, setQuery] = useState('');
    const [results, setResults] = useState([]);

    const handleSearch = async () => {
        const response = await fetch(`http://localhost:5000/search?query=${query}`);
        const data = await response.json();
        setResults(data);
    };

    return (
        <div>
            <Input  type="text" 
                    size="large" 
                    value={query}
                    onChange={(e) => setQuery(e.target.value)}
                    placeholder="Search TMD Ed" 
                    prefix={<UserOutlined />} /><br/><br/>

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
