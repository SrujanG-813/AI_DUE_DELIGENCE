# Requirements Document

## Introduction

The AI Due Diligence Engine is an MVP system that analyzes multiple business documents (contracts, financials, policies, product documentation) and generates evidence-backed investment risk memos using RAG (Retrieval-Augmented Generation) with lightweight agentic AI. The system provides structured risk analysis across financial, legal, and operational dimensions with full citation traceability.

## Glossary

- **System**: The AI Due Diligence Engine
- **Document**: A PDF or text file containing business information (contracts, financials, policies, etc.)
- **Chunk**: A segment of text extracted from a document for embedding and retrieval
- **Vector_Store**: The local FAISS or Chroma database storing document embeddings
- **Risk_Agent**: A specialized component that analyzes a specific risk category (Financial, Legal, or Operational)
- **Evidence_Reference**: A citation linking a finding to its source document and location (page/section)
- **Risk_Finding**: An identified risk with severity level and supporting evidence
- **Risk_Memo**: The final structured markdown report containing all analysis results
- **Cross_Document_Check**: A heuristic-based validation that detects inconsistencies across multiple documents
- **Risk_Score**: A numerical value (Low/Medium/High) representing overall investment risk

## Requirements

### Requirement 1: Document Ingestion

**User Story:** As a user, I want to upload multiple business documents, so that the system can analyze them for due diligence.

#### Acceptance Criteria

1. WHEN a user provides PDF or text files, THE System SHALL extract text content from each file
2. WHEN text is extracted, THE System SHALL split it into chunks suitable for embedding
3. WHEN chunks are created, THE System SHALL generate embeddings using OpenAI embeddings
4. WHEN embeddings are generated, THE System SHALL store them in the Vector_Store with document metadata
5. WHEN storing chunks, THE System SHALL preserve source document name and page/section information for citation

### Requirement 2: RAG-Based Evidence Retrieval

**User Story:** As a risk analyst, I want the system to retrieve relevant document sections when analyzing risks, so that findings are grounded in actual evidence.

#### Acceptance Criteria

1. WHEN a Risk_Agent queries for information, THE System SHALL retrieve the most relevant chunks from the Vector_Store
2. WHEN chunks are retrieved, THE System SHALL include source document name and location metadata
3. WHEN presenting findings, THE System SHALL cite the specific document and page/section for each piece of evidence
4. THE System SHALL return chunks ranked by relevance to the query

### Requirement 3: Financial Risk Analysis

**User Story:** As an investor, I want the system to analyze financial risks, so that I can understand revenue claims, growth projections, and cost structures.

#### Acceptance Criteria

1. WHEN analyzing documents, THE Financial_Risk_Agent SHALL retrieve chunks related to revenue, growth, and costs
2. WHEN financial information is found, THE Financial_Risk_Agent SHALL identify overly optimistic language
3. WHEN financial data is incomplete, THE Financial_Risk_Agent SHALL flag missing critical financial information
4. WHEN producing findings, THE Financial_Risk_Agent SHALL provide Evidence_References for each risk identified
5. THE Financial_Risk_Agent SHALL assign severity levels (Low/Medium/High) to each finding

### Requirement 4: Legal Risk Analysis

**User Story:** As a legal advisor, I want the system to analyze contract and legal risks, so that I can identify problematic clauses and obligations.

#### Acceptance Criteria

1. WHEN analyzing documents, THE Legal_Risk_Agent SHALL retrieve chunks related to contracts, termination clauses, liability, and IP ownership
2. WHEN contract terms are found, THE Legal_Risk_Agent SHALL identify one-sided or unusual clauses
3. WHEN liability terms are found, THE Legal_Risk_Agent SHALL flag inadequate liability limits
4. WHEN producing findings, THE Legal_Risk_Agent SHALL provide Evidence_References for each risk identified
5. THE Legal_Risk_Agent SHALL assign severity levels (Low/Medium/High) to each finding

### Requirement 5: Operational Risk Analysis

**User Story:** As an operations analyst, I want the system to analyze operational risks, so that I can identify dependencies, scalability issues, and single points of failure.

