import re
import xml.etree.ElementTree as ET
from nltk.stem import PorterStemmer
from collections import defaultdict
import math

# Preprocessing module
# Parses txt or xml files, generates a dictionary of documents
class TextPreprocessor:
    def __init__(self, stop_words_file=None, remove_stop_words=True, apply_stemming=True):
        self.remove_stop_words = remove_stop_words
        self.apply_stemming = apply_stemming

        # Load stop words list (if needed)
        if self.remove_stop_words and stop_words_file:
            self.stop_words = self.load_stop_words(stop_words_file)
        else:
            self.stop_words = set()

        # Create PorterStemmer object (if needed)
        if self.apply_stemming:
            self.stemmer = PorterStemmer()

    # Load stop words list from file at once
    def load_stop_words(self, stop_words_file):
        with open(stop_words_file, 'r', encoding='utf-8') as file:
            stop_words = set(file.read().strip().splitlines())
            stop_words = {word.strip().lower() for word in stop_words}
        return stop_words

    # Method to preprocess text
    def process_text(self, text):
        text = re.sub(r'-', ' ', text)
        text = re.sub(r"'s\b", '', text)
        # text = re.sub(r"'", '', text)

        tokens = re.findall(r'\b\w+\b', text)
        tokens = [token.lower() for token in tokens]

        if self.remove_stop_words:
            tokens = [token for token in tokens if token not in self.stop_words]
        
        if self.apply_stemming:
            tokens = [self.stemmer.stem(token) for token in tokens]

        return tokens

    # Process XML files
    def process_xml_file(self, xml_file_path):
        tree = ET.parse(xml_file_path)
        root = tree.getroot()

        documents = {}
        for doc in root.findall('DOC'):
            doc_id = doc.find('DOCNO').text.strip()

            # Handle <HEADLINE> element, ensure it exists
            headline_element = doc.find('HEADLINE')
            headline = headline_element.text.strip() if headline_element is not None and headline_element.text else ""

            # Handle <TEXT> element, ensure it exists
            text_element = doc.find('TEXT') if doc.find('TEXT') is not None else doc.find('Text')
            text = text_element.text.strip() if text_element is not None and text_element.text else ""

            # Combine headline and text for preprocessing
            full_text = headline + " " + text
            tokens = self.process_text(full_text)
            documents[doc_id] = tokens

        return documents


    # Process TXT files
    def process_txt_file(self, input_file_path):
        documents = {}
        with open(input_file_path, 'r', encoding='utf-8') as infile:
            doc_id = None
            headline = ""
            text = ""
            for line in infile:
                line = line.strip()
                
                if line.startswith("ID:"):
                    if doc_id is not None:  # Save the previous document
                        full_text = headline + " " + text
                        tokens = self.process_text(full_text)
                        documents[doc_id] = tokens
                        
                    doc_id = line.split(":", 1)[1].strip()
                    headline = ""
                    text = ""

                elif line.startswith("HEADLINE:"):
                    # Split only at the first ":"
                    headline = line.split(":", 1)[1].strip()

                elif line.startswith("TEXT:"):
                    text = line.split(":", 1)[1].strip()

                else:
                    text += " " + line

            # Save the last document
            if doc_id is not None:
                full_text = headline + " " + text
                tokens = self.process_text(full_text)
                documents[doc_id] = tokens

        return documents

    # Unified method to process files
    def process_file(self, file_path, file_type='txt'):
        if file_type.lower() == 'txt':
            return self.process_txt_file(file_path)
        elif file_type.lower() == 'xml':
            return self.process_xml_file(file_path)
        else:
            raise ValueError("Unsupported file type. Use 'txt' or 'xml'.")

