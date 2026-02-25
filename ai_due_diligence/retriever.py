"""
Retrieval Module

This module handles querying the vector store to retrieve relevant document chunks
based on semantic similarity. It provides functions for similarity search and
formatting retrieved chunks with proper citations.
"""

import logging
from typing import List, Tuple

# LangChain imports
from langchain_core.documents import Document
from langchain_core.vectorstores import VectorStore

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def retrieve_relevant_chunks(vector_store: VectorStore, 
                            query: str, 
                            k: int = 5) -> List[Tuple[Document, float]]:
    """
    Retrieve the top-k most relevant document chunks for a given query.
    
    This function performs semantic similarity search in the vector store to find
    document chunks that are most relevant to the query. It uses cosine similarity
    between the query embedding and stored chunk embeddings to rank results.
    
    How Similarity Search Works:
    1. Query text is converted to an embedding vector using the same model
       that was used to embed the document chunks
    2. FAISS computes distance between query embedding and all chunk embeddings
    3. Results are ranked by distance (lower distance = more similar)
    4. Top-k most similar chunks are returned with their distance scores
    
    Distance Scores:
    - FAISS returns L2 (Euclidean) distances by default
    - Lower scores indicate greater semantic similarity (0 = identical)
    - Typical range depends on embedding dimensionality and normalization
    - Scores are relative - compare within a result set rather than using absolute thresholds
    
    Metadata Preservation:
    - All chunk metadata (source, page, chunk_id) is preserved in results
    - This enables proper citation and evidence tracing in risk findings
    - Metadata is essential for Requirements 2.2 (include source document and location)
    
    Args:
        vector_store: FAISS VectorStore instance containing embedded document chunks
        query: Search query string (e.g., "revenue growth projections")
        k: Number of most relevant chunks to retrieve (default: 5)
           Recommended range: 3-10 depending on use case
           - Lower k: More focused, higher precision
           - Higher k: Broader coverage, may include less relevant results
    
    Returns:
        List of (Document, distance_score) tuples, ordered by ascending distance
        - Document: Contains page_content (text) and metadata (source, page, chunk_id, etc.)
        - distance_score: Float indicating distance (lower = more relevant/similar)
        
    Raises:
        ValueError: If query is empty or k is not positive
        Exception: If vector store query fails
        
    Example:
        >>> results = retrieve_relevant_chunks(vector_store, "financial risks", k=5)
        >>> for doc, distance in results:
        ...     print(f"Distance: {distance:.3f} | Source: {doc.metadata['source']}")
        ...     print(f"Content: {doc.page_content[:100]}...")
        
    Requirements Validation:
    - Requirement 2.1: Retrieves most relevant chunks from vector store
    - Requirement 2.2: Includes source document name and location metadata
    """
    # Validate inputs
    if not query or not query.strip():
        raise ValueError("Query string cannot be empty")
    
    if k <= 0:
        raise ValueError(f"k must be positive, got: {k}")
    
    logger.debug(f"Retrieving top-{k} chunks for query: '{query[:50]}...'")
    
    try:
        # Perform similarity search with scores
        # similarity_search_with_score returns List[Tuple[Document, float]]
        # Documents are automatically ranked by distance score (ascending - lower is better)
        #
        # Under the hood, this:
        # 1. Generates embedding for the query using the same embeddings model
        # 2. Computes L2 distance between query embedding and all stored embeddings
        # 3. Returns top-k results sorted by distance (lowest distance = most similar)
        results = vector_store.similarity_search_with_score(
            query=query,
            k=k
        )
        
        # Log retrieval statistics
        if results:
            scores = [score for _, score in results]
            logger.info(
                f"Retrieved {len(results)} chunks | "
                f"Score range: {min(scores):.3f} - {max(scores):.3f}"
            )
            
            # Log details of top result for debugging
            top_doc, top_score = results[0]
            logger.debug(
                f"Top result: {top_doc.metadata.get('source', 'unknown')} "
                f"page {top_doc.metadata.get('page', '?')} "
                f"(score: {top_score:.3f})"
            )
        else:
            logger.warning(f"No results found for query: '{query}'")
        
        # Verify metadata is present in results (critical for citations)
        for doc, score in results:
            if 'source' not in doc.metadata:
                logger.warning(
                    f"Retrieved chunk missing 'source' metadata (score: {score:.3f})"
                )
            if 'page' not in doc.metadata:
                logger.warning(
                    f"Retrieved chunk missing 'page' metadata (score: {score:.3f})"
                )
        
        return results
        
    except Exception as e:
        error_message = str(e)
        logger.error(f"Failed to retrieve chunks: {error_message}")
        raise Exception(
            f"Vector store query failed: {error_message}. "
            f"Ensure vector store is properly initialized."
        ) from e


