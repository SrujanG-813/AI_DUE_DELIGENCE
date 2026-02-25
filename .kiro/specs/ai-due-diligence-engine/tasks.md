# Implementation Plan: AI Due Diligence Engine

## Overview

This implementation plan breaks down the AI Due Diligence Engine into incremental, testable steps. The approach follows a bottom-up strategy: build core utilities first, then agents, then orchestration. Each major component includes property-based tests to validate correctness properties from the design document.

## Tasks

- [x] 1. Set up project structure and dependencies
  - Create directory structure: `ai_due_diligence/`, `data/sample_docs/`, `tests/`, `tests/property_tests/`, `tests/fixtures/`
  - Create `requirements.txt` with dependencies: langchain, openai, faiss-cpu, pypdf2, hypothesis, pytest
  - Create `.env.example` for OpenAI API key configuration
  - Create basic `README.md` with setup instructions
  - _Requirements: 9.1, 9.2, 9.3, 9.4, 9.5, 9.6_

- [ ] 2. Implement document ingestion module (ingest.py)
  - [x] 2.1 Implement document loading functions
    - Write `load_documents()` to handle PDF and text files
    - Use PyPDF2 for PDF extraction with page tracking
    - Handle encoding issues (UTF-8 with latin-1 fallback)
    - Include error handling for invalid files
    - Add detailed comments explaining extraction logic
    - _Requirements: 1.1_
  
  - [ ]* 2.2 Write property test for text extraction
    - **Property 1: Text Extraction Produces Content**
    - **Validates: Requirements 1.1**
  
  - [x] 2.3 Implement text chunking function
    - Write `chunk_documents()` with configurable chunk_size and overlap
    - Preserve metadata (source, page, chunk_id) for each chunk
    - Use LangChain's RecursiveCharacterTextSplitter
    - Add comments explaining chunking strategy
    - _Requirements: 1.2, 1.5_
  
  - [ ]* 2.4 Write property test for chunking constraints
    - **Property 2: Chunking Respects Size Constraints**
    - **Validates: Requirements 1.2**
  
  - [x] 2.5 Implement vector store creation
    - Write `create_vector_store()` using FAISS
    - Initialize OpenAI embeddings
    - Store chunks with metadata preservation
    - Add FAISS persistence to disk
    - Include retry logic for API failures with exponential backoff
    - Add comments explaining embedding and storage process
    - _Requirements: 1.3, 1.4_
  
  - [ ]* 2.6 Write property test for embedding generation
    - **Property 3: Embedding Generation Completeness**
    - **Validates: Requirements 1.3**
  
  - [ ]* 2.7 Write property test for metadata preservation
    - **Property 4: Metadata Preservation Round-Trip**
    - **Validates: Requirements 1.4, 1.5, 2.2**

- [ ] 3. Implement retrieval module (retriever.py)
  - [x] 3.1 Implement vector similarity search
    - Write `retrieve_relevant_chunks()` with configurable k parameter
    - Return chunks with similarity scores
    - Ensure metadata is included in results
    - Add comments explaining retrieval process
    - _Requirements: 2.1, 2.2_
  
  - [x] 3.2 Implement citation formatting
    - Write `format_chunks_with_citations()` to format chunks with source info
    - Include document name, page/section in formatted output
    - Add comments explaining citation format
    - _Requirements: 2.3_
  
  - [ ]* 3.3 Write property test for retrieval ranking
    - **Property 5: Retrieval Returns Ranked Results**
    - **Validates: Requirements 2.1, 2.4**

- [x] 4. Checkpoint - Verify ingestion and retrieval
  - Ensure all tests pass, ask the user if questions arise.

