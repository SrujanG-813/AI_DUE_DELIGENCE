"""
AI Due Diligence Engine - Main Orchestration Module

This module provides the main entry point for the AI Due Diligence Engine.
It orchestrates the entire analysis pipeline from document ingestion through
risk analysis to final report generation.

The pipeline follows these stages:
1. Document Ingestion: Load, chunk, and embed documents into vector store
2. Risk Analysis: Run specialized agents (Financial, Legal, Operational)
3. Cross-Document Checks: Detect inconsistencies across documents
4. Risk Scoring: Calculate overall risk score and classification
5. Report Generation: Create structured markdown risk memo

Usage:
    python main.py document1.pdf document2.txt document3.pdf
    python main.py --output custom_memo.md data/sample_docs/*.pdf
    python main.py --help
"""

import os
import sys
import argparse
import logging
from typing import List

# Import all required modules from the AI Due Diligence Engine
from ai_due_diligence.ingest import load_documents, chunk_documents, create_vector_store
from ai_due_diligence.agents import FinancialRiskAgent, LegalRiskAgent, OperationalRiskAgent
from ai_due_diligence.cross_checks import run_all_checks
from ai_due_diligence.report import calculate_risk_score, generate_risk_memo

# LangChain imports for LLM and embeddings
from langchain_openai import ChatOpenAI, OpenAIEmbeddings


