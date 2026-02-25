"""
Unit tests for document ingestion module.
"""

import os
import pytest
from pathlib import Path
from ai_due_diligence.ingest import load_documents


class TestLoadDocuments:
    """Test suite for load_documents function."""
    
    def test_load_text_file(self, tmp_path):
        """Test loading a simple text file."""
        # Create a temporary text file
        test_file = tmp_path / "test.txt"
        test_content = "This is a test document.\nIt has multiple lines."
        test_file.write_text(test_content, encoding='utf-8')
        
        # Load the document
        docs = load_documents([str(test_file)])
        
        # Verify results
        assert len(docs) == 1
        assert docs[0].page_content == test_content
        assert docs[0].metadata['source'] == "test.txt"
        assert docs[0].metadata['page'] == 1
        assert docs[0].metadata['file_type'] == 'text'
    
    def test_load_nonexistent_file(self):
        """Test handling of nonexistent files."""
        with pytest.raises(ValueError, match="No valid documents could be loaded"):
            load_documents(["nonexistent_file.txt"])
    
    def test_load_empty_text_file(self, tmp_path):
        """Test handling of empty text files."""
        # Create an empty text file
        test_file = tmp_path / "empty.txt"
        test_file.write_text("", encoding='utf-8')
        
        # Should raise ValueError since no valid documents
        with pytest.raises(ValueError, match="No valid documents could be loaded"):
            load_documents([str(test_file)])
    
    def test_load_multiple_text_files(self, tmp_path):
        """Test loading multiple text files."""
        # Create multiple text files
        file1 = tmp_path / "doc1.txt"
        file1.write_text("Document 1 content", encoding='utf-8')
        
        file2 = tmp_path / "doc2.txt"
        file2.write_text("Document 2 content", encoding='utf-8')
        
        # Load documents
        docs = load_documents([str(file1), str(file2)])
        
        # Verify results
        assert len(docs) == 2
        assert docs[0].page_content == "Document 1 content"
        assert docs[1].page_content == "Document 2 content"
    
    def test_load_latin1_encoded_file(self, tmp_path):
        """Test loading a file with latin-1 encoding."""
        # Create a file with latin-1 specific characters
        test_file = tmp_path / "latin1.txt"
        content = "Café résumé naïve"
        test_file.write_text(content, encoding='latin-1')
        
        # Load the document
        docs = load_documents([str(test_file)])
        
        # Verify it was loaded (content may differ due to encoding)
        assert len(docs) == 1
        assert docs[0].metadata['source'] == "latin1.txt"



class TestChunkDocuments:
    """Test suite for chunk_documents function."""
    
    def test_chunk_basic_functionality(self, tmp_path):
        """Test basic chunking of a document."""
        from ai_due_diligence.ingest import load_documents, chunk_documents
        
        # Create a text file with enough content to be chunked
        test_file = tmp_path / "test.txt"
        # Create content that will definitely be split into multiple chunks
        test_content = "This is a test paragraph.\n\n" * 100  # ~2700 characters
        test_file.write_text(test_content, encoding='utf-8')
        
        # Load and chunk the document
        docs = load_documents([str(test_file)])
        chunks = chunk_documents(docs, chunk_size=500, chunk_overlap=50)
        
        # Verify chunking occurred
        assert len(chunks) > 1, "Document should be split into multiple chunks"
        
        # Verify metadata preservation
        for chunk in chunks:
            assert 'source' in chunk.metadata
            assert 'page' in chunk.metadata
            assert 'chunk_id' in chunk.metadata
            assert 'chunk_index' in chunk.metadata
            assert 'total_chunks' in chunk.metadata
            assert chunk.metadata['source'] == "test.txt"
    
    def test_chunk_size_constraint(self, tmp_path):
        """Test that chunks respect size constraints."""
        from ai_due_diligence.ingest import load_documents, chunk_documents
        
        # Create a text file
        test_file = tmp_path / "test.txt"
        test_content = "Word " * 500  # 2500 characters
        test_file.write_text(test_content, encoding='utf-8')
        
        # Load and chunk with specific size
        docs = load_documents([str(test_file)])
        chunk_size = 300
        chunks = chunk_documents(docs, chunk_size=chunk_size, chunk_overlap=50)
        
        # Verify chunk sizes (all but possibly the last should be <= chunk_size)
        for i, chunk in enumerate(chunks[:-1]):  # Check all but last chunk
            assert len(chunk.page_content) <= chunk_size, \
                f"Chunk {i} exceeds size limit: {len(chunk.page_content)} > {chunk_size}"
    
    def test_chunk_metadata_uniqueness(self, tmp_path):
        """Test that each chunk has a unique chunk_id."""
        from ai_due_diligence.ingest import load_documents, chunk_documents
        
        # Create a text file
        test_file = tmp_path / "test.txt"
        test_content = "Paragraph.\n\n" * 100
        test_file.write_text(test_content, encoding='utf-8')
        
        # Load and chunk
        docs = load_documents([str(test_file)])
        chunks = chunk_documents(docs, chunk_size=400, chunk_overlap=50)
        
        # Verify all chunk_ids are unique
        chunk_ids = [chunk.metadata['chunk_id'] for chunk in chunks]
        assert len(chunk_ids) == len(set(chunk_ids)), "Chunk IDs should be unique"
    
    def test_chunk_small_document(self, tmp_path):
        """Test chunking a document smaller than chunk_size."""
        from ai_due_diligence.ingest import load_documents, chunk_documents
        
        # Create a small text file
        test_file = tmp_path / "small.txt"
        test_content = "This is a small document."
        test_file.write_text(test_content, encoding='utf-8')
        
        # Load and chunk with large chunk_size
        docs = load_documents([str(test_file)])
        chunks = chunk_documents(docs, chunk_size=1000, chunk_overlap=100)
        
        # Should result in a single chunk
        assert len(chunks) == 1
        assert chunks[0].page_content == test_content
        assert chunks[0].metadata['chunk_index'] == 0
        assert chunks[0].metadata['total_chunks'] == 1



