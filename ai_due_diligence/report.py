"""
Report Generation Module

This module provides functions for calculating risk scores and generating
structured investment risk memos. It aggregates findings from all risk agents
and cross-document checks into a comprehensive markdown report.

The risk scoring system uses a weighted approach:
- High severity findings: 3 points each
- Medium severity findings: 2 points each
- Low severity findings: 1 point each

Overall risk classification:
- Low Risk: 0-5 points
- Medium Risk: 6-12 points
- High Risk: 13+ points
"""

from typing import List, Tuple
from ai_due_diligence.agents import RiskFinding
from ai_due_diligence.cross_checks import Inconsistency


def calculate_risk_score(
    findings: List[RiskFinding],
    inconsistencies: List[Inconsistency]
) -> Tuple[int, str]:
    """
    Calculate overall risk score and classification based on findings and inconsistencies.
    
    This function implements a weighted scoring system where each risk finding and
    inconsistency contributes points based on its severity level. The total score
    is then classified into Low, Medium, or High risk categories.
    
    Scoring Rules (Requirements 7.1, 7.2, 7.3):
    - High severity: +3 points
    - Medium severity: +2 points
    - Low severity: +1 point
    
    Classification Logic (Requirements 7.4, 7.5):
    - Score 0-5: Low Risk
      * Few or minor issues identified
      * Investment appears relatively safe
      * Standard due diligence concerns only
    
    - Score 6-12: Medium Risk
      * Several moderate concerns identified
      * Requires further investigation
      * Some red flags but potentially manageable
    
    - Score 13+: High Risk
      * Multiple critical issues identified
      * Significant concerns about investment viability
      * Major red flags requiring serious consideration
    
    The scoring system treats findings and inconsistencies equally, as both
    represent potential risks to the investment. Inconsistencies may indicate
    data quality issues, outdated information, or potential misrepresentation.
    
    Edge Cases:
    - Empty findings and inconsistencies: Returns (0, "Low")
    - Invalid severity values: Logged and defaulted to "Medium" (2 points)
    - Mixed severity levels: All contribute to total score
    
    Args:
        findings: List of RiskFinding objects from all risk agents
                 (Financial, Legal, Operational)
        inconsistencies: List of Inconsistency objects from cross-document checks
    
    Returns:
        Tuple of (total_score, risk_classification)
        - total_score: Integer sum of all severity points
        - risk_classification: String "Low", "Medium", or "High"
    
    Example:
        findings = [
            RiskFinding(..., severity="High", ...),    # +3
            RiskFinding(..., severity="Medium", ...),  # +2
            RiskFinding(..., severity="Low", ...)      # +1
        ]
        inconsistencies = [
            Inconsistency(..., severity="High", ...)   # +3
        ]
        
        score, classification = calculate_risk_score(findings, inconsistencies)
        # Returns: (9, "Medium")
    
    Requirements Validation:
    - Requirement 7.1: High-risk finding = +3 points
    - Requirement 7.2: Medium-risk finding = +2 points
    - Requirement 7.3: Low-risk finding = +1 point
    - Requirement 7.4: Classification based on total score
    - Requirement 7.5: Risk score included in final memo
    """
    import logging
    
    logger = logging.getLogger(__name__)
    
    # Initialize score counter
    total_score = 0
    
    # Severity to points mapping
    # This implements Requirements 7.1, 7.2, 7.3
    severity_points = {
        "High": 3,
        "Medium": 2,
        "Low": 1
    }
    
    # Count findings by severity for logging
    severity_counts = {"High": 0, "Medium": 0, "Low": 0, "Invalid": 0}
    
    # Calculate score from risk findings
    for finding in findings:
        severity = finding.severity
        
        # Validate severity and get points
        if severity in severity_points:
            points = severity_points[severity]
            total_score += points
            severity_counts[severity] += 1
            
            logger.debug(
                f"Finding ({finding.agent_type}): {severity} = +{points} points"
            )
        else:
            # Handle invalid severity (defensive programming)
            logger.warning(
                f"Invalid severity '{severity}' in finding from {finding.agent_type}. "
                f"Defaulting to Medium (2 points)."
            )
            total_score += 2  # Default to Medium
            severity_counts["Invalid"] += 1
    
    # Calculate score from inconsistencies
    # Inconsistencies are treated the same as findings for scoring
    for inconsistency in inconsistencies:
        severity = inconsistency.severity
        
        # Validate severity and get points
        if severity in severity_points:
            points = severity_points[severity]
            total_score += points
            severity_counts[severity] += 1
            
            logger.debug(
                f"Inconsistency: {severity} = +{points} points"
            )
        else:
            # Handle invalid severity
            logger.warning(
                f"Invalid severity '{severity}' in inconsistency. "
                f"Defaulting to Medium (2 points)."
            )
            total_score += 2  # Default to Medium
            severity_counts["Invalid"] += 1
    
    # Determine risk classification based on total score
    # This implements Requirement 7.4
    if total_score <= 5:
        risk_classification = "Low"
    elif total_score <= 12:
        risk_classification = "Medium"
    else:  # total_score >= 13
        risk_classification = "High"
    
    # Log summary
    logger.info(
        f"Risk score calculation complete: {total_score} points "
        f"({severity_counts['High']} High, {severity_counts['Medium']} Medium, "
        f"{severity_counts['Low']} Low) = {risk_classification} Risk"
    )
    
    if severity_counts["Invalid"] > 0:
        logger.warning(
            f"{severity_counts['Invalid']} items had invalid severity values"
        )
    
    return total_score, risk_classification


