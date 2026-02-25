"""
Tests for Risk Analysis Agents

This module tests the risk analysis agents to ensure they correctly
analyze documents and produce structured risk findings.
"""

import pytest
from unittest.mock import Mock, MagicMock
from ai_due_diligence.agents import FinancialRiskAgent, RiskFinding
from langchain_core.documents import Document


class TestFinancialRiskAgent:
    """Tests for the FinancialRiskAgent class."""
    
    def test_financial_agent_initialization(self):
        """Test that FinancialRiskAgent initializes correctly."""
        # Create mock LLM and vector store
        mock_llm = Mock()
        mock_vector_store = Mock()
        
        # Initialize agent
        agent = FinancialRiskAgent(llm=mock_llm, vector_store=mock_vector_store)
        
        # Verify initialization
        assert agent.agent_type == "Financial"
        assert agent.llm == mock_llm
        assert agent.vector_store == mock_vector_store
    
    def test_financial_agent_analyze_with_valid_response(self):
        """Test that FinancialRiskAgent correctly parses valid LLM responses."""
        # Create mock LLM that returns valid JSON
        mock_llm = Mock()
        mock_response = Mock()
        mock_response.content = """[
            {
                "risk_description": "Revenue projections lack supporting data",
                "severity": "High",
                "evidence": "Q4 revenue target of $5M mentioned without methodology",
                "source_document": "financial_summary.pdf",
                "source_location": "Page 3"
            }
        ]"""
        mock_llm.invoke.return_value = mock_response
        
        # Create mock vector store that returns sample chunks
        mock_vector_store = Mock()
        sample_doc = Document(
            page_content="The company projects $5M in Q4 revenue.",
            metadata={"source": "financial_summary.pdf", "page": 3, "chunk_id": "chunk_1"}
        )
        mock_vector_store.similarity_search_with_score.return_value = [
            (sample_doc, 0.15)
        ]
        
        # Initialize agent and run analysis
        agent = FinancialRiskAgent(llm=mock_llm, vector_store=mock_vector_store)
        findings = agent.analyze()
        
        # Verify results
        assert len(findings) == 1
        assert isinstance(findings[0], RiskFinding)
        assert findings[0].risk_description == "Revenue projections lack supporting data"
        assert findings[0].severity == "High"
        assert findings[0].agent_type == "Financial"
        assert findings[0].source_document == "financial_summary.pdf"
    
    def test_financial_agent_analyze_with_empty_response(self):
        """Test that FinancialRiskAgent handles empty LLM responses."""
        # Create mock LLM that returns empty array
        mock_llm = Mock()
        mock_response = Mock()
        mock_response.content = "[]"
        mock_llm.invoke.return_value = mock_response
        
        # Create mock vector store
        mock_vector_store = Mock()
        sample_doc = Document(
            page_content="Sample content",
            metadata={"source": "test.pdf", "page": 1, "chunk_id": "chunk_1"}
        )
        mock_vector_store.similarity_search_with_score.return_value = [
            (sample_doc, 0.15)
        ]
        
        # Initialize agent and run analysis
        agent = FinancialRiskAgent(llm=mock_llm, vector_store=mock_vector_store)
        findings = agent.analyze()
        
        # Verify empty results
        assert len(findings) == 0
    
    def test_financial_agent_analyze_with_no_chunks(self):
        """Test that FinancialRiskAgent handles case when no chunks are retrieved."""
        # Create mock LLM
        mock_llm = Mock()
        
        # Create mock vector store that returns no chunks
        mock_vector_store = Mock()
        mock_vector_store.similarity_search_with_score.return_value = []
        
        # Initialize agent and run analysis
        agent = FinancialRiskAgent(llm=mock_llm, vector_store=mock_vector_store)
        findings = agent.analyze()
        
        # Verify empty results and that LLM was not called
        assert len(findings) == 0
        mock_llm.invoke.assert_not_called()
    
    def test_financial_agent_analyze_with_invalid_json(self):
        """Test that FinancialRiskAgent handles malformed JSON gracefully."""
        # Create mock LLM that returns invalid JSON
        mock_llm = Mock()
        mock_response = Mock()
        mock_response.content = "This is not valid JSON"
        mock_llm.invoke.return_value = mock_response
        
        # Create mock vector store
        mock_vector_store = Mock()
        sample_doc = Document(
            page_content="Sample content",
            metadata={"source": "test.pdf", "page": 1, "chunk_id": "chunk_1"}
        )
        mock_vector_store.similarity_search_with_score.return_value = [
            (sample_doc, 0.15)
        ]
        
        # Initialize agent and run analysis
        agent = FinancialRiskAgent(llm=mock_llm, vector_store=mock_vector_store)
        findings = agent.analyze()
        
        # Verify empty results (graceful error handling)
        assert len(findings) == 0
    
    def test_financial_agent_analyze_with_invalid_severity(self):
        """Test that FinancialRiskAgent defaults invalid severity to Medium."""
        # Create mock LLM that returns finding with invalid severity
        mock_llm = Mock()
        mock_response = Mock()
        mock_response.content = """[
            {
                "risk_description": "Test risk",
                "severity": "Critical",
                "evidence": "Test evidence",
                "source_document": "test.pdf",
                "source_location": "Page 1"
            }
        ]"""
        mock_llm.invoke.return_value = mock_response
        
        # Create mock vector store
        mock_vector_store = Mock()
        sample_doc = Document(
            page_content="Sample content",
            metadata={"source": "test.pdf", "page": 1, "chunk_id": "chunk_1"}
        )
        mock_vector_store.similarity_search_with_score.return_value = [
            (sample_doc, 0.15)
        ]
        
        # Initialize agent and run analysis
        agent = FinancialRiskAgent(llm=mock_llm, vector_store=mock_vector_store)
        findings = agent.analyze()
        
        # Verify severity was defaulted to Medium
        assert len(findings) == 1
        assert findings[0].severity == "Medium"
