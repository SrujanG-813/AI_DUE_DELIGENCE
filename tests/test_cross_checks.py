"""
Unit tests for cross-document inconsistency detection module.
"""

import pytest
from dataclasses import dataclass
from ai_due_diligence.cross_checks import (
    check_revenue_consistency,
    _extract_revenue_amounts,
    _format_amount,
    Inconsistency
)


# Mock RiskFinding class for testing
@dataclass
class MockRiskFinding:
    """Mock RiskFinding for testing purposes."""
    risk_description: str
    severity: str
    evidence: str
    source_document: str
    source_location: str
    agent_type: str


class TestExtractRevenueAmounts:
    """Test suite for _extract_revenue_amounts helper function."""
    
    def test_extract_millions_with_decimal(self):
        """Test extracting amounts like $2.5M."""
        text = "The company reported $2.5M in revenue."
        amounts = _extract_revenue_amounts(text)
        assert len(amounts) == 1
        assert amounts[0] == 2_500_000.0
    
    def test_extract_millions_without_decimal(self):
        """Test extracting amounts like $2M."""
        text = "Annual revenue is $2M."
        amounts = _extract_revenue_amounts(text)
        assert len(amounts) == 1
        assert amounts[0] == 2_000_000.0
    
    def test_extract_thousands(self):
        """Test extracting amounts like $500K."""
        text = "Monthly revenue: $500K"
        amounts = _extract_revenue_amounts(text)
        assert len(amounts) == 1
        assert amounts[0] == 500_000.0
    
    def test_extract_billions(self):
        """Test extracting amounts like $1.2B."""
        text = "Total valuation is $1.2B"
        amounts = _extract_revenue_amounts(text)
        assert len(amounts) == 1
        assert amounts[0] == 1_200_000_000.0
    
    def test_extract_raw_dollar_amount(self):
        """Test extracting raw dollar amounts like $2,500,000."""
        text = "Revenue was $2,500,000 last year."
        amounts = _extract_revenue_amounts(text)
        assert len(amounts) == 1
        assert amounts[0] == 2_500_000.0
    
    def test_extract_multiple_amounts(self):
        """Test extracting multiple amounts from text."""
        text = "Q1 revenue was $1.5M and Q2 was $2M."
        amounts = _extract_revenue_amounts(text)
        assert len(amounts) == 2
        assert 1_500_000.0 in amounts
        assert 2_000_000.0 in amounts
    
    def test_extract_no_amounts(self):
        """Test text with no revenue amounts."""
        text = "This is a document with no financial figures."
        amounts = _extract_revenue_amounts(text)
        assert len(amounts) == 0
    
    def test_extract_case_insensitive(self):
        """Test that extraction is case insensitive."""
        text = "Revenue is $3m annually."
        amounts = _extract_revenue_amounts(text)
        assert len(amounts) == 1
        assert amounts[0] == 3_000_000.0


class TestFormatAmount:
    """Test suite for _format_amount helper function."""
    
    def test_format_millions(self):
        """Test formatting amounts in millions."""
        assert _format_amount(2_500_000) == "$2.50M"
        assert _format_amount(1_000_000) == "$1.00M"
    
    def test_format_thousands(self):
        """Test formatting amounts in thousands."""
        assert _format_amount(500_000) == "$500.00K"
        assert _format_amount(1_500) == "$1.50K"
    
    def test_format_billions(self):
        """Test formatting amounts in billions."""
        assert _format_amount(1_200_000_000) == "$1.20B"
        assert _format_amount(5_000_000_000) == "$5.00B"
    
    def test_format_small_amounts(self):
        """Test formatting small amounts."""
        assert _format_amount(500) == "$500.00"
        assert _format_amount(99.99) == "$99.99"