- [ ] 5. Implement risk analysis agents (agents.py)
  - [x] 5.1 Create base RiskAgent class
    - Define `__init__()` with agent_type, llm, vector_store parameters
    - Define abstract `analyze()` method structure
    - Create RiskFinding dataclass with all required fields
    - Add detailed comments explaining agent architecture
    - _Requirements: 3.4, 3.5, 4.4, 4.5, 5.4, 5.5_
  
  - [x] 5.2 Implement FinancialRiskAgent
    - Define query templates for revenue, growth, costs, financial data
    - Implement `analyze()` to retrieve chunks and call LLM
    - Create LLM prompt for financial risk analysis
    - Parse LLM JSON response into RiskFinding objects
    - Handle parsing errors gracefully
    - Add comments explaining financial risk focus areas
    - _Requirements: 3.1, 3.2, 3.3, 3.4, 3.5_
  
  - [x] 5.3 Implement LegalRiskAgent
    - Define query templates for contracts, termination, liability, IP
    - Implement `analyze()` to retrieve chunks and call LLM
    - Create LLM prompt for legal risk analysis
    - Parse LLM JSON response into RiskFinding objects
    - Add comments explaining legal risk focus areas
    - _Requirements: 4.1, 4.2, 4.3, 4.4, 4.5_
  
  - [x] 5.4 Implement OperationalRiskAgent
    - Define query templates for personnel, vendors, scalability
    - Implement `analyze()` to retrieve chunks and call LLM
    - Create LLM prompt for operational risk analysis
    - Parse LLM JSON response into RiskFinding objects
    - Add comments explaining operational risk focus areas
    - _Requirements: 5.1, 5.2, 5.3, 5.4, 5.5_
  
  - [ ]* 5.5 Write property test for finding structure
    - **Property 6: Risk Findings Have Required Structure**
    - **Validates: Requirements 2.3, 3.4, 3.5, 4.4, 4.5, 5.4, 5.5**
  
  - [ ]* 5.6 Write unit tests for agent behavior
    - Test each agent with mock LLM responses
    - Test handling of empty retrieval results
    - Test parsing of malformed LLM responses
    - _Requirements: 3.1, 4.1, 5.1_

- [ ] 6. Implement cross-document checks (cross_checks.py)
  - [x] 6.1 Create Inconsistency dataclass
    - Define fields: issue_description, documents_involved, severity, details
    - Add comments explaining inconsistency structure
    - _Requirements: 6.4_
  
  - [x] 6.2 Implement revenue consistency check
    - Write `check_revenue_consistency()` to extract and compare revenue figures
    - Use regex or simple parsing to find numeric values
    - Flag discrepancies > 10%
    - Add comments explaining heuristic logic
    - _Requirements: 6.1, 6.5_
  
  - [x] 6.3 Implement IP ownership conflict check
    - Write `check_ip_ownership_conflicts()` to find ownership statements
    - Use keyword matching for IP-related terms
    - Flag conflicting ownership claims
    - Add comments explaining detection logic
    - _Requirements: 6.2, 6.5_
  
  - [x] 6.4 Implement scalability-vendor contradiction check
    - Write `check_scalability_vendor_conflicts()` to find contradictions
    - Use keyword matching for scalability and vendor lock-in terms
    - Flag contradictory statements
    - Add comments explaining detection logic
    - _Requirements: 6.3, 6.5_
  
  - [x] 6.5 Create orchestration function for all checks
    - Write `run_all_checks()` to execute all cross-document checks
    - Handle missing data gracefully
    - Return list of all detected inconsistencies
    - _Requirements: 6.1, 6.2, 6.3_
  
  - [ ]* 6.6 Write property test for inconsistency structure
    - **Property 7: Inconsistencies Have Required Structure**
    - **Validates: Requirements 6.4**
  
  - [ ]* 6.7 Write unit tests for cross-document checks
    - Test revenue mismatch detection with known discrepancies
    - Test IP conflict detection with known conflicts
    - Test scalability contradiction detection
    - _Requirements: 6.1, 6.2, 6.3_

- [x] 7. Checkpoint - Verify agents and cross-checks
  - Ensure all tests pass, ask the user if questions arise.

- [x] 8. Implement report generation (report.py)
  - [x] 8.1 Implement risk score calculation
    - Write `calculate_risk_score()` with scoring rules (High=3, Medium=2, Low=1)
    - Implement classification logic (0-5=Low, 6-12=Medium, 13+=High)
    - Handle empty findings list
    - Add comments explaining scoring algorithm
    - _Requirements: 7.1, 7.2, 7.3, 7.4, 7.5_
  
  - [ ]* 8.2 Write property test for risk scoring
    - **Property 8: Risk Score Calculation Correctness**
    - **Validates: Requirements 7.1, 7.2, 7.3, 7.4, 7.5**
  
  - [x] 8.3 Implement risk memo generation
    - Write `generate_risk_memo()` to create structured markdown
    - Include all required sections: Executive Summary, Risk Breakdown, Key Red Flags, Evidence References, Final Risk Score
    - Format findings by category (Financial, Legal, Operational)
    - Extract top 3-5 critical issues for Key Red Flags
    - Compile all citations for Evidence References section
    - Add comments explaining memo structure
    - _Requirements: 8.1, 8.2, 8.3, 8.4, 8.5, 8.6_
  
  - [ ]* 8.4 Write property test for memo completeness
    - **Property 9: Risk Memo Completeness**
    - **Validates: Requirements 8.1, 8.2, 8.3, 8.4, 8.5, 8.6**
  
  - [ ]* 8.5 Write unit tests for report generation
    - Test memo with complete data
    - Test memo with missing categories
    - Test markdown formatting validity
    - Test boundary cases for risk scoring
    - _Requirements: 7.1, 7.2, 7.3, 7.4, 8.1, 8.2, 8.3, 8.4, 8.5, 8.6_

