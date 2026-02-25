"""
Document Ingestion Module

This module handles loading documents from various file formats (PDF, text),
extracting text content, chunking documents for embedding, and creating
vector stores for retrieval.
"""

import os
from typing import List, Dict, Any
from pathlib import Path
import logging

# PDF processing
from PyPDF2 import PdfReader

# LangChain document handling
from langchain_core.documents import Document
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_core.embeddings import Embeddings
from langchain_core.vectorstores import VectorStore
from langchain_community.vectorstores import FAISS

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def load_documents(file_paths: List[str]) -> List[Document]:
    """
    Load documents from file paths, supporting PDF and text files.
    
    This function processes multiple document types and extracts text content
    while preserving metadata about the source file and location within the file.
    
    Args:
        file_paths: List of paths to PDF or text files to load
    
    Returns:
        List of Document objects with content and metadata (source, page)
        
    Raises:
        ValueError: If no valid documents could be loaded from the provided paths
        
    Example:
        >>> docs = load_documents(['financial.pdf', 'contract.txt'])
        >>> print(f"Loaded {len(docs)} document pages/sections")
    """
    documents = []
    skipped_files = []
    
    for file_path in file_paths:
        try:
            # Validate file exists
            if not os.path.exists(file_path):
                logger.warning(f"File not found: {file_path}")
                skipped_files.append((file_path, "File not found"))
                continue
            
            # Get file extension to determine processing method
            file_extension = Path(file_path).suffix.lower()
            
            if file_extension == '.pdf':
                # Process PDF files
                docs = _load_pdf(file_path)
                documents.extend(docs)
                logger.info(f"Loaded {len(docs)} pages from PDF: {file_path}")
                
            elif file_extension in ['.txt', '.text']:
                # Process text files
                docs = _load_text_file(file_path)
                documents.extend(docs)
                logger.info(f"Loaded text file: {file_path}")
                
            else:
                logger.warning(f"Unsupported file format: {file_path} (extension: {file_extension})")
                skipped_files.append((file_path, f"Unsupported format: {file_extension}"))
                
        except Exception as e:
            logger.error(f"Error loading file {file_path}: {str(e)}")
            skipped_files.append((file_path, str(e)))
            continue
    
    # Report skipped files
    if skipped_files:
        logger.warning(f"Skipped {len(skipped_files)} files:")
        for file_path, reason in skipped_files:
            logger.warning(f"  - {file_path}: {reason}")
    
    # Ensure at least some documents were loaded
    if not documents:
        raise ValueError(
            f"No valid documents could be loaded. "
            f"Attempted to load {len(file_paths)} files, all failed."
        )
    
    logger.info(f"Successfully loaded {len(documents)} document pages/sections from {len(file_paths) - len(skipped_files)} files")
    return documents


def _load_pdf(file_path: str) -> List[Document]:
    """
    Load and extract text from a PDF file with page tracking.
    
    Uses PyPDF2 to extract text from each page individually, preserving
    page numbers for citation purposes. Each page becomes a separate
    Document object.
    
    Args:
        file_path: Path to the PDF file
        
    Returns:
        List of Document objects, one per page with metadata
        
    Raises:
        Exception: If PDF cannot be read or is corrupted
    """
    documents = []
    
    try:
        # Open and read the PDF file
        reader = PdfReader(file_path)
        
        # Extract text from each page
        for page_num, page in enumerate(reader.pages, start=1):
            # Extract text content from the page
            text = page.extract_text()
            
            # Skip empty pages (some PDFs have blank pages)
            if not text or not text.strip():
                logger.debug(f"Skipping empty page {page_num} in {file_path}")
                continue
            
            # Create Document object with metadata
            doc = Document(
                page_content=text,
                metadata={
                    'source': os.path.basename(file_path),
                    'page': page_num,
                    'file_path': file_path,
                    'file_type': 'pdf'
                }
            )
            documents.append(doc)
        
        # Warn if no text could be extracted from any page
        if not documents:
            logger.warning(f"No text content extracted from PDF: {file_path}")
            
    except Exception as e:
        logger.error(f"Failed to read PDF {file_path}: {str(e)}")
        raise
    
    return documents


