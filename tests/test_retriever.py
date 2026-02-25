"""
Unit tests for retrieval module.
"""

import pytest
import numpy as np
from langchain_core.documents import Document
from langchain_core.embeddings import Embeddings
from ai_due_diligence.ingest import create_vector_store
from ai_due_diligence.retriever import retrieve_relevant_chunks


class MockEmbeddings(Embeddings):
    """Mock embeddings for testing without API calls."""
    
    def embed_documents(self, texts):
        """Return mock embeddings for a list of texts."""
        # Return random vectors of dimension 1536 (OpenAI's dimension)
        return [np.random.rand(1536).tolist() for _ in texts]
    
    def embed_query(self, text):
        """Return mock embedding for a single query."""
        return np.random.rand(1536).tolist()


class TestRetrieveRelevantChunks:
    """Test suite for retrieve_relevant_chunks function."""
    
    def test_retrieve_basic_functionality(self, tmp_path):
        """Test basic retrieval of relevant chunks."""
        # Create test documents with metadata
        docs = [
            Document(
                page_content="Financial projections show strong revenue growth.",
                metadata={'source': 'financial.txt', 'page': 1, 'chunk_id': 'financial.txt_page1_chunk0'}
            ),
            Document(
                page_content="Legal contract includes termination clauses.",
                metadata={'source': 'contract.txt', 'page': 2, 'chunk_id': 'contract.txt_page2_chunk0'}
            ),
            Document(
                page_content="Operational risks include vendor dependencies.",
                metadata={'source': 'operations.txt', 'page': 1, 'chunk_id': 'operations.txt_page1_chunk0'}
            )
        ]
        
        # Create vector store
        mock_embeddings = MockEmbeddings()
        persist_dir = str(tmp_path / "test_retrieval")
        vector_store = create_vector_store(docs, mock_embeddings, persist_directory=persist_dir)
        
        # Retrieve relevant chunks
        results = retrieve_relevant_chunks(vector_store, "financial revenue", k=2)
        
        # Verify results structure
        assert len(results) <= 2, "Should return at most k results"
        assert all(isinstance(item, tuple) for item in results), "Results should be tuples"
        assert all(len(item) == 2 for item in results), "Each tuple should have 2 elements"
        
        # Verify Document and score types
        for doc, score in results:
            assert isinstance(doc, Document), "First element should be Document"
            # Score can be numpy float32 or regular float
            assert isinstance(score, (int, float, np.floating)), "Second element should be numeric score"
    
    def test_retrieve_returns_metadata(self, tmp_path):
        """Test that retrieved chunks include metadata."""
        # Create test document with specific metadata
        test_metadata = {
            'source': 'test_doc.pdf',
            'page': 5,
            'chunk_id': 'test_doc.pdf_page5_chunk0',
            'chunk_index': 0
        }
        
        docs = [
            Document(
                page_content="This document contains important information.",
                metadata=test_metadata
            )
        ]
        
        # Create vector store
        mock_embeddings = MockEmbeddings()
        persist_dir = str(tmp_path / "metadata_retrieval")
        vector_store = create_vector_store(docs, mock_embeddings, persist_directory=persist_dir)
        
        # Retrieve chunks
        results = retrieve_relevant_chunks(vector_store, "important information", k=1)
        
        # Verify metadata is present
        assert len(results) == 1
        doc, score = results[0]
        
        assert 'source' in doc.metadata, "Metadata should include 'source'"
        assert 'page' in doc.metadata, "Metadata should include 'page'"
        assert 'chunk_id' in doc.metadata, "Metadata should include 'chunk_id'"
        
        # Verify metadata values
        assert doc.metadata['source'] == 'test_doc.pdf'
        assert doc.metadata['page'] == 5
        assert doc.metadata['chunk_id'] == 'test_doc.pdf_page5_chunk0'
    
    def test_retrieve_ranking_order(self, tmp_path):
        """Test that results are returned in descending order by similarity score."""
        # Create multiple test documents
        docs = [
            Document(
                page_content="Document one content.",
                metadata={'source': 'doc1.txt', 'page': 1}
            ),
            Document(
                page_content="Document two content.",
                metadata={'source': 'doc2.txt', 'page': 1}
            ),
            Document(
                page_content="Document three content.",
                metadata={'source': 'doc3.txt', 'page': 1}
            ),
            Document(
                page_content="Document four content.",
                metadata={'source': 'doc4.txt', 'page': 1}
            )
        ]
        
        # Create vector store
        mock_embeddings = MockEmbeddings()
        persist_dir = str(tmp_path / "ranking_test")
        vector_store = create_vector_store(docs, mock_embeddings, persist_directory=persist_dir)
        
        # Retrieve multiple chunks
        results = retrieve_relevant_chunks(vector_store, "document content", k=4)
        
        # Verify results are in ascending order by score (FAISS returns distances, lower is better)
        scores = [float(score) for _, score in results]
        assert scores == sorted(scores), \
            "Results should be ranked in ascending order by distance (lower distance = higher similarity)"
    
    def test_retrieve_with_different_k_values(self, tmp_path):
        """Test retrieval with different k parameter values."""
        # Create test documents
        docs = [
            Document(page_content=f"Document {i} content.", metadata={'source': f'doc{i}.txt', 'page': 1})
            for i in range(10)
        ]
        
        # Create vector store
        mock_embeddings = MockEmbeddings()
        persist_dir = str(tmp_path / "k_values_test")
        vector_store = create_vector_store(docs, mock_embeddings, persist_directory=persist_dir)
        
        # Test different k values
        for k in [1, 3, 5, 10]:
            results = retrieve_relevant_chunks(vector_store, "document", k=k)
            assert len(results) <= k, f"Should return at most {k} results"
    
    def test_retrieve_empty_query_raises_error(self, tmp_path):
        """Test that empty query raises ValueError."""
        # Create minimal vector store
        docs = [Document(page_content="Test content.", metadata={'source': 'test.txt', 'page': 1})]
        mock_embeddings = MockEmbeddings()
        persist_dir = str(tmp_path / "empty_query_test")
        vector_store = create_vector_store(docs, mock_embeddings, persist_directory=persist_dir)
        
        # Test empty query
        with pytest.raises(ValueError, match="Query string cannot be empty"):
            retrieve_relevant_chunks(vector_store, "", k=5)
        
        # Test whitespace-only query
        with pytest.raises(ValueError, match="Query string cannot be empty"):
            retrieve_relevant_chunks(vector_store, "   ", k=5)
    
    def test_retrieve_invalid_k_raises_error(self, tmp_path):
        """Test that invalid k parameter raises ValueError."""
        # Create minimal vector store
        docs = [Document(page_content="Test content.", metadata={'source': 'test.txt', 'page': 1})]
        mock_embeddings = MockEmbeddings()
        persist_dir = str(tmp_path / "invalid_k_test")
        vector_store = create_vector_store(docs, mock_embeddings, persist_directory=persist_dir)
        
        # Test k = 0
        with pytest.raises(ValueError, match="k must be positive"):
            retrieve_relevant_chunks(vector_store, "test", k=0)
        
        # Test negative k
        with pytest.raises(ValueError, match="k must be positive"):
            retrieve_relevant_chunks(vector_store, "test", k=-1)
    
    def test_retrieve_k_larger_than_corpus(self, tmp_path):
        """Test retrieval when k is larger than the number of documents."""
        # Create small corpus
        docs = [
            Document(page_content="Doc 1.", metadata={'source': 'doc1.txt', 'page': 1}),
            Document(page_content="Doc 2.", metadata={'source': 'doc2.txt', 'page': 1})
        ]
        
        # Create vector store
        mock_embeddings = MockEmbeddings()
        persist_dir = str(tmp_path / "large_k_test")
        vector_store = create_vector_store(docs, mock_embeddings, persist_directory=persist_dir)
        
        # Request more results than available
        results = retrieve_relevant_chunks(vector_store, "document", k=10)
        
        # Should return all available documents (2), not fail
        assert len(results) == 2, "Should return all available documents when k > corpus size"