- [x] 9. Implement main orchestration (main.py)
  - [x] 9.1 Create main pipeline function
    - Write `main()` to orchestrate entire analysis pipeline
    - Implement step-by-step execution: ingestion → agents → cross-checks → report
    - Add progress feedback for each stage
    - Handle errors at each stage gracefully
    - Write output to file and optionally print to console
    - Add detailed comments explaining orchestration flow
    - _Requirements: 9.6, 10.2, 10.3_
  
  - [x] 9.2 Implement CLI argument parsing
    - Use argparse to accept document file paths
    - Add optional output path argument
    - Add help text and usage examples
    - _Requirements: 10.1_
  
  - [x] 9.3 Add configuration loading
    - Load OpenAI API key from environment variable
    - Validate API key is present
    - Provide clear error message if missing
    - _Requirements: 10.1_
  
  - [ ]* 9.4 Write property test for end-to-end processing
    - **Property 10: End-to-End Processing Succeeds**
    - **Validates: Requirements 10.2**
  
  - [ ]* 9.5 Write integration tests
    - Test complete pipeline with sample documents
    - Verify all agents produce findings
    - Verify memo generation succeeds
    - _Requirements: 10.2, 10.3_

- [x] 10. Create sample documents
  - [x] 10.1 Create sample financial summary
    - Write realistic financial document with revenue, growth, costs
    - Include some optimistic language and missing data points
    - Save as `data/sample_docs/financial_summary.txt`
    - _Requirements: 11.1, 11.4, 11.5_
  
  - [x] 10.2 Create sample customer contract
    - Write realistic contract with termination clauses, liability, IP terms
    - Include some one-sided clauses
    - Save as `data/sample_docs/customer_contract.txt`
    - _Requirements: 11.2, 11.4, 11.5_
  
  - [x] 10.3 Create sample internal policy
    - Write realistic policy document with personnel, vendor, scalability info
    - Include some single points of failure
    - Save as `data/sample_docs/internal_policy.txt`
    - _Requirements: 11.3, 11.4, 11.5_
  
  - [x] 10.4 Add intentional inconsistencies across documents
    - Ensure revenue figures differ between financial summary and contract
    - Ensure IP ownership statements conflict
    - Ensure scalability claims contradict vendor dependencies
    - _Requirements: 6.1, 6.2, 6.3_

- [ ] 11. Create documentation and finalize
  - [x] 11.1 Write comprehensive README
    - Add project overview and features
    - Add setup instructions (dependencies, API key)
    - Add usage examples with sample commands
    - Add architecture overview
    - Add troubleshooting section
    - _Requirements: 9.7, 10.1_
  
  - [x] 11.2 Add inline code comments
    - Review all modules for comment completeness
    - Ensure beginner-friendly explanations
    - Add docstrings to all functions and classes
    - _Requirements: 9.7_
  
  - [x] 11.3 Create example output
    - Run system with sample documents
    - Save generated memo as `examples/sample_risk_memo.md`
    - Include in README as example output
    - _Requirements: 10.2, 10.3_

- [x] 12. Final checkpoint - Complete system validation
  - Run all unit tests and property tests
  - Run end-to-end test with sample documents
  - Verify generated memo has all required sections
  - Ensure all tests pass, ask the user if questions arise.

## Notes

- Tasks marked with `*` are optional and can be skipped for faster MVP
- Each task references specific requirements for traceability
- Property tests validate universal correctness properties from the design document
- Unit tests validate specific examples and edge cases
- The implementation follows a bottom-up approach: utilities → agents → orchestration
- All code should include thorough comments for beginner readability
- Sample documents should contain intentional issues to demonstrate system capabilities
