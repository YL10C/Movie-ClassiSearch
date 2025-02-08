import TrieSearch from 'trie-search';

let trie = null;

export const fetchMovies = async () => {
  try {
    const response = await fetch('/data/hot_movies_title.json');  
    const data = await response.json();
    if (trie === null) {
      trie = new TrieSearch('title'); 
      data.forEach(title => {
        trie.add({ title });  
      });
      console.log("Trie built successfully!");
    }
    
    return data;  

  } catch (error) {
    console.error("Error fetching movie data:", error);
    return [];
  }
};

export const searchTrie = (searchTerm) => {
  if (trie) {
    const searchResults = trie.get(searchTerm);
    return searchResults.slice(0, 10).map(result => result.title); 
  }
  return [];
};