# Index building module
# Generate an index of type defaultdict{defaultdict{doc_id:list}} using documents
class PositionalInvertedIndex:
    def __init__(self):
        # Initialize inverted index as a nested dictionary in the format:
        # {term: {doc_id: [positions]}}
        self.index = defaultdict(lambda: defaultdict(list))
    
    # Build positional inverted index
    def build_index(self, documents):
        """
        Build positional inverted index
        :param documents: Preprocessed documents dictionary in the format {doc_id: [tokens]}
        """
        for doc_id, tokens in documents.items():
            for pos, token in enumerate(tokens):  # Create iterator over tokens
                # Record the positions where the term occurs in the corresponding document's inverted index
                self.index[token][doc_id].append(pos)

    # Query the inverted index
    def query(self, term, preprocessor=None):
        """
        Query information of a term in the inverted index
        :param term: The term to query
        :param preprocessor: TextPreprocessor object for preprocessing the query term
        :return: Returns a dictionary containing documents and positions where the term appears, in the format {doc_id: [positions]}
        """
        if preprocessor:
            # Preprocess the query term (lowercasing, stemming, etc.)
            term = preprocessor.process_text(term)[0]  # After preprocessing, returns a list; take the first element
        return self.index.get(term, {})
    
    # Save the index to a file
    def save_index(self, file_path):
        """
        Save the inverted index to a file
        :param file_path: File path to save the index
        """
        with open(file_path, 'w', encoding='utf-8') as file:
            for term, doc_dict in self.index.items():
                df = len(doc_dict)  # Document frequency, indicating how many documents the term appears in
                file.write(f"{term}:{df}\n")  # Term and document frequency
                for doc_id, positions in doc_dict.items():
                    positions_str = ','.join(map(str, positions))  # Convert position information to string
                    file.write(f"\t{doc_id}: {positions_str}\n")  # Indent document ID and position information

    # Load the index from a file
    def load_index(self, file_path):
        """
        Load the inverted index from a file
        :param file_path: Index file path
        """
        self.index = defaultdict(lambda: defaultdict(list))
        with open(file_path, 'r', encoding='utf-8') as file:
            current_term = None
            for line in file:
                line = line.strip()
                
                # Determine if it's a term line, i.e., contains term:df format
                if ": " not in line:  # Term line
                    parts = line.split(":")
                    current_term = parts[0].strip()  # Term, removing possible spaces
                    # df = parts[1].strip()  # Document frequency, though not used here
                    # print(f"Loaded term: {current_term}, Document Frequency: {df}")  # Debug output
                elif current_term is not None:
                    # Process document ID and position line
                    doc_id, positions_str = line.split(":")
                    positions = list(map(int, positions_str.split(',')))
                    self.index[current_term][doc_id.strip()] = positions