class TestCheckRevenueConsistency:
    """Test suite for check_revenue_consistency function."""
    
    def test_no_revenue_findings(self):
        """Test with no revenue-related findings."""
        from unittest.mock import Mock
        
        # Create findings without revenue mentions
        findings = [
            MockRiskFinding(
                risk_description="Legal risk identified",
                severity="Medium",
                evidence="Contract has unusual terms",
                source_document="contract.pdf",
                source_location="Page 3",
                agent_type="Legal"
            )
        ]
        
        # Mock vector store
        mock_vector_store = Mock()
        mock_vector_store.similarity_search_with_score.return_value = []
        
        # Should return empty list
        inconsistencies = check_revenue_consistency(findings, mock_vector_store)
        assert len(inconsistencies) == 0
    
    def test_single_revenue_figure(self):
        """Test with only one revenue figure (no inconsistency possible)."""
        from unittest.mock import Mock
        
        findings = [
            MockRiskFinding(
                risk_description="Revenue projection lacks support",
                severity="High",
                evidence="The company reports $2M in annual revenue.",
                source_document="financial.pdf",
                source_location="Page 1",
                agent_type="Financial"
            )
        ]
        
        mock_vector_store = Mock()
        mock_vector_store.similarity_search_with_score.return_value = []
        
        # Should return empty list (need at least 2 figures)
        inconsistencies = check_revenue_consistency(findings, mock_vector_store)
        assert len(inconsistencies) == 0
    
    def test_detect_revenue_mismatch(self):
        """Test detection of revenue mismatch across documents."""
        from unittest.mock import Mock
        from langchain_core.documents import Document
        
        # Create findings with different revenue figures
        findings = [
            MockRiskFinding(
                risk_description="Revenue claim",
                severity="Medium",
                evidence="Annual revenue is $2M.",
                source_document="financial.pdf",
                source_location="Page 1",
                agent_type="Financial"
            ),
            MockRiskFinding(
                risk_description="Contract revenue",
                severity="Medium",
                evidence="Contract value is $1.5M annually.",
                source_document="contract.pdf",
                source_location="Page 5",
                agent_type="Financial"
            )
        ]
        
        mock_vector_store = Mock()
        mock_vector_store.similarity_search_with_score.return_value = []
        
        # Check for inconsistencies
        inconsistencies = check_revenue_consistency(findings, mock_vector_store)
        
        # Should detect the 25% discrepancy
        assert len(inconsistencies) > 0
        assert any("Revenue mismatch" in inc.issue_description for inc in inconsistencies)
        
        # Verify inconsistency details
        inc = inconsistencies[0]
        assert "financial.pdf" in inc.documents_involved
        assert "contract.pdf" in inc.documents_involved
        assert inc.severity in ["Low", "Medium", "High"]
    
    def test_small_discrepancy_not_flagged(self):
        """Test that small discrepancies (<10%) are not flagged."""
        from unittest.mock import Mock
        
        # Create findings with 5% difference (should not be flagged)
        findings = [
            MockRiskFinding(
                risk_description="Revenue claim",
                severity="Medium",
                evidence="Annual revenue is $2M.",
                source_document="doc1.pdf",
                source_location="Page 1",
                agent_type="Financial"
            ),
            MockRiskFinding(
                risk_description="Revenue claim",
                severity="Medium",
                evidence="Revenue reported as $1.9M.",
                source_document="doc2.pdf",
                source_location="Page 1",
                agent_type="Financial"
            )
        ]
        
        mock_vector_store = Mock()
        mock_vector_store.similarity_search_with_score.return_value = []
        
        # Should not flag 5% discrepancy
        inconsistencies = check_revenue_consistency(findings, mock_vector_store)
        assert len(inconsistencies) == 0
    
    def test_severity_levels(self):
        """Test that severity is assigned correctly based on discrepancy magnitude."""
        from unittest.mock import Mock
        
        # Test High severity (>30% discrepancy)
        findings_high = [
            MockRiskFinding(
                risk_description="Revenue",
                severity="Medium",
                evidence="Revenue is $2M.",
                source_document="doc1.pdf",
                source_location="Page 1",
                agent_type="Financial"
            ),
            MockRiskFinding(
                risk_description="Revenue",
                severity="Medium",
                evidence="Revenue is $1M.",
                source_document="doc2.pdf",
                source_location="Page 1",
                agent_type="Financial"
            )
        ]
        
        mock_vector_store = Mock()
        mock_vector_store.similarity_search_with_score.return_value = []
        
        inconsistencies = check_revenue_consistency(findings_high, mock_vector_store)
        assert len(inconsistencies) > 0
        assert inconsistencies[0].severity == "High"  # 50% discrepancy