class TestCreateVectorStore:
    """Test suite for create_vector_store function."""
    
    def test_create_vector_store_basic(self, tmp_path):
        """Test basic vector store creation with mock embeddings."""
        from ai_due_diligence.ingest import chunk_documents, create_vector_store
        from langchain_core.documents import Document
        from langchain_core.embeddings import Embeddings
        import numpy as np
        
        # Create a simple mock embeddings class
        class MockEmbeddings(Embeddings):
            """Mock embeddings for testing without API calls."""
            
            def embed_documents(self, texts):
                """Return mock embeddings for a list of texts."""
                # Return random vectors of dimension 1536 (OpenAI's dimension)
                return [np.random.rand(1536).tolist() for _ in texts]
            
            def embed_query(self, text):
                """Return mock embedding for a single query."""
                return np.random.rand(1536).tolist()
        
        # Create test documents
        docs = [
            Document(
                page_content="This is the first test document.",
                metadata={'source': 'test1.txt', 'page': 1}
            ),
            Document(
                page_content="This is the second test document.",
                metadata={'source': 'test2.txt', 'page': 1}
            )
        ]
        
        # Chunk documents
        chunks = chunk_documents(docs, chunk_size=100, chunk_overlap=20)
        
        # Create vector store with mock embeddings
        mock_embeddings = MockEmbeddings()
        persist_dir = str(tmp_path / "test_vector_store")
        
        vector_store = create_vector_store(
            chunks, 
            mock_embeddings,
            persist_directory=persist_dir
        )
        
        # Verify vector store was created
        assert vector_store is not None
        
        # Verify persistence directory was created
        assert os.path.exists(persist_dir)
    
    def test_create_vector_store_empty_chunks(self):
        """Test that empty chunks list raises ValueError."""
        from ai_due_diligence.ingest import create_vector_store
        from langchain_core.embeddings import Embeddings
        import numpy as np
        
        class MockEmbeddings(Embeddings):
            def embed_documents(self, texts):
                return [np.random.rand(1536).tolist() for _ in texts]
            
            def embed_query(self, text):
                return np.random.rand(1536).tolist()
        
        mock_embeddings = MockEmbeddings()
        
        # Should raise ValueError for empty chunks
        with pytest.raises(ValueError, match="Cannot create vector store from empty chunks list"):
            create_vector_store([], mock_embeddings)
    
    def test_create_vector_store_metadata_preservation(self, tmp_path):
        """Test that metadata is preserved in the vector store."""
        from ai_due_diligence.ingest import create_vector_store
        from langchain_core.documents import Document
        from langchain_core.embeddings import Embeddings
        import numpy as np
        
        class MockEmbeddings(Embeddings):
            def embed_documents(self, texts):
                return [np.random.rand(1536).tolist() for _ in texts]
            
            def embed_query(self, text):
                return np.random.rand(1536).tolist()
        
        # Create test document with specific metadata
        test_metadata = {
            'source': 'contract.pdf',
            'page': 5,
            'chunk_id': 'contract.pdf_page5_chunk0',
            'chunk_index': 0
        }
        
        docs = [
            Document(
                page_content="Test content for metadata preservation.",
                metadata=test_metadata
            )
        ]
        
        # Create vector store
        mock_embeddings = MockEmbeddings()
        persist_dir = str(tmp_path / "metadata_test")
        
        vector_store = create_vector_store(
            docs,
            mock_embeddings,
            persist_directory=persist_dir
        )
        
        # Retrieve the document to verify metadata
        results = vector_store.similarity_search("Test content", k=1)
        
        assert len(results) == 1
        retrieved_doc = results[0]
        
        # Verify all metadata fields are preserved
        assert retrieved_doc.metadata['source'] == 'contract.pdf'
        assert retrieved_doc.metadata['page'] == 5
        assert retrieved_doc.metadata['chunk_id'] == 'contract.pdf_page5_chunk0'
        assert retrieved_doc.metadata['chunk_index'] == 0
