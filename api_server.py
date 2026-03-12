"""
FastAPI Backend Server for AI Due Diligence Engine

This module provides a REST API interface for the AI Due Diligence Engine,
allowing the React frontend to communicate with the Python backend.
"""

from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles
from typing import List
import tempfile
import os
import shutil
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

from ai_due_diligence.ingest import load_documents, chunk_documents, create_vector_store
from ai_due_diligence.agents import FinancialRiskAgent, LegalRiskAgent, OperationalRiskAgent
from ai_due_diligence.cross_checks import run_all_checks
from ai_due_diligence.report import calculate_risk_score, generate_risk_memo

# Support both OpenAI and Mistral
try:
    from langchain_openai import ChatOpenAI, OpenAIEmbeddings
    OPENAI_AVAILABLE = True
except ImportError:
    OPENAI_AVAILABLE = False

try:
    from langchain_mistralai import ChatMistralAI
    MISTRAL_AVAILABLE = True
except ImportError:
    MISTRAL_AVAILABLE = False

# Import our free embeddings
from ai_due_diligence.free_embeddings import FreeEmbeddings

# Initialize FastAPI app
app = FastAPI(
    title="AI Due Diligence Engine API",
    description="REST API for AI-powered investment risk analysis",
    version="2.0.0"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins for Railway deployment
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Serve static files from frontend build
frontend_build_path = Path(__file__).parent / "frontend" / "dist"
if frontend_build_path.exists():
    app.mount("/static", StaticFiles(directory=str(frontend_build_path / "assets")), name="static")
    app.mount("/", StaticFiles(directory=str(frontend_build_path), html=True), name="frontend")


@app.get("/")
async def root():
    """Root endpoint - API health check"""
    return {
        "message": "AI Due Diligence Engine API",
        "version": "2.0.0",
        "status": "operational"
    }


@app.get("/api/health")
async def health_check():
    """Health check endpoint"""
    # Check which AI provider is configured
    mistral_key = os.getenv("MISTRAL_API_KEY")
    
    provider = None
    if mistral_key:
        provider = "Mistral AI (with free TF-IDF embeddings)"
    
    return {
        "status": "healthy",
        "api_key_configured": bool(mistral_key),
        "provider": provider,
        "message": f"API is operational with {provider}" if provider else "Mistral API key required"
    }


@app.post("/api/analyze")
async def analyze_documents(files: List[UploadFile] = File(...)):
    """
    Analyze uploaded documents and generate risk assessment.
    
    This endpoint:
    1. Receives uploaded files from the frontend
    2. Saves them temporarily
    3. Runs the complete analysis pipeline
    4. Returns structured results
    
    Args:
        files: List of uploaded files (PDF or TXT)
    
    Returns:
        JSON response with analysis results including:
        - documents_loaded: Number of documents processed
        - chunks_created: Number of text chunks created
        - financial_findings: List of financial risk findings
        - legal_findings: List of legal risk findings
        - operational_findings: List of operational risk findings
        - inconsistencies: List of cross-document inconsistencies
        - risk_score: Numerical risk score
        - risk_classification: Overall risk level (Low/Medium/High)
        - memo: Complete markdown risk memo
    """
    
    # Check if API key is configured - only need Mistral for free deployment
    mistral_key = os.getenv("MISTRAL_API_KEY")
    
    if not mistral_key:
        raise HTTPException(
            status_code=500,
            detail="Mistral API key required. Please set MISTRAL_API_KEY environment variable. Get a free key at https://console.mistral.ai/"
        )
    
    # Validate files
    if not files:
        raise HTTPException(status_code=400, detail="No files uploaded")
    
    if len(files) > 10:
        raise HTTPException(status_code=400, detail="Maximum 10 files allowed")
    
    # Create temporary directory for uploaded files
    temp_dir = tempfile.mkdtemp()
    file_paths = []
    
    try:
        # Save uploaded files
        for uploaded_file in files:
            # Validate file type
            if not uploaded_file.filename.endswith(('.pdf', '.txt')):
                raise HTTPException(
                    status_code=400,
                    detail=f"Unsupported file type: {uploaded_file.filename}. Only PDF and TXT files are allowed."
                )
            
            file_path = os.path.join(temp_dir, uploaded_file.filename)
            print(f"Saving file: {uploaded_file.filename} to {file_path}")
            with open(file_path, "wb") as f:
                content = await uploaded_file.read()
                f.write(content)
            file_paths.append(file_path)
            print(f"File saved successfully: {uploaded_file.filename} ({len(content)} bytes)")
        
        # Step 1: Document Ingestion
        print(f"Loading {len(file_paths)} documents...")
        documents = load_documents(file_paths)
        
        if not documents:
            raise HTTPException(status_code=400, detail="No text could be extracted from the uploaded documents")
        
        print(f"Chunking documents...")
        chunks = chunk_documents(documents)
        
        print(f"Creating vector store...")
        # Use free TF-IDF embeddings to avoid API costs
        print("Using free TF-IDF embeddings")
        embeddings = FreeEmbeddings(max_features=1000)
        
        # Pre-fit the embeddings on all document chunks for better performance
        all_texts = [chunk.page_content for chunk in chunks]
        embeddings.add_texts_to_corpus(all_texts)
        
        vector_store = create_vector_store(chunks, embeddings)
        
        # Step 2: Initialize LLM and Agents
        print("Initializing AI agents...")
        # Use Mistral AI for LLM
        if mistral_key and MISTRAL_AVAILABLE:
            print("Using Mistral AI")
            llm = ChatMistralAI(
                model="mistral-large-latest",
                mistral_api_key=mistral_key,
                temperature=0
            )
        else:
            raise HTTPException(status_code=500, detail="Mistral AI not available")
        
        # Step 3: Run Agent Analyses
        print("Analyzing financial risks...")
        financial_agent = FinancialRiskAgent(llm, vector_store)
        financial_findings = financial_agent.analyze()
        
        print("Analyzing legal risks...")
        legal_agent = LegalRiskAgent(llm, vector_store)
        legal_findings = legal_agent.analyze()
        
        print("Analyzing operational risks...")
        operational_agent = OperationalRiskAgent(llm, vector_store)
        operational_findings = operational_agent.analyze()
        
        # Step 4: Cross-Document Checks
        print("Running cross-document checks...")
        all_findings = financial_findings + legal_findings + operational_findings
        inconsistencies = run_all_checks(all_findings, vector_store)
        
        # Step 5: Calculate Risk Score
        print("Calculating risk score...")
        score, classification = calculate_risk_score(all_findings, inconsistencies)
        
        # Step 6: Generate Report
        print("Generating risk memo...")
        memo = generate_risk_memo(
            financial_findings,
            legal_findings,
            operational_findings,
            inconsistencies,
            score,
            classification
        )
        
        # Convert findings to dictionaries for JSON serialization
        def finding_to_dict(finding):
            return {
                "risk_description": finding.risk_description,
                "severity": finding.severity,
                "evidence": finding.evidence,
                "source_document": finding.source_document,
                "source_location": finding.source_location,
                "agent_type": finding.agent_type
            }
        
        def inconsistency_to_dict(inconsistency):
            return {
                "issue_description": inconsistency.issue_description,
                "documents_involved": inconsistency.documents_involved,
                "severity": inconsistency.severity,
                "details": inconsistency.details
            }
        
        # Prepare response
        results = {
            "documents_loaded": len(documents),
            "chunks_created": len(chunks),
            "financial_findings": [finding_to_dict(f) for f in financial_findings],
            "legal_findings": [finding_to_dict(f) for f in legal_findings],
            "operational_findings": [finding_to_dict(f) for f in operational_findings],
            "inconsistencies": [inconsistency_to_dict(i) for i in inconsistencies],
            "risk_score": score,
            "risk_classification": classification,
            "memo": memo
        }
        
        print(f"Analysis complete! Risk: {classification} (Score: {score})")
        
        return JSONResponse(content=results)
    
    except HTTPException as he:
        print(f"HTTP Exception: {he.detail}")
        raise
    except Exception as e:
        import traceback
        error_trace = traceback.format_exc()
        print(f"Error during analysis: {str(e)}")
        print(f"Full traceback:\n{error_trace}")
        raise HTTPException(status_code=500, detail=f"Analysis failed: {str(e)}")
    
    finally:
        # Cleanup temporary files
        try:
            shutil.rmtree(temp_dir)
        except Exception as e:
            print(f"Warning: Failed to cleanup temporary directory: {e}")


@app.post("/api/analyze-sample")
async def analyze_sample_documents():
    """
    Analyze the included sample documents.
    
    This endpoint runs analysis on the pre-included sample documents
    for demonstration purposes.
    """
    
    # Check if API key is configured - only need Mistral for free deployment
    mistral_key = os.getenv("MISTRAL_API_KEY")
    
    if not mistral_key:
        raise HTTPException(
            status_code=500,
            detail="Mistral API key required. Please set MISTRAL_API_KEY environment variable. Get a free key at https://console.mistral.ai/"
        )
    
    # Sample document paths
    sample_paths = [
        "data/sample_docs/financial_summary.txt",
        "data/sample_docs/customer_contract.txt",
        "data/sample_docs/internal_policy.txt"
    ]
    
    # Verify sample files exist
    for path in sample_paths:
        if not os.path.exists(path):
            raise HTTPException(
                status_code=404,
                detail=f"Sample document not found: {path}"
            )
    
    try:
        # Run analysis on sample documents
        # (Same logic as analyze_documents but with predefined paths)
        print("Loading sample documents...")
        documents = load_documents(sample_paths)
        
        print("Chunking documents...")
        chunks = chunk_documents(documents)
        
        print("Creating vector store...")
        # Use free TF-IDF embeddings to avoid API costs
        print("Using free TF-IDF embeddings")
        embeddings = FreeEmbeddings(max_features=1000)
        
        # Pre-fit the embeddings on all document chunks for better performance
        all_texts = [chunk.page_content for chunk in chunks]
        embeddings.add_texts_to_corpus(all_texts)
        
        vector_store = create_vector_store(chunks, embeddings)
        
        print("Initializing AI agents...")
        # Use Mistral AI for LLM
        if mistral_key and MISTRAL_AVAILABLE:
            print("Using Mistral AI")
            llm = ChatMistralAI(
                model="mistral-large-latest",
                mistral_api_key=mistral_key,
                temperature=0
            )
        else:
            raise HTTPException(status_code=500, detail="Mistral AI not available")
        
        print("Analyzing financial risks...")
        financial_agent = FinancialRiskAgent(llm, vector_store)
        financial_findings = financial_agent.analyze()
        
        print("Analyzing legal risks...")
        legal_agent = LegalRiskAgent(llm, vector_store)
        legal_findings = legal_agent.analyze()
        
        print("Analyzing operational risks...")
        operational_agent = OperationalRiskAgent(llm, vector_store)
        operational_findings = operational_agent.analyze()
        
        print("Running cross-document checks...")
        all_findings = financial_findings + legal_findings + operational_findings
        inconsistencies = run_all_checks(all_findings, vector_store)
        
        print("Calculating risk score...")
        score, classification = calculate_risk_score(all_findings, inconsistencies)
        
        print("Generating risk memo...")
        memo = generate_risk_memo(
            financial_findings,
            legal_findings,
            operational_findings,
            inconsistencies,
            score,
            classification
        )
        
        # Convert to dictionaries
        def finding_to_dict(finding):
            return {
                "risk_description": finding.risk_description,
                "severity": finding.severity,
                "evidence": finding.evidence,
                "source_document": finding.source_document,
                "source_location": finding.source_location,
                "agent_type": finding.agent_type
            }
        
        def inconsistency_to_dict(inconsistency):
            return {
                "issue_description": inconsistency.issue_description,
                "documents_involved": inconsistency.documents_involved,
                "severity": inconsistency.severity,
                "details": inconsistency.details
            }
        
        results = {
            "documents_loaded": len(documents),
            "chunks_created": len(chunks),
            "financial_findings": [finding_to_dict(f) for f in financial_findings],
            "legal_findings": [finding_to_dict(f) for f in legal_findings],
            "operational_findings": [finding_to_dict(f) for f in operational_findings],
            "inconsistencies": [inconsistency_to_dict(i) for i in inconsistencies],
            "risk_score": score,
            "risk_classification": classification,
            "memo": memo
        }
        
        print(f"Analysis complete! Risk: {classification} (Score: {score})")
        
        return JSONResponse(content=results)
    
    except Exception as e:
        print(f"Error during analysis: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Analysis failed: {str(e)}")


if __name__ == "__main__":
    import uvicorn
    
    # Get port from environment variable (Railway sets this)
    port = int(os.getenv("PORT", 8000))
    
    print("=" * 70)
    print("AI Due Diligence Engine - API Server")
    print("=" * 70)
    print()
    print("Starting FastAPI server...")
    print(f"API will be available at: http://0.0.0.0:{port}")
    print(f"API documentation: http://0.0.0.0:{port}/docs")
    print()
    print("Press CTRL+C to stop the server")
    print("=" * 70)
    
    uvicorn.run(app, host="0.0.0.0", port=port, log_level="info")