def format_chunks_with_citations(chunks: List[Tuple[Document, float]]) -> str:
    """
    Format retrieved document chunks with proper source citations.
    
    This function takes chunks returned from similarity search and formats them
    into a readable string with clear citations. Each chunk includes:
    - The actual text content
    - Source document name
    - Page or section number
    - Similarity score (for transparency)
    
    Citation Format:
    The function uses a structured format that makes it easy for LLMs and humans
    to identify evidence sources:
    
    [Chunk N] (Source: document.pdf, Page: 5, Score: 0.234)
    <chunk text content>
    
    Why This Format:
    - Numbered chunks: Easy to reference in analysis ("see Chunk 2")
    - Source metadata: Enables traceability to original documents
    - Page numbers: Allows verification and detailed review
    - Scores: Provides confidence indication (lower = more relevant)
    - Clear separators: Makes parsing easier for both humans and LLMs
    
    This format satisfies Requirement 2.3: "cite the specific document and 
    page/section for each piece of evidence"
    
    Args:
        chunks: List of (Document, distance_score) tuples from retrieve_relevant_chunks()
               Each Document contains page_content and metadata (source, page, chunk_id)
               
    Returns:
        Formatted string with all chunks and their citations
        Returns empty string if chunks list is empty
        
    Example Output:
        [Chunk 1] (Source: financial_summary.pdf, Page: 3, Score: 0.145)
        The company reported revenue of $2.5M in Q4 2023, representing 
        45% year-over-year growth...
        
        [Chunk 2] (Source: customer_contract.pdf, Page: 7, Score: 0.289)
        Termination clause: Either party may terminate with 30 days notice...
        
    Requirements Validation:
    - Requirement 2.3: Cites specific document and page/section for each evidence piece
    """
    # Handle empty input
    if not chunks:
        logger.debug("No chunks to format")
        return ""
    
    logger.debug(f"Formatting {len(chunks)} chunks with citations")
    
    # Build formatted output
    formatted_parts = []
    
    for idx, (doc, score) in enumerate(chunks, start=1):
        # Extract metadata with fallback values
        # Using .get() ensures we handle missing metadata gracefully
        source = doc.metadata.get('source', 'unknown_source')
        page = doc.metadata.get('page', 'unknown')
        
        # Format the citation header
        # Include chunk number for easy reference
        # Include all key metadata for full traceability
        citation = (
            f"[Chunk {idx}] "
            f"(Source: {source}, Page: {page}, Score: {score:.3f})"
        )
        
        # Get the chunk content
        # Strip whitespace to clean up formatting
        content = doc.page_content.strip()
        
        # Combine citation and content with clear separation
        # Double newline creates visual separation between chunks
        chunk_text = f"{citation}\n{content}"
        
        formatted_parts.append(chunk_text)
    
    # Join all chunks with double newlines for readability
    # This creates clear visual separation between different evidence pieces
    formatted_output = "\n\n".join(formatted_parts)
    
    logger.info(
        f"Formatted {len(chunks)} chunks into citation string "
        f"({len(formatted_output)} characters)"
    )
    
    return formatted_output