#### Acceptance Criteria

1. WHEN analyzing documents, THE Operational_Risk_Agent SHALL retrieve chunks related to key personnel, vendor dependencies, and scalability
2. WHEN dependencies are found, THE Operational_Risk_Agent SHALL identify single points of failure
3. WHEN vendor information is found, THE Operational_Risk_Agent SHALL flag vendor lock-in risks
4. WHEN producing findings, THE Operational_Risk_Agent SHALL provide Evidence_References for each risk identified
5. THE Operational_Risk_Agent SHALL assign severity levels (Low/Medium/High) to each finding

### Requirement 6: Cross-Document Inconsistency Detection

**User Story:** As a due diligence analyst, I want the system to detect inconsistencies across documents, so that I can identify contradictions and discrepancies.

#### Acceptance Criteria

1. WHEN multiple documents contain financial claims, THE System SHALL check for revenue mismatches
2. WHEN multiple documents reference IP ownership, THE System SHALL check for ownership conflicts
3. WHEN documents contain scalability claims and vendor dependencies, THE System SHALL check for contradictions
4. WHEN inconsistencies are detected, THE System SHALL report the issue description, involved documents, and severity level
5. THE System SHALL use rule-based heuristics for inconsistency detection

### Requirement 7: Risk Score Calculation

**User Story:** As an investor, I want an overall risk score, so that I can quickly assess the investment risk level.

#### Acceptance Criteria

1. WHEN calculating risk score, THE System SHALL assign 3 points for each High-risk finding
2. WHEN calculating risk score, THE System SHALL assign 2 points for each Medium-risk finding
3. WHEN calculating risk score, THE System SHALL assign 1 point for each Low-risk finding
4. WHEN the total score is calculated, THE System SHALL classify overall risk as Low, Medium, or High
5. THE System SHALL include the risk score in the final Risk_Memo

### Requirement 8: Investment Risk Memo Generation

**User Story:** As a decision maker, I want a structured investment risk memo, so that I can review all findings in a clear, organized format.

#### Acceptance Criteria

1. WHEN generating the Risk_Memo, THE System SHALL include an Executive Summary section
2. WHEN generating the Risk_Memo, THE System SHALL include a Risk Breakdown section organized by category
3. WHEN generating the Risk_Memo, THE System SHALL include a Key Red Flags section highlighting critical issues
4. WHEN generating the Risk_Memo, THE System SHALL include an Evidence References section with all citations
5. WHEN generating the Risk_Memo, THE System SHALL include a Final Risk Score with classification
6. THE System SHALL output the Risk_Memo in structured markdown format

### Requirement 9: System Architecture and Modularity

**User Story:** As a developer, I want the codebase to be modular and well-organized, so that I can understand and extend the system easily.

#### Acceptance Criteria

1. THE System SHALL separate document ingestion logic into a dedicated module
2. THE System SHALL separate retrieval logic into a dedicated module
3. THE System SHALL separate agent logic into a dedicated module
4. THE System SHALL separate cross-document checking logic into a dedicated module
5. THE System SHALL separate report generation logic into a dedicated module
6. THE System SHALL provide a main orchestration module that coordinates all components
7. THE System SHALL include thorough code comments for beginner readability

### Requirement 10: Command-Line Interface

**User Story:** As a user, I want to run the system from the command line, so that I can analyze documents without complex setup.

#### Acceptance Criteria

1. WHEN a user runs the main script, THE System SHALL accept document file paths as input
2. WHEN documents are provided, THE System SHALL process them and generate the Risk_Memo
3. WHEN processing is complete, THE System SHALL output the Risk_Memo to the console or file
4. THE System SHALL provide clear feedback during processing stages

### Requirement 11: Sample Data Provision

**User Story:** As a new user, I want sample documents included, so that I can test the system immediately.

#### Acceptance Criteria

1. THE System SHALL include a sample financial summary document
2. THE System SHALL include a sample customer contract document
3. THE System SHALL include a sample internal policy document
4. THE System SHALL store sample documents in the data/sample_docs directory
5. THE System SHALL ensure sample documents are realistic but fictional