def _load_text_file(file_path: str) -> List[Document]:
    """
    Load and extract text from a plain text file.
    
    Handles encoding issues by attempting UTF-8 first, then falling back
    to latin-1 encoding if UTF-8 fails. This ensures compatibility with
    various text file encodings.
    
    Args:
        file_path: Path to the text file
        
    Returns:
        List containing a single Document object with the file content
        
    Raises:
        Exception: If file cannot be read with any supported encoding
    """
    documents = []
    text = None
    encoding_used = None
    
    # Try UTF-8 encoding first (most common)
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            text = f.read()
        encoding_used = 'utf-8'
    except UnicodeDecodeError:
        # Fall back to latin-1 encoding if UTF-8 fails
        logger.debug(f"UTF-8 decoding failed for {file_path}, trying latin-1")
        try:
            with open(file_path, 'r', encoding='latin-1') as f:
                text = f.read()
            encoding_used = 'latin-1'
            logger.info(f"Successfully read {file_path} using latin-1 encoding")
        except Exception as e:
            logger.error(f"Failed to read text file {file_path} with latin-1: {str(e)}")
            raise
    except Exception as e:
        logger.error(f"Failed to read text file {file_path}: {str(e)}")
        raise
    
    # Check if file is empty
    if not text or not text.strip():
        logger.warning(f"Text file is empty: {file_path}")
        return documents
    
    # Create Document object with metadata
    # For text files, we don't have page numbers, so we use section=1
    doc = Document(
        page_content=text,
        metadata={
            'source': os.path.basename(file_path),
            'page': 1,  # Text files are treated as single-page documents
            'file_path': file_path,
            'file_type': 'text',
            'encoding': encoding_used
        }
    )
    documents.append(doc)
    
    return documents


