"""
Free embeddings implementation using scikit-learn TF-IDF
This avoids the need for OpenAI API or heavy PyTorch dependencies
"""

from typing import List
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from langchain_core.embeddings import Embeddings


class FreeEmbeddings(Embeddings):
    """
    Free embeddings using TF-IDF vectorization from scikit-learn.
    This provides a lightweight alternative to OpenAI or sentence-transformers.
    """
    
    def __init__(self, max_features: int = 5000):
        """
        Initialize the free embeddings.
        
        Args:
            max_features: Maximum number of features for TF-IDF
        """
        self.max_features = max_features
        self.vectorizer = TfidfVectorizer(
            max_features=max_features,
            stop_words='english',
            ngram_range=(1, 2),  # Use unigrams and bigrams
            lowercase=True,
            strip_accents='ascii'
        )
        self.is_fitted = False
        self._corpus = []
    
    def embed_documents(self, texts: List[str]) -> List[List[float]]:
        """
        Embed a list of documents.
        
        Args:
            texts: List of documents to embed
            
        Returns:
            List of embeddings (each embedding is a list of floats)
        """
        # Store corpus for fitting if not already fitted
        if not self.is_fitted:
            self._corpus.extend(texts)
            # Fit the vectorizer on all texts
            self.vectorizer.fit(self._corpus)
            self.is_fitted = True
        
        # Transform texts to embeddings
        embeddings_matrix = self.vectorizer.transform(texts)
        
        # Convert sparse matrix to dense and then to list of lists
        embeddings_dense = embeddings_matrix.toarray()
        
        return [embedding.tolist() for embedding in embeddings_dense]
    
    def embed_query(self, text: str) -> List[float]:
        """
        Embed a single query text.
        
        Args:
            text: Query text to embed
            
        Returns:
            Embedding as a list of floats
        """
        if not self.is_fitted:
            # If not fitted yet, fit on the query (not ideal but works)
            self.vectorizer.fit([text])
            self.is_fitted = True
        
        # Transform the query
        embedding_matrix = self.vectorizer.transform([text])
        embedding_dense = embedding_matrix.toarray()[0]
        
        return embedding_dense.tolist()
    
    def add_texts_to_corpus(self, texts: List[str]):
        """
        Add texts to the corpus for better TF-IDF fitting.
        Call this before embedding if you have a known corpus.
        
        Args:
            texts: List of texts to add to corpus
        """
        self._corpus.extend(texts)
        if len(self._corpus) > 0:
            self.vectorizer.fit(self._corpus)
            self.is_fitted = True