class TestRunAllChecks:
    """Test suite for run_all_checks orchestration function."""
    
    def test_run_all_checks_with_no_findings(self):
        """Test run_all_checks with empty findings list."""
        from unittest.mock import Mock
        from ai_due_diligence.cross_checks import run_all_checks
        
        findings = []
        mock_vector_store = Mock()
        mock_vector_store.similarity_search_with_score.return_value = []
        
        # Should return empty list
        inconsistencies = run_all_checks(findings, mock_vector_store)
        assert isinstance(inconsistencies, list)
        assert len(inconsistencies) == 0
    
    def test_run_all_checks_aggregates_results(self):
        """Test that run_all_checks aggregates results from all check functions."""
        from unittest.mock import Mock, patch
        from ai_due_diligence.cross_checks import run_all_checks, Inconsistency
        
        # Create mock findings
        findings = [
            MockRiskFinding(
                risk_description="Revenue claim",
                severity="Medium",
                evidence="Revenue is $2M.",
                source_document="doc1.pdf",
                source_location="Page 1",
                agent_type="Financial"
            )
        ]
        
        mock_vector_store = Mock()
        
        # Mock the individual check functions to return known inconsistencies
        mock_revenue_inc = Inconsistency(
            issue_description="Revenue mismatch",
            documents_involved=["doc1.pdf", "doc2.pdf"],
            severity="High",
            details="Test revenue inconsistency"
        )
        
        mock_ip_inc = Inconsistency(
            issue_description="IP conflict",
            documents_involved=["doc1.pdf", "doc3.pdf"],
            severity="Medium",
            details="Test IP inconsistency"
        )
        
        mock_scalability_inc = Inconsistency(
            issue_description="Scalability contradiction",
            documents_involved=["doc2.pdf", "doc3.pdf"],
            severity="Low",
            details="Test scalability inconsistency"
        )
        
        with patch('ai_due_diligence.cross_checks.check_revenue_consistency', return_value=[mock_revenue_inc]), \
             patch('ai_due_diligence.cross_checks.check_ip_ownership_conflicts', return_value=[mock_ip_inc]), \
             patch('ai_due_diligence.cross_checks.check_scalability_vendor_conflicts', return_value=[mock_scalability_inc]):
            
            # Run all checks
            inconsistencies = run_all_checks(findings, mock_vector_store)
            
            # Should aggregate all three inconsistencies
            assert len(inconsistencies) == 3
            assert mock_revenue_inc in inconsistencies
            assert mock_ip_inc in inconsistencies
            assert mock_scalability_inc in inconsistencies
    
    def test_run_all_checks_handles_errors_gracefully(self):
        """Test that run_all_checks continues even if one check fails."""
        from unittest.mock import Mock, patch
        from ai_due_diligence.cross_checks import run_all_checks, Inconsistency
        
        findings = []
        mock_vector_store = Mock()
        
        # Mock one check to raise an exception
        mock_ip_inc = Inconsistency(
            issue_description="IP conflict",
            documents_involved=["doc1.pdf", "doc2.pdf"],
            severity="Medium",
            details="Test IP inconsistency"
        )
        
        with patch('ai_due_diligence.cross_checks.check_revenue_consistency', side_effect=Exception("Test error")), \
             patch('ai_due_diligence.cross_checks.check_ip_ownership_conflicts', return_value=[mock_ip_inc]), \
             patch('ai_due_diligence.cross_checks.check_scalability_vendor_conflicts', return_value=[]):
            
            # Should not raise exception, should return partial results
            inconsistencies = run_all_checks(findings, mock_vector_store)
            
            # Should still get results from successful checks
            assert len(inconsistencies) == 1
            assert mock_ip_inc in inconsistencies
    
    def test_run_all_checks_returns_empty_list_on_all_failures(self):
        """Test that run_all_checks returns empty list if all checks fail."""
        from unittest.mock import Mock, patch
        from ai_due_diligence.cross_checks import run_all_checks
        
        findings = []
        mock_vector_store = Mock()
        
        # Mock all checks to raise exceptions
        with patch('ai_due_diligence.cross_checks.check_revenue_consistency', side_effect=Exception("Error 1")), \
             patch('ai_due_diligence.cross_checks.check_ip_ownership_conflicts', side_effect=Exception("Error 2")), \
             patch('ai_due_diligence.cross_checks.check_scalability_vendor_conflicts', side_effect=Exception("Error 3")):
            
            # Should not raise exception, should return empty list
            inconsistencies = run_all_checks(findings, mock_vector_store)
            assert isinstance(inconsistencies, list)
            assert len(inconsistencies) == 0