class QueryProcessor:
    def __init__(self, index, preprocessor=None):
        self.index = index.index  # Inverted index
        self.preprocessor = preprocessor  # Preprocessor object

    def query(self, query_str):
        """
        General query method, parses the query string and executes the corresponding query method
        :param query_str: Query string
        :return: Returns a set of document IDs matching the query results
        """
        # Call the parsing method to execute the corresponding query based on input format
        return self.parse_query(query_str)

    def parse_query(self, query):
        """
        Parse the query, recognizing Boolean, phrase, and proximity searches
        :param query: User input query string
        :return: Calls different query methods based on the query type
        """
        # 1. Extract phrase queries and replace with placeholders
        phrase_matches = re.findall(r'"([^"]+)"', query)
        phrase_placeholders = [f'PHRASE_{i}' for i in range(len(phrase_matches))]
        for i, phrase in enumerate(phrase_matches):
            query = query.replace(f'"{phrase}"', phrase_placeholders[i])

        # 2. Extract proximity queries and replace with placeholders
        proximity_matches = re.findall(r'#(\d+)\(([^,]+),([^,]+)\)', query)
        proximity_placeholders = [f'PROX_{i}' for i in range(len(proximity_matches))]
        for i, (dist, term1, term2) in enumerate(proximity_matches):
            pattern = f'#%s(%s,%s)' % (dist, term1, term2)
            query = query.replace(pattern, proximity_placeholders[i])

        # 3. Parse Boolean query
        terms_and_operators = self.parse_boolean_query(query)

        # 4. Handle placeholders, execute phrase and proximity searches
        # Create a mapping to associate placeholders with their corresponding result sets
        placeholder_results = {}

        # Process phrase queries
        for i, placeholder in enumerate(phrase_placeholders):
            phrase_result = self.phrase_search(phrase_matches[i])
            placeholder_results[placeholder] = phrase_result

        # Process proximity queries
        for i, placeholder in enumerate(proximity_placeholders):
            dist, term1, term2 = proximity_matches[i]
            proximity_result = self.proximity_search(term1.strip(), term2.strip(), int(dist))
            placeholder_results[placeholder] = proximity_result

        # 5. Before Boolean search, replace placeholders with corresponding result sets
        for i, term in enumerate(terms_and_operators[0]):
            if term in placeholder_results:
                terms_and_operators[0][i] = placeholder_results[term]

        # 6. Execute Boolean search
        return self.boolean_search(*terms_and_operators)



    def parse_boolean_query(self, query):
        """
        Parse Boolean queries, supporting multiple operators
        :param query: User input Boolean query string
        :return: Returns the parsed Boolean query structure
        """
        # First handle NOT operator, as it has the highest precedence
        tokens = query.split()

        terms_processed = []
        operators = []

        i = 0
        while i < len(tokens):
            token = tokens[i]
            if token == "NOT":
                if i + 1 < len(tokens):
                    next_token = tokens[i + 1]
                    terms_processed.append(("NOT", next_token))
                    i += 2
                else:
                    raise ValueError("NOT operator must be followed by a term.")
            elif token in ("AND", "OR"):
                operators.append(token)
                i += 1
            else:
                terms_processed.append(tokens[i])
                i += 1

        return terms_processed, operators


    def boolean_search(self, query_terms, operators):
        """
        Implement Boolean search, supporting multiple AND, OR, NOT operations
        :param query_terms: Processed query terms list, including normal terms, phrase/proximity search results, and ("NOT", term) structures
        :param operators: List of Boolean operators, including "AND" and "OR"
        :return: Returns a set of document IDs that meet the conditions
        """
        results = None

        for i, term in enumerate(query_terms):
            if isinstance(term, set):
                # term is a result set from phrase or proximity search
                term_docs = term
            elif isinstance(term, tuple) and term[0] == "NOT":
                not_term = self.preprocessor.process_text(term[1])[0]
                term_docs = self.get_all_docs() - set(self.index.get(not_term, {}).keys())
            else:
                preprocessed_term = self.preprocessor.process_text(term)[0]
                term_docs = set(self.index.get(preprocessed_term, {}).keys())

            # Perform Boolean operations
            if results is None:
                results = term_docs
            else:
                if i - 1 >= 0 and i - 1 < len(operators):
                    operator = operators[i - 1]
                    if operator == "AND":
                        results &= term_docs  # Intersection
                    elif operator == "OR":
                        results |= term_docs  # Union
                    else:
                        raise ValueError(f"Unsupported operator: {operator}")
                else:
                    # If no operator, default to AND
                    results &= term_docs

        return results if results is not None else set()


    def get_all_docs(self):
        """
        Get the set of all document IDs
        :return: Returns a set of all document IDs
        """
        all_docs = set()
        for term in self.index:
            all_docs.update(self.index[term].keys())
        return all_docs


    def phrase_search(self, phrase):
        """
        Implement phrase search
        :param phrase: The phrase to query (multiple terms)
        :return: Returns a set of document IDs that meet the conditions
        """
        if self.preprocessor:
            # Preprocess the phrase to get a list of terms
            phrase_terms = self.preprocessor.process_text(phrase)
        else:
            phrase_terms = phrase.split()

        if len(phrase_terms) == 0:
            return set()

        # Get documents and position lists for the first term
        first_term_docs = self.index.get(phrase_terms[0], {})

        result_docs = set()

        # Check if positions in each document satisfy the phrase condition
        for doc_id, positions in first_term_docs.items():
            for pos in positions:
                match = True
                for i, term in enumerate(phrase_terms[1:], start=1):
                    term_positions = self.index.get(term, {}).get(doc_id, [])
                    if pos + i not in term_positions:
                        match = False
                        break
                if match:
                    result_docs.add(doc_id)

        return result_docs

    def proximity_search(self, term1, term2, max_distance):
        """
        Implement proximity search to find if two terms are within max_distance in the same document
        :param term1: First term
        :param term2: Second term
        :param max_distance: Maximum allowed distance
        :return: Returns a set of document IDs that meet the proximity condition
        """
        if self.preprocessor:
            term1 = self.preprocessor.process_text(term1)[0]
            term2 = self.preprocessor.process_text(term2)[0]

        term1_docs = self.index.get(term1, {})
        term2_docs = self.index.get(term2, {})

        result_docs = set()

        # Find if the two terms are within the allowed distance in the same document
        for doc_id in term1_docs.keys() & term2_docs.keys():
            positions1 = term1_docs[doc_id]
            positions2 = term2_docs[doc_id]

            for pos1 in positions1:
                for pos2 in positions2:
                    if abs(pos1 - pos2) <= max_distance:
                        result_docs.add(doc_id)

        return result_docs
    
    def load_queries(self, query_file_path):
        """
        Load queries from a query file
        :param query_file_path: Query file path
        :return: Returns a dictionary of queries with keys as query IDs and values as query content
        """
        queries = {}
        with open(query_file_path, 'r', encoding='utf-8') as file:
            for line in file:
                line = line.strip()
                if line:
                    # Split query_id and query_text
                    query_id, query_text = line.split(" ", 1)  # May be separated by ": "
                    queries[query_id.strip().lstrip('q')] = query_text.strip()
        return queries

    def save_results(self, result_file_path, results):
        """
        Save search results to a file, with query ID and document ID on the same line
        :param result_file_path: Result file path
        :param results: Result dictionary with keys as query IDs and values as lists of document IDs
        """
        with open(result_file_path, 'w', encoding='utf-8') as file:
            for query_id, doc_ids in results.items():
                for doc_id in doc_ids:
                    file.write(f"{query_id},{doc_id}\n")

    def process_queries_and_save_results(self, query_file_path, result_file_path):
        """
        Process query files and save results to the result file
        :param query_file_path: Query file path
        :param result_file_path: Result file path
        """
        queries = self.load_queries(query_file_path)
        results = {}

        # Process queries one by one and store results
        for query_id, query_text in queries.items():
            result_docs = self.query(query_text)  # Execute query
            results[query_id] = sorted(result_docs)  # Sort result document IDs

        self.save_results(result_file_path, results)  # Save results to file