def generate_risk_memo(
    financial_findings: List[RiskFinding],
    legal_findings: List[RiskFinding],
    operational_findings: List[RiskFinding],
    inconsistencies: List[Inconsistency],
    risk_score: int,
    risk_classification: str
) -> str:
    """
    Generate a structured investment risk memo in markdown format.
    
    This function creates a comprehensive due diligence report that aggregates
    all risk findings and inconsistencies into a well-organized markdown document.
    The memo is designed to be readable by both technical and non-technical
    stakeholders, providing clear evidence-backed risk assessments.
    
    Memo Structure (Requirements 8.1-8.6):
    
    1. Executive Summary
       - High-level overview of the analysis
       - Overall risk assessment and key takeaways
       - Summary of critical issues found
    
    2. Risk Breakdown
       - Financial Risks: Revenue, growth, cost concerns
       - Legal Risks: Contract, liability, IP concerns
       - Operational Risks: Personnel, vendor, scalability concerns
       - Cross-Document Inconsistencies: Contradictions and discrepancies
       - Each finding includes: description, severity, evidence, source citation
    
    3. Key Red Flags
       - Top 3-5 most critical issues requiring immediate attention
       - Extracted from High severity findings across all categories
       - Prioritized by potential impact on investment decision
    
    4. Evidence References
       - Complete list of all source documents cited
       - Organized by document name with page/section references
       - Enables traceability and verification of findings
    
    5. Final Risk Score
       - Numerical score and classification (Low/Medium/High)
       - Explanation of scoring methodology
       - Investment recommendation context
    
    Formatting Guidelines:
    - Use markdown headers (##, ###) for section hierarchy
    - Use bullet points for lists of findings
    - Use bold (**text**) for severity levels and key terms
    - Use blockquotes (>) for evidence excerpts
    - Use horizontal rules (---) to separate major sections
    - Ensure proper spacing for readability
    
    Edge Cases:
    - Empty findings in a category: Display "No risks identified"
    - No High severity findings: Key Red Flags section notes this
    - No inconsistencies: Section notes "No inconsistencies detected"
    - Missing source information: Display "Unknown source"
    
    Args:
        financial_findings: List of RiskFinding objects from Financial agent
        legal_findings: List of RiskFinding objects from Legal agent
        operational_findings: List of RiskFinding objects from Operational agent
        inconsistencies: List of Inconsistency objects from cross-document checks
        risk_score: Total risk score (integer)
        risk_classification: Risk classification string ("Low", "Medium", or "High")
    
    Returns:
        Formatted markdown string containing the complete risk memo
    
    Example Output Structure:
        # Investment Risk Memo
        
        ## Executive Summary
        This due diligence analysis identified 12 risks across financial, legal,
        and operational dimensions...
        
        ## Risk Breakdown
        
        ### Financial Risks
        - **High**: Revenue projections lack supporting data...
        
        [... more sections ...]
        
        ## Final Risk Score
        **Overall Risk: High**
        **Score: 15 / ∞**
    
    Requirements Validation:
    - Requirement 8.1: Includes Executive Summary section
    - Requirement 8.2: Includes Risk Breakdown section organized by category
    - Requirement 8.3: Includes Key Red Flags section highlighting critical issues
    - Requirement 8.4: Includes Evidence References section with all citations
    - Requirement 8.5: Includes Final Risk Score with classification
    - Requirement 8.6: Outputs structured markdown format
    """
    import logging
    from datetime import datetime
    
    logger = logging.getLogger(__name__)
    logger.info("Generating investment risk memo...")
    
    # Start building the memo
    memo_lines = []
    
    # Header
    memo_lines.append("# Investment Risk Memo")
    memo_lines.append("")
    memo_lines.append(f"**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    memo_lines.append("")
    memo_lines.append("---")
    memo_lines.append("")
    
    # Section 1: Executive Summary (Requirement 8.1)
    memo_lines.append("## Executive Summary")
    memo_lines.append("")
    
    # Count total findings
    total_findings = len(financial_findings) + len(legal_findings) + len(operational_findings)
    total_inconsistencies = len(inconsistencies)
    
    # Count by severity
    all_items = financial_findings + legal_findings + operational_findings + inconsistencies
    high_count = sum(1 for item in all_items if item.severity == "High")
    medium_count = sum(1 for item in all_items if item.severity == "Medium")
    low_count = sum(1 for item in all_items if item.severity == "Low")
    
    # Generate executive summary text
    memo_lines.append(
        f"This due diligence analysis identified **{total_findings} risk findings** "
        f"and **{total_inconsistencies} cross-document inconsistencies** across "
        f"financial, legal, and operational dimensions."
    )
    memo_lines.append("")
    
    memo_lines.append(
        f"**Risk Distribution:** {high_count} High severity, {medium_count} Medium severity, "
        f"{low_count} Low severity"
    )
    memo_lines.append("")
    
    # Overall assessment based on classification
    if risk_classification == "High":
        memo_lines.append(
            "**Overall Assessment:** This investment presents **HIGH RISK**. "
            "Multiple critical issues have been identified that could significantly "
            "impact the investment decision. Serious consideration and further "
            "investigation are strongly recommended before proceeding."
        )
    elif risk_classification == "Medium":
        memo_lines.append(
            "**Overall Assessment:** This investment presents **MEDIUM RISK**. "
            "Several notable concerns have been identified that require further "
            "investigation. While potentially manageable, these issues should be "
            "addressed before finalizing the investment."
        )
    else:  # Low
        memo_lines.append(
            "**Overall Assessment:** This investment presents **LOW RISK**. "
            "Only minor issues or standard due diligence concerns have been identified. "
            "The investment appears relatively safe based on available documentation."
        )
    
    memo_lines.append("")
    memo_lines.append("---")
    memo_lines.append("")
    
    # Section 2: Risk Breakdown (Requirement 8.2)
    memo_lines.append("## Risk Breakdown")
    memo_lines.append("")
    
    # 2.1: Financial Risks
    memo_lines.append("### Financial Risks")
    memo_lines.append("")
    
    if financial_findings:
        for idx, finding in enumerate(financial_findings, 1):
            memo_lines.append(f"**{idx}. [{finding.severity}] {finding.risk_description}**")
            memo_lines.append("")
            memo_lines.append(f"*Evidence:* {finding.evidence}")
            memo_lines.append("")
            memo_lines.append(
                f"*Source:* {finding.source_document} ({finding.source_location})"
            )
            memo_lines.append("")
    else:
        memo_lines.append("No financial risks identified.")
        memo_lines.append("")
    
    # 2.2: Legal Risks
    memo_lines.append("### Legal Risks")
    memo_lines.append("")
    
    if legal_findings:
        for idx, finding in enumerate(legal_findings, 1):
            memo_lines.append(f"**{idx}. [{finding.severity}] {finding.risk_description}**")
            memo_lines.append("")
            memo_lines.append(f"*Evidence:* {finding.evidence}")
            memo_lines.append("")
            memo_lines.append(
                f"*Source:* {finding.source_document} ({finding.source_location})"
            )
            memo_lines.append("")
    else:
        memo_lines.append("No legal risks identified.")
        memo_lines.append("")
    
    # 2.3: Operational Risks
    memo_lines.append("### Operational Risks")
    memo_lines.append("")
    
    if operational_findings:
        for idx, finding in enumerate(operational_findings, 1):
            memo_lines.append(f"**{idx}. [{finding.severity}] {finding.risk_description}**")
            memo_lines.append("")
            memo_lines.append(f"*Evidence:* {finding.evidence}")
            memo_lines.append("")
            memo_lines.append(
                f"*Source:* {finding.source_document} ({finding.source_location})"
            )
            memo_lines.append("")
    else:
        memo_lines.append("No operational risks identified.")
        memo_lines.append("")
    
    # 2.4: Cross-Document Inconsistencies
    memo_lines.append("### Cross-Document Inconsistencies")
    memo_lines.append("")
    
    if inconsistencies:
        for idx, inconsistency in enumerate(inconsistencies, 1):
            memo_lines.append(
                f"**{idx}. [{inconsistency.severity}] {inconsistency.issue_description}**"
            )
            memo_lines.append("")
            memo_lines.append(f"*Details:* {inconsistency.details}")
            memo_lines.append("")
            docs_list = ", ".join(inconsistency.documents_involved)
            memo_lines.append(f"*Documents Involved:* {docs_list}")
            memo_lines.append("")
    else:
        memo_lines.append("No cross-document inconsistencies detected.")
        memo_lines.append("")
    
    memo_lines.append("---")
    memo_lines.append("")
    
    # Section 3: Key Red Flags (Requirement 8.3)
    memo_lines.append("## Key Red Flags")
    memo_lines.append("")
    memo_lines.append(
        "The following are the most critical issues requiring immediate attention:"
    )
    memo_lines.append("")
    
    # Extract all High severity items
    high_severity_items = []
    
    for finding in financial_findings:
        if finding.severity == "High":
            high_severity_items.append({
                'type': 'Financial Risk',
                'description': finding.risk_description,
                'source': f"{finding.source_document} ({finding.source_location})"
            })
    
    for finding in legal_findings:
        if finding.severity == "High":
            high_severity_items.append({
                'type': 'Legal Risk',
                'description': finding.risk_description,
                'source': f"{finding.source_document} ({finding.source_location})"
            })
    
    for finding in operational_findings:
        if finding.severity == "High":
            high_severity_items.append({
                'type': 'Operational Risk',
                'description': finding.risk_description,
                'source': f"{finding.source_document} ({finding.source_location})"
            })
    
    for inconsistency in inconsistencies:
        if inconsistency.severity == "High":
            docs_list = ", ".join(inconsistency.documents_involved)
            high_severity_items.append({
                'type': 'Inconsistency',
                'description': inconsistency.issue_description,
                'source': docs_list
            })
    
    # Display top 3-5 critical issues
    if high_severity_items:
        # Limit to top 5 if there are many
        top_red_flags = high_severity_items[:5]
        
        for idx, item in enumerate(top_red_flags, 1):
            memo_lines.append(f"**{idx}. {item['type']}: {item['description']}**")
            memo_lines.append(f"   - *Source:* {item['source']}")
            memo_lines.append("")
        
        if len(high_severity_items) > 5:
            memo_lines.append(
                f"*Note: {len(high_severity_items) - 5} additional High severity "
                f"issues identified. See Risk Breakdown section for complete list.*"
            )
            memo_lines.append("")
    else:
        memo_lines.append("No High severity issues identified.")
        memo_lines.append("")
    
    memo_lines.append("---")
    memo_lines.append("")
    
    # Section 4: Evidence References (Requirement 8.4)
    memo_lines.append("## Evidence References")
    memo_lines.append("")
    memo_lines.append(
        "All findings in this memo are supported by evidence from the following sources:"
    )
    memo_lines.append("")
    
    # Collect all unique source documents
    all_sources = set()
    
    for finding in financial_findings + legal_findings + operational_findings:
        all_sources.add(finding.source_document)
    
    for inconsistency in inconsistencies:
        for doc in inconsistency.documents_involved:
            all_sources.add(doc)
    
    # Display sources alphabetically
    if all_sources:
        sorted_sources = sorted(all_sources)
        for source in sorted_sources:
            # Collect all locations referenced in this source
            locations = set()
            
            for finding in financial_findings + legal_findings + operational_findings:
                if finding.source_document == source:
                    locations.add(finding.source_location)
            
            # Format locations
            if locations:
                locations_str = ", ".join(sorted(locations))
                memo_lines.append(f"- **{source}** (Referenced: {locations_str})")
            else:
                memo_lines.append(f"- **{source}**")
        
        memo_lines.append("")
    else:
        memo_lines.append("No source documents referenced.")
        memo_lines.append("")
    
    memo_lines.append("---")
    memo_lines.append("")
    
    # Section 5: Final Risk Score (Requirement 8.5)
    memo_lines.append("## Final Risk Score")
    memo_lines.append("")
    memo_lines.append(f"**Overall Risk: {risk_classification}**")
    memo_lines.append("")
    memo_lines.append(f"**Score: {risk_score}**")
    memo_lines.append("")
    memo_lines.append("**Scoring Methodology:**")
    memo_lines.append("- High severity: 3 points")
    memo_lines.append("- Medium severity: 2 points")
    memo_lines.append("- Low severity: 1 point")
    memo_lines.append("")
    memo_lines.append("**Risk Classification:**")
    memo_lines.append("- Low Risk: 0-5 points")
    memo_lines.append("- Medium Risk: 6-12 points")
    memo_lines.append("- High Risk: 13+ points")
    memo_lines.append("")
    
    # Join all lines into final memo
    memo = "\n".join(memo_lines)
    
    logger.info(
        f"Risk memo generated successfully ({len(memo)} characters, "
        f"{len(memo_lines)} lines)"
    )
    
    return memo