def chunk_documents(documents: List[Document], 
                   chunk_size: int = 1000, 
                   chunk_overlap: int = 200) -> List[Document]:
    """
    Split documents into smaller chunks suitable for embedding and retrieval.
    
    This function uses LangChain's RecursiveCharacterTextSplitter to intelligently
    split documents at natural boundaries (paragraphs, sentences, words) while
    respecting the specified chunk size and overlap constraints.
    
    Chunking Strategy:
    - Splits text recursively at natural boundaries: "\n\n" (paragraphs), "\n" (lines),
      " " (words), and "" (characters) in that order
    - Preserves context between chunks using overlap (helps maintain semantic continuity)
    - Maintains all original metadata (source, page) and adds chunk_id for tracking
    - Each chunk becomes an independent Document object for embedding
    
    Why Chunking is Important:
    - Embedding models have token limits (typically 8191 tokens for OpenAI)
    - Smaller chunks improve retrieval precision (more focused semantic matching)
    - Overlap ensures important context isn't lost at chunk boundaries
    
    Args:
        documents: List of Document objects to chunk (from load_documents)
        chunk_size: Maximum characters per chunk (default: 1000)
                   Recommended range: 500-2000 depending on use case
        chunk_overlap: Number of characters to overlap between consecutive chunks (default: 200)
                      Recommended: 10-20% of chunk_size for context preservation
    
    Returns:
        List of chunked Document objects with preserved metadata plus chunk_id
        
    Example:
        >>> docs = load_documents(['contract.pdf'])
        >>> chunks = chunk_documents(docs, chunk_size=800, chunk_overlap=150)
        >>> print(f"Split {len(docs)} documents into {len(chunks)} chunks")
        >>> print(f"First chunk metadata: {chunks[0].metadata}")
        
    Metadata Preservation:
        Original metadata (source, page, file_path, file_type) is preserved
        New metadata added:
        - chunk_id: Unique identifier in format "source_page_N" where N is chunk number
        - chunk_index: Zero-based index of chunk within the parent document
        - total_chunks: Total number of chunks created from the parent document
    """
    # Initialize the text splitter with recursive strategy
    # RecursiveCharacterTextSplitter tries to split at natural boundaries in order:
    # 1. Double newlines (paragraph breaks)
    # 2. Single newlines (line breaks)
    # 3. Spaces (word boundaries)
    # 4. Characters (as last resort)
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=chunk_size,
        chunk_overlap=chunk_overlap,
        length_function=len,  # Use character count (not tokens) for simplicity
        separators=["\n\n", "\n", " ", ""]  # Natural text boundaries in priority order
    )
    
    chunked_documents = []
    total_chunks_created = 0
    
    # Process each document individually to preserve metadata
    for doc in documents:
        # Split the document content into chunks
        # split_text returns a list of text strings
        text_chunks = text_splitter.split_text(doc.page_content)
        
        # Create Document objects for each chunk, preserving original metadata
        for chunk_index, chunk_text in enumerate(text_chunks):
            # Copy original metadata to preserve source, page, etc.
            chunk_metadata = doc.metadata.copy()
            
            # Add chunk-specific metadata for tracking and citation
            # Format: "filename_page_chunknum" (e.g., "contract.pdf_3_0")
            source = chunk_metadata.get('source', 'unknown')
            page = chunk_metadata.get('page', 0)
            chunk_id = f"{source}_page{page}_chunk{chunk_index}"
            
            chunk_metadata['chunk_id'] = chunk_id
            chunk_metadata['chunk_index'] = chunk_index
            chunk_metadata['total_chunks'] = len(text_chunks)
            
            # Create new Document object for this chunk
            chunked_doc = Document(
                page_content=chunk_text,
                metadata=chunk_metadata
            )
            chunked_documents.append(chunked_doc)
        
        total_chunks_created += len(text_chunks)
        logger.debug(
            f"Split document from {doc.metadata.get('source', 'unknown')} "
            f"page {doc.metadata.get('page', '?')} into {len(text_chunks)} chunks"
        )
    
    logger.info(
        f"Chunking complete: {len(documents)} documents → {total_chunks_created} chunks "
        f"(avg {total_chunks_created / len(documents):.1f} chunks per document)"
    )
    
    return chunked_documents