# RankedRetrieval class for TF-IDF ranking
class RankedRetrieval:
    def __init__(self, index, preprocessor, documents):
        self.index = index.index  # Inverted index
        self.preprocessor = preprocessor
        self.documents = documents  # {doc_id: [tokens]}
        self.N = len(documents)  # Total number of documents

        # Precompute term weights in documents
        self.doc_term_weights = self.calculate_doc_term_weights()

    def calculate_doc_term_weights(self):
        """
        Calculate the weight of each term in each document, stored as a nested dictionary:
        {doc_id: {term: weight}}
        """
        doc_term_weights = defaultdict(dict)
        for doc_id, tokens in self.documents.items():
            term_freqs = defaultdict(int)
            for term in tokens:
                term_freqs[term] += 1
            for term, tf in term_freqs.items():
                tf_weight = 1 + math.log10(tf)
                df = len(self.index.get(term, {}))
                idf = math.log10(self.N / df) if df > 0 else 0
                weight = tf_weight * idf
                doc_term_weights[doc_id][term] = weight
        return doc_term_weights

    def compute_tfidf_scores(self, query):
        """
        Calculate the score of each document for the query, without considering normalization and query weighting.
        """
        query_terms = self.preprocessor.process_text(query)
        doc_scores = defaultdict(float)

        for term in query_terms:
            if term in self.index:
                # df = len(self.index[term])
                # idf = math.log10(self.N / df)
                postings = self.index[term]
                for doc_id in postings.keys():
                    # Get the weight of the term in the document
                    weight = self.doc_term_weights[doc_id].get(term, 0)
                    doc_scores[doc_id] += weight

        # Sort by score in descending order, take the top 150 documents
        sorted_doc_scores = sorted(doc_scores.items(), key=lambda x: x[1], reverse=True)[:150]
        return sorted_doc_scores

    def load_queries(self, query_file_path):
        queries = {}
        with open(query_file_path, 'r', encoding='utf-8') as file:
            for line in file:
                line = line.strip()
                if line:
                    parts = line.split(" ", 1)
                    if len(parts) == 2:
                        query_id, query_text = parts
                        queries[query_id.strip()] = query_text.strip()
        return queries

    def save_results(self, result_file_path, results):
        with open(result_file_path, 'w', encoding='utf-8') as file:
            for query_id, doc_scores in results.items():
                for doc_id, score in doc_scores:
                    file.write(f"{query_id},{doc_id},{score:.4f}\n")

    def process_queries_and_save_results(self, query_file_path, result_file_path):
        queries = self.load_queries(query_file_path)
        results = {}

        for query_id, query_text in queries.items():
            doc_scores = self.compute_tfidf_scores(query_text)
            results[query_id] = doc_scores

        self.save_results(result_file_path, results)


# Example usage
if __name__ == "__main__":
    # Create TextPreprocessor object
    preprocessor = TextPreprocessor(
        stop_words_file='ttds_2023_english_stop_words.txt',
        remove_stop_words=True,
        apply_stemming=True
    )

    # # Process TXT file
    # txt_documents = preprocessor.process_file('sample.txt', file_type='txt')
    # print("Processed TXT Documents:")
    # for doc_id, tokens in txt_documents.items():
    #     print(f"Document {doc_id}: {tokens}")

    # Process XML file
    documents = preprocessor.process_file('cw1collection/trec.5000.xml', file_type='xml')
    # print("\nProcessed XML Documents:")
    # for doc_id, tokens in documents.items():
    #     print(f"Document {doc_id}: {tokens}")

    # Create an inverted index object
    index = PositionalInvertedIndex()

    # Build the index
    index.build_index(documents)

    # Query a term
    # print("Query 'Scotland':", index.query('Scotland', preprocessor))

    # Save the index
    index.save_index('index.txt')

    # Load the index
    # index.load_index('index.txt')

    # Create QueryProcessor object
    query_processor = QueryProcessor(index, preprocessor)

    # Query file path and result file path
    query_file_path = 'cw1collection/queries.boolean.txt'
    result_file_path = 'results.boolean.txt'

    # Process queries and save results
    query_processor.process_queries_and_save_results(query_file_path, result_file_path)
    
    # Create RankedRetrieval object
    ranked_retrieval = RankedRetrieval(index, preprocessor, documents)

    # Process queries and save results
    query_file_path = 'cw1collection/queries.ranked.txt'
    result_file_path = 'results.ranked.txt'

    ranked_retrieval.process_queries_and_save_results(query_file_path, result_file_path)