# Configure logging for the application
# This provides visibility into the pipeline execution and helps with debugging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def main(document_paths: List[str], output_path: str = "risk_memo.md") -> None:
    """
    Main orchestration function for the AI Due Diligence Engine.
    
    This function coordinates the entire analysis pipeline, executing each stage
    in sequence and handling errors gracefully at each step. It provides progress
    feedback to the user and ensures that the final risk memo is generated even
    if some stages encounter issues.
    
    Pipeline Stages:
    
    1. Document Ingestion
       - Load documents from file paths (PDF and text files)
       - Extract text content with page tracking
       - Split into chunks for embedding (1000 chars with 200 char overlap)
       - Generate embeddings using OpenAI text-embedding-ada-002
       - Create FAISS vector store for similarity search
    
    2. Risk Agent Analysis
       - Financial Risk Agent: Analyzes revenue, growth, costs
       - Legal Risk Agent: Analyzes contracts, liability, IP
       - Operational Risk Agent: Analyzes personnel, vendors, scalability
       - Each agent queries vector store and uses LLM to identify risks
    
    3. Cross-Document Checks
       - Revenue consistency check: Detects revenue mismatches
       - IP ownership conflict check: Detects conflicting IP claims
       - Scalability-vendor check: Detects contradictions
    
    4. Risk Scoring
       - Calculate total risk score (High=3, Medium=2, Low=1 points)
       - Classify overall risk (Low: 0-5, Medium: 6-12, High: 13+)
    
    5. Report Generation
       - Generate structured markdown memo with all findings
       - Include Executive Summary, Risk Breakdown, Key Red Flags,
         Evidence References, and Final Risk Score
       - Write to output file and optionally print to console
    
    Error Handling:
    - Each stage is wrapped in try-except to handle errors gracefully
    - If a stage fails, a clear error message is displayed
    - The pipeline attempts to continue with remaining stages when possible
    - Critical failures (e.g., no documents loaded) will stop execution
    
    Progress Feedback:
    - Each stage prints a status message before execution
    - Completion messages show results (e.g., "Found 5 financial risks")
    - Final summary shows overall risk assessment
    
    Args:
        document_paths: List of file paths to analyze (PDF or text files)
        output_path: Path where the risk memo should be saved (default: "risk_memo.md")
    
    Returns:
        None. Writes risk memo to output_path and prints summary to console.
    
    Raises:
        SystemExit: If critical errors occur (missing API key, no documents loaded, etc.)
    
    Example:
        main(
            document_paths=["financial.pdf", "contract.txt", "policy.pdf"],
            output_path="investment_risk_memo.md"
        )
    
    Requirements Validation:
    - Requirement 9.6: Orchestrates entire analysis pipeline
    - Requirement 10.2: Processes documents and generates risk memo
    - Requirement 10.3: Outputs memo to file
    """
    
    print("=" * 80)
    print("AI Due Diligence Engine")
    print("=" * 80)
    print()
    
    # -------------------------------------------------------------------------
    # Stage 1: Document Ingestion
    # -------------------------------------------------------------------------
    print("Stage 1: Document Ingestion")
    print("-" * 80)
    
    try:
        # Step 1.1: Load documents from file paths
        print(f"Loading {len(document_paths)} document(s)...")
        documents = load_documents(document_paths)
        print(f"✓ Successfully loaded {len(documents)} document pages/sections")
        print()
        
    except Exception as e:
        logger.error(f"Failed to load documents: {str(e)}")
        print(f"✗ Error: Could not load documents - {str(e)}")
        print("Please check that the file paths are correct and files are readable.")
        sys.exit(1)
    
    try:
        # Step 1.2: Chunk documents for embedding
        print("Chunking documents...")
        chunks = chunk_documents(documents, chunk_size=1000, chunk_overlap=200)
        print(f"✓ Created {len(chunks)} chunks for embedding")
        print()
        
    except Exception as e:
        logger.error(f"Failed to chunk documents: {str(e)}")
        print(f"✗ Error: Could not chunk documents - {str(e)}")
        sys.exit(1)
    
    try:
        # Step 1.3: Create vector store with embeddings
        print("Generating embeddings and creating vector store...")
        print("(This may take a moment depending on document size)")
        
        # Initialize OpenAI embeddings model
        embeddings = OpenAIEmbeddings(model="text-embedding-ada-002")
        
        # Create FAISS vector store
        vector_store = create_vector_store(chunks, embeddings, persist_directory="vector_store")
        print(f"✓ Vector store created with {len(chunks)} embeddings")
        print()
        
    except Exception as e:
        logger.error(f"Failed to create vector store: {str(e)}")
        print(f"✗ Error: Could not create vector store - {str(e)}")
        print("Please check your OpenAI API key and network connection.")
        sys.exit(1)
    
    # -------------------------------------------------------------------------
    # Stage 2: Risk Agent Analysis
    # -------------------------------------------------------------------------
    print("Stage 2: Risk Agent Analysis")
    print("-" * 80)
    
    # Initialize the LLM for risk analysis
    # Using GPT-4 for high-quality analysis, temperature=0 for consistency
    try:
        print("Initializing LLM for risk analysis...")
        llm = ChatOpenAI(model="gpt-4", temperature=0)
        print("✓ LLM initialized")
        print()
    except Exception as e:
        logger.error(f"Failed to initialize LLM: {str(e)}")
        print(f"✗ Error: Could not initialize LLM - {str(e)}")
        print("Please check your OpenAI API key.")
        sys.exit(1)
    
    # Run Financial Risk Agent
    try:
        print("Analyzing financial risks...")
        financial_agent = FinancialRiskAgent(llm=llm, vector_store=vector_store)
        financial_findings = financial_agent.analyze()
        print(f"✓ Identified {len(financial_findings)} financial risk(s)")
        
        # Show severity breakdown
        if financial_findings:
            high = sum(1 for f in financial_findings if f.severity == "High")
            medium = sum(1 for f in financial_findings if f.severity == "Medium")
            low = sum(1 for f in financial_findings if f.severity == "Low")
            print(f"  ({high} High, {medium} Medium, {low} Low)")
        print()
        
    except Exception as e:
        logger.error(f"Financial risk analysis failed: {str(e)}")
        print(f"✗ Warning: Financial risk analysis failed - {str(e)}")
        print("  Continuing with other agents...")
        financial_findings = []
        print()
    
    # Run Legal Risk Agent
    try:
        print("Analyzing legal risks...")
        legal_agent = LegalRiskAgent(llm=llm, vector_store=vector_store)
        legal_findings = legal_agent.analyze()
        print(f"✓ Identified {len(legal_findings)} legal risk(s)")
        
        # Show severity breakdown
        if legal_findings:
            high = sum(1 for f in legal_findings if f.severity == "High")
            medium = sum(1 for f in legal_findings if f.severity == "Medium")
            low = sum(1 for f in legal_findings if f.severity == "Low")
            print(f"  ({high} High, {medium} Medium, {low} Low)")
        print()
        
    except Exception as e:
        logger.error(f"Legal risk analysis failed: {str(e)}")
        print(f"✗ Warning: Legal risk analysis failed - {str(e)}")
        print("  Continuing with other agents...")
        legal_findings = []
        print()
    
    # Run Operational Risk Agent
    try:
        print("Analyzing operational risks...")
        operational_agent = OperationalRiskAgent(llm=llm, vector_store=vector_store)
        operational_findings = operational_agent.analyze()
        print(f"✓ Identified {len(operational_findings)} operational risk(s)")
        
        # Show severity breakdown
        if operational_findings:
            high = sum(1 for f in operational_findings if f.severity == "High")
            medium = sum(1 for f in operational_findings if f.severity == "Medium")
            low = sum(1 for f in operational_findings if f.severity == "Low")
            print(f"  ({high} High, {medium} Medium, {low} Low)")
        print()
        
    except Exception as e:
        logger.error(f"Operational risk analysis failed: {str(e)}")
        print(f"✗ Warning: Operational risk analysis failed - {str(e)}")
        print("  Continuing with remaining stages...")
        operational_findings = []
        print()
    
    # -------------------------------------------------------------------------
    # Stage 3: Cross-Document Checks
    # -------------------------------------------------------------------------
    print("Stage 3: Cross-Document Consistency Checks")
    print("-" * 80)
    
    try:
        # Combine all findings for cross-document analysis
        all_findings = financial_findings + legal_findings + operational_findings
        
        print("Running cross-document consistency checks...")
        inconsistencies = run_all_checks(all_findings, vector_store)
        print(f"✓ Detected {len(inconsistencies)} cross-document inconsistenc(ies)")
        
        # Show severity breakdown
        if inconsistencies:
            high = sum(1 for i in inconsistencies if i.severity == "High")
            medium = sum(1 for i in inconsistencies if i.severity == "Medium")
            low = sum(1 for i in inconsistencies if i.severity == "Low")
            print(f"  ({high} High, {medium} Medium, {low} Low)")
        print()
        
    except Exception as e:
        logger.error(f"Cross-document checks failed: {str(e)}")
        print(f"✗ Warning: Cross-document checks failed - {str(e)}")
        print("  Continuing with report generation...")
        inconsistencies = []
        print()
    
    # -------------------------------------------------------------------------
    # Stage 4: Risk Scoring
    # -------------------------------------------------------------------------
    print("Stage 4: Risk Score Calculation")
    print("-" * 80)
    
    try:
        print("Calculating overall risk score...")
        risk_score, risk_classification = calculate_risk_score(
            findings=all_findings,
            inconsistencies=inconsistencies
        )
        print(f"✓ Risk Score: {risk_score} ({risk_classification} Risk)")
        print()
        
    except Exception as e:
        logger.error(f"Risk score calculation failed: {str(e)}")
        print(f"✗ Warning: Risk score calculation failed - {str(e)}")
        print("  Using default values...")
        risk_score = 0
        risk_classification = "Unknown"
        print()
    
    # -------------------------------------------------------------------------
    # Stage 5: Report Generation
    # -------------------------------------------------------------------------
    print("Stage 5: Report Generation")
    print("-" * 80)
    
    try:
        print("Generating investment risk memo...")
        memo = generate_risk_memo(
            financial_findings=financial_findings,
            legal_findings=legal_findings,
            operational_findings=operational_findings,
            inconsistencies=inconsistencies,
            risk_score=risk_score,
            risk_classification=risk_classification
        )
        print(f"✓ Risk memo generated ({len(memo)} characters)")
        print()
        
    except Exception as e:
        logger.error(f"Report generation failed: {str(e)}")
        print(f"✗ Error: Could not generate risk memo - {str(e)}")
        sys.exit(1)
    
    # -------------------------------------------------------------------------
    # Stage 6: Output
    # -------------------------------------------------------------------------
    print("Stage 6: Output")
    print("-" * 80)
    
    try:
        # Write memo to file
        print(f"Writing risk memo to: {output_path}")
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(memo)
        print(f"✓ Risk memo saved successfully")
        print()
        
    except Exception as e:
        logger.error(f"Failed to write output file: {str(e)}")
        print(f"✗ Warning: Could not write to file - {str(e)}")
        print("Printing memo to console instead:")
        print()
        print(memo)
        print()
    
    # -------------------------------------------------------------------------
    # Final Summary
    # -------------------------------------------------------------------------
    print("=" * 80)
    print("Analysis Complete")
    print("=" * 80)
    print()
    print(f"Overall Risk Assessment: {risk_classification} Risk (Score: {risk_score})")
    print(f"Total Findings: {len(all_findings)} risks, {len(inconsistencies)} inconsistencies")
    print(f"Output: {output_path}")
    print()
    
    # Provide recommendation based on risk level
    if risk_classification == "High":
        print("⚠️  RECOMMENDATION: Serious concerns identified. Thorough review recommended before proceeding.")
    elif risk_classification == "Medium":
        print("⚠️  RECOMMENDATION: Notable concerns identified. Further investigation recommended.")
    else:
        print("✓ RECOMMENDATION: Standard due diligence concerns only. Investment appears relatively safe.")
    
    print()
    print("Thank you for using the AI Due Diligence Engine!")
    print()


