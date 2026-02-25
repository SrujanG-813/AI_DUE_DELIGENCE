"""
Streamlit Web UI for AI Due Diligence Engine

This module provides a user-friendly web interface for the AI Due Diligence Engine,
allowing users to upload documents, run analysis, and view results in an interactive format.
"""

import streamlit as st
import os
import tempfile
from pathlib import Path
import sys
from datetime import datetime

# Add the project root to the path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from ai_due_diligence.ingest import load_documents, chunk_documents, create_vector_store
from ai_due_diligence.agents import FinancialRiskAgent, LegalRiskAgent, OperationalRiskAgent
from ai_due_diligence.cross_checks import run_all_checks
from ai_due_diligence.report import calculate_risk_score, generate_risk_memo
from langchain_openai import ChatOpenAI, OpenAIEmbeddings

# Page configuration
st.set_page_config(
    page_title="AI Due Diligence Engine",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for better styling
st.markdown("""
    <style>
    .main-header {
        font-size: 3rem;
        font-weight: bold;
        color: #1f77b4;
        text-align: center;
        margin-bottom: 1rem;
    }
    .sub-header {
        font-size: 1.2rem;
        color: #666;
        text-align: center;
        margin-bottom: 2rem;
    }
    .risk-high {
        background-color: #ffebee;
        padding: 1rem;
        border-left: 5px solid #f44336;
        border-radius: 5px;
        margin: 1rem 0;
    }
    .risk-medium {
        background-color: #fff3e0;
        padding: 1rem;
        border-left: 5px solid #ff9800;
        border-radius: 5px;
        margin: 1rem 0;
    }
    .risk-low {
        background-color: #e8f5e9;
        padding: 1rem;
        border-left: 5px solid #4caf50;
        border-radius: 5px;
        margin: 1rem 0;
    }
    .metric-card {
        background-color: #f5f5f5;
        padding: 1.5rem;
        border-radius: 10px;
        text-align: center;
    }
    .stProgress > div > div > div > div {
        background-color: #1f77b4;
    }
    </style>
""", unsafe_allow_html=True)


def check_api_key():
    """Check if OpenAI API key is configured."""
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        st.error("⚠️ OpenAI API Key not found!")
        st.info("""
        Please set your OpenAI API key:
        
        **Option 1: Environment Variable**
        ```bash
        export OPENAI_API_KEY='your-api-key-here'  # Linux/Mac
        set OPENAI_API_KEY=your-api-key-here       # Windows CMD
        $env:OPENAI_API_KEY='your-api-key-here'    # Windows PowerShell
        ```
        
        **Option 2: .env file**
        1. Copy `.env.example` to `.env`
        2. Add your API key: `OPENAI_API_KEY=your-api-key-here`
        
        Get your API key at: https://platform.openai.com/api-keys
        """)
        return False
    return True


def save_uploaded_files(uploaded_files):
    """Save uploaded files to temporary directory and return paths."""
    temp_dir = tempfile.mkdtemp()
    file_paths = []
    
    for uploaded_file in uploaded_files:
        file_path = os.path.join(temp_dir, uploaded_file.name)
        with open(file_path, "wb") as f:
            f.write(uploaded_file.getbuffer())
        file_paths.append(file_path)
    
    return file_paths, temp_dir


def run_analysis(file_paths, progress_callback=None):
    """Run the complete due diligence analysis pipeline."""
    results = {}
    
    try:
        # Step 1: Document Ingestion
        if progress_callback:
            progress_callback(0.1, "Loading documents...")
        documents = load_documents(file_paths)
        results['documents_loaded'] = len(documents)
        
        if progress_callback:
            progress_callback(0.2, "Chunking documents...")
        chunks = chunk_documents(documents)
        results['chunks_created'] = len(chunks)
        
        if progress_callback:
            progress_callback(0.3, "Creating vector store...")
        embeddings = OpenAIEmbeddings()
        vector_store = create_vector_store(chunks, embeddings)
        
        # Step 2: Initialize LLM and Agents
        if progress_callback:
            progress_callback(0.4, "Initializing AI agents...")
        llm = ChatOpenAI(model="gpt-4", temperature=0)
        
        # Step 3: Run Agent Analyses
        if progress_callback:
            progress_callback(0.5, "Analyzing financial risks...")
        financial_agent = FinancialRiskAgent(llm, vector_store)
        financial_findings = financial_agent.analyze()
        results['financial_findings'] = financial_findings
        
        if progress_callback:
            progress_callback(0.6, "Analyzing legal risks...")
        legal_agent = LegalRiskAgent(llm, vector_store)
        legal_findings = legal_agent.analyze()
        results['legal_findings'] = legal_findings
        
        if progress_callback:
            progress_callback(0.7, "Analyzing operational risks...")
        operational_agent = OperationalRiskAgent(llm, vector_store)
        operational_findings = operational_agent.analyze()
        results['operational_findings'] = operational_findings
        
        # Step 4: Cross-Document Checks
        if progress_callback:
            progress_callback(0.8, "Running cross-document checks...")
        all_findings = financial_findings + legal_findings + operational_findings
        inconsistencies = run_all_checks(all_findings, vector_store)
        results['inconsistencies'] = inconsistencies
        
        # Step 5: Calculate Risk Score
        if progress_callback:
            progress_callback(0.9, "Calculating risk score...")
        score, classification = calculate_risk_score(all_findings, inconsistencies)
        results['risk_score'] = score
        results['risk_classification'] = classification
        
        # Step 6: Generate Report
        if progress_callback:
            progress_callback(0.95, "Generating risk memo...")
        memo = generate_risk_memo(
            financial_findings,
            legal_findings,
            operational_findings,
            inconsistencies,
            score,
            classification
        )
        results['memo'] = memo
        
        if progress_callback:
            progress_callback(1.0, "Analysis complete!")
        
        return results
    
    except Exception as e:
        st.error(f"Error during analysis: {str(e)}")
        raise


def display_risk_badge(classification):
    """Display a colored risk classification badge."""
    if classification == "High Risk":
        st.markdown(f'<div class="risk-high"><h2>🔴 {classification}</h2></div>', unsafe_allow_html=True)
    elif classification == "Medium Risk":
        st.markdown(f'<div class="risk-medium"><h2>🟡 {classification}</h2></div>', unsafe_allow_html=True)
    else:
        st.markdown(f'<div class="risk-low"><h2>🟢 {classification}</h2></div>', unsafe_allow_html=True)


def display_findings_summary(findings, category_name):
    """Display a summary of findings for a category."""
    if not findings:
        st.info(f"No {category_name.lower()} risks identified.")
        return
    
    high_count = sum(1 for f in findings if f.severity == "High")
    medium_count = sum(1 for f in findings if f.severity == "Medium")
    low_count = sum(1 for f in findings if f.severity == "Low")
    
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("🔴 High", high_count)
    with col2:
        st.metric("🟡 Medium", medium_count)
    with col3:
        st.metric("🟢 Low", low_count)
    
    with st.expander(f"View {category_name} Findings Details"):
        for i, finding in enumerate(findings, 1):
            severity_emoji = "🔴" if finding.severity == "High" else "🟡" if finding.severity == "Medium" else "🟢"
            st.markdown(f"**{severity_emoji} Finding {i}: {finding.risk_description}**")
            st.markdown(f"*Evidence:* {finding.evidence[:200]}...")
            st.markdown(f"*Source:* {finding.source_document} - {finding.source_location}")
            st.markdown("---")


def main():
    """Main Streamlit application."""
    
    # Header
    st.markdown('<div class="main-header">📊 AI Due Diligence Engine</div>', unsafe_allow_html=True)
    st.markdown('<div class="sub-header">Automated Investment Risk Analysis with AI</div>', unsafe_allow_html=True)
    
    # Check API key
    if not check_api_key():
        st.stop()
    
    # Sidebar
    with st.sidebar:
        st.header("📁 Document Upload")
        st.markdown("Upload business documents for analysis:")
        
        uploaded_files = st.file_uploader(
            "Choose files",
            type=['txt', 'pdf'],
            accept_multiple_files=True,
            help="Upload PDF or text files containing financial statements, contracts, policies, etc."
        )
        
        st.markdown("---")
        st.header("ℹ️ About")
        st.markdown("""
        This tool analyzes business documents to identify:
        - 💰 Financial risks
        - ⚖️ Legal risks
        - 🔧 Operational risks
        - 🔍 Cross-document inconsistencies
        
        **Powered by:**
        - OpenAI GPT-4
        - LangChain
        - FAISS Vector Store
        """)
        
        st.markdown("---")
        
        # Sample documents option
        use_sample = st.checkbox("Use sample documents", help="Run analysis on included sample documents")
        
        analyze_button = st.button("🚀 Run Analysis", type="primary", use_container_width=True)
    
    # Main content area
    if analyze_button:
        if not uploaded_files and not use_sample:
            st.warning("⚠️ Please upload documents or select 'Use sample documents'")
            st.stop()
        
        # Determine which files to analyze
        if use_sample:
            file_paths = [
                "data/sample_docs/financial_summary.txt",
                "data/sample_docs/customer_contract.txt",
                "data/sample_docs/internal_policy.txt"
            ]
            temp_dir = None
            st.info("📄 Using sample documents for analysis")
        else:
            file_paths, temp_dir = save_uploaded_files(uploaded_files)
            st.success(f"✅ Uploaded {len(file_paths)} document(s)")
        
        # Progress tracking
        progress_bar = st.progress(0)
        status_text = st.empty()
        
        def update_progress(value, message):
            progress_bar.progress(value)
            status_text.text(message)
        
        # Run analysis
        with st.spinner("Running analysis..."):
            try:
                results = run_analysis(file_paths, progress_callback=update_progress)
                
                # Clear progress indicators
                progress_bar.empty()
                status_text.empty()
                
                # Display results
                st.success("✅ Analysis complete!")
                
                # Risk Score Overview
                st.header("📈 Risk Assessment Overview")
                
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.markdown('<div class="metric-card">', unsafe_allow_html=True)
                    st.metric("Risk Score", results['risk_score'])
                    st.markdown('</div>', unsafe_allow_html=True)
                
                with col2:
                    st.markdown('<div class="metric-card">', unsafe_allow_html=True)
                    st.metric("Documents Analyzed", results['documents_loaded'])
                    st.markdown('</div>', unsafe_allow_html=True)
                
                with col3:
                    st.markdown('<div class="metric-card">', unsafe_allow_html=True)
                    st.metric("Total Findings", 
                             len(results['financial_findings']) + 
                             len(results['legal_findings']) + 
                             len(results['operational_findings']))
                    st.markdown('</div>', unsafe_allow_html=True)
                
                st.markdown("---")
                display_risk_badge(results['risk_classification'])
                
                # Findings by Category
                st.header("🔍 Risk Findings by Category")
                
                tab1, tab2, tab3, tab4 = st.tabs(["💰 Financial", "⚖️ Legal", "🔧 Operational", "🔗 Inconsistencies"])
                
                with tab1:
                    display_findings_summary(results['financial_findings'], "Financial")
                
                with tab2:
                    display_findings_summary(results['legal_findings'], "Legal")
                
                with tab3:
                    display_findings_summary(results['operational_findings'], "Operational")
                
                with tab4:
                    if results['inconsistencies']:
                        for i, inconsistency in enumerate(results['inconsistencies'], 1):
                            severity_emoji = "🔴" if inconsistency.severity == "High" else "🟡" if inconsistency.severity == "Medium" else "🟢"
                            st.markdown(f"**{severity_emoji} Inconsistency {i}: {inconsistency.issue_description}**")
                            st.markdown(f"*Documents:* {', '.join(inconsistency.documents_involved)}")
                            st.markdown(f"*Details:* {inconsistency.details}")
                            st.markdown("---")
                    else:
                        st.info("No cross-document inconsistencies detected.")
                
                # Full Report
                st.header("📄 Complete Risk Memo")
                st.markdown(results['memo'])
                
                # Download button
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                st.download_button(
                    label="📥 Download Risk Memo",
                    data=results['memo'],
                    file_name=f"risk_memo_{timestamp}.md",
                    mime="text/markdown",
                    use_container_width=True
                )
                
                # Cleanup temp files
                if temp_dir:
                    import shutil
                    shutil.rmtree(temp_dir, ignore_errors=True)
                
            except Exception as e:
                st.error(f"❌ Analysis failed: {str(e)}")
                st.exception(e)
    
    else:
        # Welcome screen
        st.markdown("---")
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("🎯 How It Works")
            st.markdown("""
            1. **Upload Documents** - Add your business documents (PDFs or text files)
            2. **AI Analysis** - Our AI agents analyze financial, legal, and operational risks
            3. **Get Results** - Receive a comprehensive risk memo with evidence-backed findings
            4. **Download Report** - Export the full analysis as a markdown document
            """)
        
        with col2:
            st.subheader("📋 Document Types")
            st.markdown("""
            - Financial statements and projections
            - Customer contracts and agreements
            - Internal policies and procedures
            - Product documentation
            - Any business-related documents
            """)
        
        st.markdown("---")
        st.info("👈 Upload documents in the sidebar to get started, or try the sample documents!")


if __name__ == "__main__":
    main()