def create_vector_store(chunks: List[Document], 
                       embeddings_model: Embeddings,
                       persist_directory: str = "vector_store") -> VectorStore:
    """
    Generate embeddings for document chunks and create a FAISS vector store.
    
    This function takes chunked documents, generates embeddings using OpenAI's
    embedding model, and stores them in a FAISS (Facebook AI Similarity Search)
    vector store for efficient similarity search during retrieval.
    
    What are Embeddings?
    - Embeddings are dense vector representations of text (typically 1536 dimensions for OpenAI)
    - Similar text has similar embeddings (measured by cosine similarity)
    - Enables semantic search: find documents by meaning, not just keywords
    
    What is FAISS?
    - FAISS is a library for efficient similarity search in high-dimensional spaces
    - Optimized for fast nearest-neighbor search in embedding vectors
    - Supports persistence to disk for reuse without re-embedding
    
    Retry Logic:
    - OpenAI API calls can fail due to rate limits, network issues, or service outages
    - Implements exponential backoff: wait 1s, 2s, 4s between retries
    - Retries up to 3 times before raising an error
    
    Args:
        chunks: List of Document objects with text content and metadata
        embeddings_model: OpenAI embeddings model instance (e.g., OpenAIEmbeddings())
        persist_directory: Directory path to save the FAISS index (default: "vector_store")
                          Allows loading the vector store later without re-embedding
    
    Returns:
        FAISS VectorStore object containing indexed embeddings with metadata
        
    Raises:
        Exception: If embedding generation fails after all retries
        ValueError: If chunks list is empty
        
    Example:
        >>> from langchain_openai import OpenAIEmbeddings
        >>> chunks = chunk_documents(documents)
        >>> embeddings = OpenAIEmbeddings(model="text-embedding-ada-002")
        >>> vector_store = create_vector_store(chunks, embeddings)
        >>> # Later, load from disk:
        >>> loaded_store = FAISS.load_local("vector_store", embeddings)
        
    Metadata Preservation:
    - All chunk metadata (source, page, chunk_id) is preserved in the vector store
    - Metadata is returned with retrieved chunks for citation purposes
    - Essential for tracing findings back to source documents
    """
    import time
    
    # Validate input
    if not chunks:
        raise ValueError("Cannot create vector store from empty chunks list")
    
    logger.info(f"Creating vector store from {len(chunks)} chunks...")
    logger.info(f"Embedding model: {embeddings_model.__class__.__name__}")
    
    # Retry configuration for API calls
    max_retries = 3
    base_delay = 1  # seconds
    
    vector_store = None
    last_error = None
    
    # Attempt to create vector store with retry logic
    for attempt in range(max_retries):
        try:
            logger.info(f"Generating embeddings (attempt {attempt + 1}/{max_retries})...")
            
            # Create FAISS vector store from documents
            # This performs the following steps internally:
            # 1. Extracts text content from each Document
            # 2. Calls OpenAI API to generate embeddings for each chunk
            # 3. Builds FAISS index for efficient similarity search
            # 4. Stores metadata alongside embeddings
            vector_store = FAISS.from_documents(
                documents=chunks,
                embedding=embeddings_model
            )
            
            logger.info(f"Successfully created vector store with {len(chunks)} embeddings")
            
            # Persist vector store to disk for future use
            # This saves both the FAISS index and the document metadata
            # Allows loading the vector store without re-generating embeddings
            try:
                # Create directory if it doesn't exist
                os.makedirs(persist_directory, exist_ok=True)
                
                # Save FAISS index and metadata to disk
                vector_store.save_local(persist_directory)
                logger.info(f"Vector store persisted to: {persist_directory}")
                
            except Exception as persist_error:
                # Log persistence error but don't fail the function
                # The vector store is still usable in memory
                logger.warning(
                    f"Failed to persist vector store to disk: {str(persist_error)}. "
                    f"Vector store is still available in memory."
                )
            
            # Success - return the vector store
            return vector_store
            
        except Exception as e:
            last_error = e
            error_message = str(e)
            
            # Check if this is a rate limit error (HTTP 429)
            is_rate_limit = "429" in error_message or "rate limit" in error_message.lower()
            
            # Check if this is a retriable error
            is_retriable = (
                is_rate_limit or
                "timeout" in error_message.lower() or
                "connection" in error_message.lower() or
                "network" in error_message.lower()
            )
            
            if attempt < max_retries - 1 and is_retriable:
                # Calculate exponential backoff delay: 1s, 2s, 4s
                delay = base_delay * (2 ** attempt)
                
                if is_rate_limit:
                    logger.warning(
                        f"Rate limit hit. Waiting {delay}s before retry "
                        f"(attempt {attempt + 1}/{max_retries})..."
                    )
                else:
                    logger.warning(
                        f"API error: {error_message}. Retrying in {delay}s "
                        f"(attempt {attempt + 1}/{max_retries})..."
                    )
                
                time.sleep(delay)
            else:
                # Non-retriable error or final attempt failed
                if attempt == max_retries - 1:
                    logger.error(
                        f"Failed to create vector store after {max_retries} attempts. "
                        f"Last error: {error_message}"
                    )
                else:
                    logger.error(f"Non-retriable error: {error_message}")
                
                # Re-raise the error
                raise Exception(
                    f"Failed to create vector store: {error_message}. "
                    f"Please check your OpenAI API key and network connection."
                ) from last_error
    
    # Should never reach here due to raise in loop, but for type safety
    raise Exception(f"Failed to create vector store after {max_retries} attempts") from last_error