def parse_arguments() -> argparse.Namespace:
    """
    Parse command-line arguments for the AI Due Diligence Engine.
    
    This function sets up the argument parser with all supported options,
    provides help text and usage examples, and validates the provided arguments.
    
    Arguments:
    - document_paths (positional): One or more file paths to analyze
    - --output, -o (optional): Path for the output risk memo (default: risk_memo.md)
    
    Returns:
        argparse.Namespace containing parsed arguments
    
    Example Usage:
        python main.py document1.pdf document2.txt
        python main.py --output custom_memo.md data/*.pdf
        python main.py -o report.md financial.pdf contract.txt policy.pdf
    
    Requirements Validation:
    - Requirement 10.1: Accepts document file paths as input
    """
    parser = argparse.ArgumentParser(
        description="AI Due Diligence Engine - Automated investment risk analysis",
        epilog="""
Examples:
  # Analyze sample documents with default output
  python main.py data/sample_docs/financial_summary.txt data/sample_docs/customer_contract.txt
  
  # Analyze documents with custom output path
  python main.py --output my_risk_memo.md document1.pdf document2.txt
  
  # Analyze all PDFs in a directory
  python main.py data/sample_docs/*.pdf
  
  # Short form with multiple documents
  python main.py -o report.md financial.pdf contract.txt policy.pdf

For more information, see README.md
        """,
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    
    # Positional argument: document file paths
    parser.add_argument(
        'document_paths',
        nargs='+',  # Require at least one document path
        metavar='DOCUMENT',
        help='Path(s) to document files to analyze (PDF or text files). '
             'Multiple documents can be provided separated by spaces.'
    )
    
    # Optional argument: output path
    parser.add_argument(
        '--output', '-o',
        dest='output_path',
        default='risk_memo.md',
        metavar='PATH',
        help='Path where the risk memo should be saved (default: risk_memo.md). '
             'The memo will be generated in markdown format.'
    )
    
    # Parse and return arguments
    args = parser.parse_args()
    
    return args


def load_configuration() -> None:
    """
    Load and validate configuration from environment variables.
    
    This function checks for required environment variables (OpenAI API key)
    and validates that they are present. It provides clear error messages
    if configuration is missing or invalid.
    
    Required Environment Variables:
    - OPENAI_API_KEY: API key for OpenAI services (embeddings and LLM)
    
    The function will exit the program with a clear error message if the
    API key is not found, guiding the user on how to set it up.
    
    Configuration Sources:
    1. Environment variable: OPENAI_API_KEY
    2. .env file (loaded automatically by python-dotenv if installed)
    
    Returns:
        None. Exits program if configuration is invalid.
    
    Raises:
        SystemExit: If OPENAI_API_KEY is not set
    
    Requirements Validation:
    - Requirement 10.1: Loads OpenAI API key from environment variable
    """
    # Try to load .env file if python-dotenv is available
    # This is optional - users can also set environment variables directly
    try:
        from dotenv import load_dotenv
        load_dotenv()
    except ImportError:
        # python-dotenv not installed, that's okay
        # User can still set environment variables manually
        pass
    
    # Check for OpenAI API key
    api_key = os.getenv('OPENAI_API_KEY')
    
    if not api_key:
        print("=" * 80)
        print("Configuration Error: OpenAI API Key Not Found")
        print("=" * 80)
        print()
        print("The AI Due Diligence Engine requires an OpenAI API key to function.")
        print()
        print("To set up your API key:")
        print()
        print("Option 1: Set environment variable")
        print("  export OPENAI_API_KEY='your-api-key-here'  # Linux/Mac")
        print("  set OPENAI_API_KEY=your-api-key-here       # Windows CMD")
        print("  $env:OPENAI_API_KEY='your-api-key-here'    # Windows PowerShell")
        print()
        print("Option 2: Create a .env file")
        print("  1. Copy .env.example to .env")
        print("  2. Edit .env and add your API key:")
        print("     OPENAI_API_KEY=your-api-key-here")
        print()
        print("To get an API key:")
        print("  1. Visit https://platform.openai.com/api-keys")
        print("  2. Sign in or create an account")
        print("  3. Create a new API key")
        print()
        sys.exit(1)
    
    # Validate API key format (basic check)
    if not api_key.startswith('sk-'):
        print("=" * 80)
        print("Configuration Warning: API Key Format")
        print("=" * 80)
        print()
        print("The provided OpenAI API key does not start with 'sk-'.")
        print("This may indicate an invalid or incorrectly formatted key.")
        print()
        print("Please verify your API key at: https://platform.openai.com/api-keys")
        print()
        print("Continuing anyway, but API calls may fail...")
        print()
    
    logger.info("Configuration loaded successfully")


# Entry point for the script
if __name__ == "__main__":
    # Parse command-line arguments first (allows --help to work without API key)
    args = parse_arguments()
    
    # Load and validate configuration (API keys, etc.)
    load_configuration()
    
    # Run the main pipeline
    main(
        document_paths=args.document_paths,
        output_path=args.output_path
    )