class TestFormatChunksWithCitations:
    """Test suite for format_chunks_with_citations function."""
    
    def test_format_basic_functionality(self):
        """Test basic formatting of chunks with citations."""
        from ai_due_diligence.retriever import format_chunks_with_citations
        
        # Create test chunks
        chunks = [
            (
                Document(
                    page_content="Financial projections show strong revenue growth.",
                    metadata={'source': 'financial.pdf', 'page': 3}
                ),
                0.145
            ),
            (
                Document(
                    page_content="Legal contract includes termination clauses.",
                    metadata={'source': 'contract.pdf', 'page': 7}
                ),
                0.289
            )
        ]
        
        # Format chunks
        result = format_chunks_with_citations(chunks)
        
        # Verify output structure
        assert isinstance(result, str), "Should return a string"
        assert len(result) > 0, "Should return non-empty string"
        
        # Verify chunk numbering
        assert "[Chunk 1]" in result, "Should include first chunk number"
        assert "[Chunk 2]" in result, "Should include second chunk number"
        
        # Verify source citations
        assert "Source: financial.pdf" in result, "Should include first source"
        assert "Source: contract.pdf" in result, "Should include second source"
        
        # Verify page numbers
        assert "Page: 3" in result, "Should include first page number"
        assert "Page: 7" in result, "Should include second page number"
        
        # Verify scores
        assert "Score: 0.145" in result, "Should include first score"
        assert "Score: 0.289" in result, "Should include second score"
        
        # Verify content is included
        assert "Financial projections show strong revenue growth." in result
        assert "Legal contract includes termination clauses." in result
    
    def test_format_empty_chunks(self):
        """Test formatting with empty chunks list."""
        from ai_due_diligence.retriever import format_chunks_with_citations
        
        result = format_chunks_with_citations([])
        
        assert result == "", "Should return empty string for empty input"
    
    def test_format_single_chunk(self):
        """Test formatting with a single chunk."""
        from ai_due_diligence.retriever import format_chunks_with_citations
        
        chunks = [
            (
                Document(
                    page_content="Single chunk content.",
                    metadata={'source': 'test.txt', 'page': 1}
                ),
                0.123
            )
        ]
        
        result = format_chunks_with_citations(chunks)
        
        assert "[Chunk 1]" in result
        assert "Source: test.txt" in result
        assert "Page: 1" in result
        assert "Score: 0.123" in result
        assert "Single chunk content." in result
    
    def test_format_missing_metadata(self):
        """Test formatting when metadata is missing."""
        from ai_due_diligence.retriever import format_chunks_with_citations
        
        # Create chunk with missing metadata
        chunks = [
            (
                Document(
                    page_content="Content without metadata.",
                    metadata={}
                ),
                0.456
            )
        ]
        
        result = format_chunks_with_citations(chunks)
        
        # Should use fallback values
        assert "Source: unknown_source" in result, "Should use fallback for missing source"
        assert "Page: unknown" in result, "Should use fallback for missing page"
        assert "Content without metadata." in result
    
    def test_format_preserves_chunk_order(self):
        """Test that formatting preserves the order of chunks."""
        from ai_due_diligence.retriever import format_chunks_with_citations
        
        chunks = [
            (Document(page_content="First chunk.", metadata={'source': 'doc1.txt', 'page': 1}), 0.1),
            (Document(page_content="Second chunk.", metadata={'source': 'doc2.txt', 'page': 2}), 0.2),
            (Document(page_content="Third chunk.", metadata={'source': 'doc3.txt', 'page': 3}), 0.3)
        ]
        
        result = format_chunks_with_citations(chunks)
        
        # Find positions of chunk markers
        pos_chunk1 = result.find("[Chunk 1]")
        pos_chunk2 = result.find("[Chunk 2]")
        pos_chunk3 = result.find("[Chunk 3]")
        
        # Verify order
        assert pos_chunk1 < pos_chunk2 < pos_chunk3, "Chunks should appear in order"
        
        # Verify content order
        pos_first = result.find("First chunk.")
        pos_second = result.find("Second chunk.")
        pos_third = result.find("Third chunk.")
        
        assert pos_first < pos_second < pos_third, "Content should appear in order"
    
    def test_format_with_various_score_values(self):
        """Test formatting with different score values."""
        from ai_due_diligence.retriever import format_chunks_with_citations
        
        chunks = [
            (Document(page_content="Very relevant.", metadata={'source': 'doc.txt', 'page': 1}), 0.001),
            (Document(page_content="Less relevant.", metadata={'source': 'doc.txt', 'page': 2}), 1.234),
            (Document(page_content="Least relevant.", metadata={'source': 'doc.txt', 'page': 3}), 99.999)
        ]
        
        result = format_chunks_with_citations(chunks)
        
        # Verify scores are formatted to 3 decimal places
        assert "Score: 0.001" in result
        assert "Score: 1.234" in result
        assert "Score: 99.999" in result
    
    def test_format_with_multiline_content(self):
        """Test formatting with multiline chunk content."""
        from ai_due_diligence.retriever import format_chunks_with_citations
        
        multiline_content = """This is a chunk with
multiple lines of text.
It should be preserved correctly."""
        
        chunks = [
            (
                Document(
                    page_content=multiline_content,
                    metadata={'source': 'multiline.txt', 'page': 1}
                ),
                0.5
            )
        ]
        
        result = format_chunks_with_citations(chunks)
        
        # Verify multiline content is preserved
        assert "multiple lines of text." in result
        assert "It should be preserved correctly." in result
