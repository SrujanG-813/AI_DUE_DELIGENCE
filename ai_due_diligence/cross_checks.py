"""
Cross-Document Inconsistency Detection Module

This module provides rule-based heuristic checks to detect inconsistencies
across multiple business documents. It helps identify contradictions and
discrepancies that may indicate risks or data quality issues.
"""

from dataclasses import dataclass
from typing import List


@dataclass
class Inconsistency:
    """
    Represents a detected inconsistency across multiple documents.
    
    An inconsistency occurs when information in one document contradicts or
    conflicts with information in another document. This could include:
    - Mismatched financial figures (e.g., different revenue numbers)
    - Conflicting ownership claims (e.g., IP ownership disputes)
    - Contradictory operational statements (e.g., scalability vs. vendor lock-in)
    
    Attributes:
        issue_description: A clear, concise description of the inconsistency
        documents_involved: List of document filenames that contain the conflicting information
        severity: The severity level of the inconsistency ("Low", "Medium", or "High")
        details: Additional context and explanation about the inconsistency, including
                specific quotes or data points that conflict
    
    Example:
        Inconsistency(
            issue_description="Revenue mismatch between financial summary and contract",
            documents_involved=["financial_summary.pdf", "customer_contract.pdf"],
            severity="High",
            details="Financial summary reports $2M ARR, but contract shows $1.5M commitment"
        )
    """
    issue_description: str
    documents_involved: List[str]
    severity: str  # Must be one of: "Low", "Medium", "High"
    details: str

import re
from langchain_core.vectorstores import VectorStore
from ai_due_diligence.retriever import retrieve_relevant_chunks


def check_revenue_consistency(findings: List, vector_store: VectorStore) -> List[Inconsistency]:
    """
    Check for revenue mismatches across multiple documents.

    This function implements a heuristic-based approach to detect inconsistencies
    in revenue figures mentioned across different business documents. Revenue
    discrepancies can indicate data quality issues, outdated information, or
    potential misrepresentation.

    Detection Strategy:
    1. Extract revenue figures from financial risk findings (already analyzed by agents)
    2. Query vector store for additional revenue mentions in all documents
    3. Parse numeric values from both sources using regex patterns
    4. Compare all revenue figures and flag discrepancies > 10%

    Heuristic Logic:
    - Searches for common revenue patterns: "$X million", "$XM", "$X.XM ARR", etc.
    - Handles various formats: millions (M), thousands (K), with/without decimals
    - Normalizes all values to a common unit (dollars) for comparison
    - Uses 10% threshold as significant discrepancy (industry standard for due diligence)
    - Considers context: "revenue", "ARR", "annual revenue", "sales" keywords

    Limitations:
    - Simple regex-based extraction may miss complex phrasings
    - Cannot distinguish between different time periods (Q1 vs Q4 revenue)
    - May produce false positives if documents discuss projections vs actuals
    - Does not understand context like "target revenue" vs "actual revenue"

    These limitations are acceptable for MVP heuristic checks. A production system
    would use more sophisticated NLP or LLM-based extraction.

    Args:
        findings: List of RiskFinding objects from all agents
                 We primarily look at Financial agent findings for revenue mentions
        vector_store: FAISS VectorStore to query for additional revenue information
                     across all ingested documents

    Returns:
        List of Inconsistency objects describing detected revenue mismatches
        Returns empty list if no inconsistencies found or insufficient data

    Example:
        If financial_summary.pdf mentions "$2M ARR" and customer_contract.pdf
        mentions "$1.5M annual commitment", this function would detect a 25%
        discrepancy and flag it as a High severity inconsistency.

    Requirements Validation:
    - Requirement 6.1: Checks for revenue mismatches across multiple documents
    - Requirement 6.5: Uses rule-based heuristics for inconsistency detection
    """
    inconsistencies = []

    # Step 1: Extract revenue figures from financial findings
    # Financial agents may have already identified revenue-related risks
    revenue_from_findings = []

    for finding in findings:
        # Focus on financial findings that mention revenue
        if finding.agent_type == "Financial":
            # Look for revenue keywords in the finding
            if any(keyword in finding.risk_description.lower() or
                   keyword in finding.evidence.lower()
                   for keyword in ["revenue", "arr", "sales", "income"]):

                # Extract numeric values from the evidence text
                amounts = _extract_revenue_amounts(finding.evidence)

                for amount in amounts:
                    revenue_from_findings.append({
                        'amount': amount,
                        'source': finding.source_document,
                        'location': finding.source_location,
                        'context': finding.evidence[:100]  # First 100 chars for context
                    })

    # Step 2: Query vector store for additional revenue mentions
    # This catches revenue figures that might not have been flagged as risks
    revenue_queries = [
        "revenue annual recurring",
        "total revenue sales",
        "ARR MRR annual revenue",
        "financial performance revenue"
    ]

    revenue_from_retrieval = []

    for query in revenue_queries:
        try:
            # Retrieve relevant chunks (k=3 to avoid too many results)
            chunks = retrieve_relevant_chunks(vector_store, query, k=3)

            for doc, score in chunks:
                # Only consider highly relevant chunks (score < 1.0 is typically good)
                # This threshold may need tuning based on your embedding model
                if score < 1.0:
                    amounts = _extract_revenue_amounts(doc.page_content)

                    for amount in amounts:
                        revenue_from_retrieval.append({
                            'amount': amount,
                            'source': doc.metadata.get('source', 'unknown'),
                            'location': f"Page {doc.metadata.get('page', '?')}",
                            'context': doc.page_content[:100]
                        })
        except Exception as e:
            # Log error but continue - retrieval failures shouldn't break the check
            print(f"Warning: Failed to retrieve chunks for query '{query}': {e}")
            continue

    # Step 3: Combine all revenue figures
    all_revenue_figures = revenue_from_findings + revenue_from_retrieval

    # Remove duplicates (same amount from same source)
    # This prevents flagging the same figure mentioned multiple times in one document
    unique_revenues = []
    seen = set()

    for rev in all_revenue_figures:
        key = (rev['amount'], rev['source'])
        if key not in seen:
            seen.add(key)
            unique_revenues.append(rev)

    # Step 4: Compare revenue figures and detect discrepancies
    # We need at least 2 different figures to detect inconsistency
    if len(unique_revenues) < 2:
        return inconsistencies

    # Compare each pair of revenue figures
    for i in range(len(unique_revenues)):
        for j in range(i + 1, len(unique_revenues)):
            rev1 = unique_revenues[i]
            rev2 = unique_revenues[j]

            # Skip if from the same document (not a cross-document inconsistency)
            if rev1['source'] == rev2['source']:
                continue

            # Calculate percentage difference
            # Use the larger value as the base to avoid division issues
            larger = max(rev1['amount'], rev2['amount'])
            smaller = min(rev1['amount'], rev2['amount'])

            if larger == 0:
                continue  # Avoid division by zero

            percent_diff = ((larger - smaller) / larger) * 100

            # Flag discrepancies > 10%
            if percent_diff > 10:
                # Determine severity based on magnitude of discrepancy
                if percent_diff > 30:
                    severity = "High"
                elif percent_diff > 20:
                    severity = "Medium"
                else:
                    severity = "Low"

                # Format the amounts for display
                rev1_formatted = _format_amount(rev1['amount'])
                rev2_formatted = _format_amount(rev2['amount'])

                inconsistency = Inconsistency(
                    issue_description=f"Revenue mismatch detected: {percent_diff:.1f}% discrepancy",
                    documents_involved=[rev1['source'], rev2['source']],
                    severity=severity,
                    details=(
                        f"{rev1['source']} ({rev1['location']}) reports {rev1_formatted}, "
                        f"but {rev2['source']} ({rev2['location']}) reports {rev2_formatted}. "
                        f"Discrepancy: {percent_diff:.1f}%. "
                        f"Context 1: '{rev1['context']}...' "
                        f"Context 2: '{rev2['context']}...'"
                    )
                )

                inconsistencies.append(inconsistency)

    return inconsistencies


def _extract_revenue_amounts(text: str) -> List[float]:
    """
    Extract revenue amounts from text using regex patterns.

    This helper function uses regular expressions to find monetary values
    in various common formats. It handles:
    - Dollar signs: $2M, $2.5M, $2,500,000
    - Suffixes: M (million), K (thousand), B (billion)
    - Decimals: 2.5M, 1.25K
    - Commas: 2,500,000

    Regex Pattern Explanation:
    - \\$? : Optional dollar sign
    - ([\\d,]+\\.?\\d*) : Capture digits with optional commas and decimal
    - \\s* : Optional whitespace
    - ([MKB])? : Optional suffix (M=million, K=thousand, B=billion)

    Args:
        text: Text to search for revenue amounts

    Returns:
        List of amounts normalized to dollars (float)
        Example: "$2.5M" -> [2500000.0]
    """
    amounts = []

    # Pattern 1: $X.XM, $XM, $X.XK, $XK, $X.XB, $XB
    # Matches: $2M, $2.5M, $500K, $1.2B
    pattern1 = r'\$?\s*([\d,]+\.?\d*)\s*([MKB])\b'
    matches1 = re.finditer(pattern1, text, re.IGNORECASE)

    for match in matches1:
        value = float(match.group(1).replace(',', ''))
        suffix = match.group(2).upper()

        # Convert to dollars
        if suffix == 'K':
            value *= 1_000
        elif suffix == 'M':
            value *= 1_000_000
        elif suffix == 'B':
            value *= 1_000_000_000

        amounts.append(value)

    # Pattern 2: $X,XXX,XXX or $XXXXXX (raw dollar amounts)
    # Matches: $2,500,000 or $2500000
    pattern2 = r'\$\s*([\d,]+)\b'
    matches2 = re.finditer(pattern2, text)

    for match in matches2:
        value_str = match.group(1).replace(',', '')
        # Only consider if it's a substantial amount (> $1000)
        # This filters out small amounts that are unlikely to be revenue
        if len(value_str) >= 4:
            value = float(value_str)
            if value >= 1000:
                amounts.append(value)

    return amounts


def _format_amount(amount: float) -> str:
    """
    Format a dollar amount for human-readable display.

    Converts large numbers to abbreviated format with appropriate suffix.

    Args:
        amount: Dollar amount as float

    Returns:
        Formatted string (e.g., "$2.5M", "$500K", "$1.2B")
    """
    if amount >= 1_000_000_000:
        return f"${amount / 1_000_000_000:.2f}B"
    elif amount >= 1_000_000:
        return f"${amount / 1_000_000:.2f}M"
    elif amount >= 1_000:
        return f"${amount / 1_000:.2f}K"
    else:
        return f"${amount:.2f}"



import re
from langchain_core.vectorstores import VectorStore
from ai_due_diligence.retriever import retrieve_relevant_chunks


def check_revenue_consistency(findings: List, vector_store: VectorStore) -> List[Inconsistency]:
    """
    Check for revenue mismatches across multiple documents.
    
    This function implements a heuristic-based approach to detect inconsistencies
    in revenue figures mentioned across different business documents. Revenue
    discrepancies can indicate data quality issues, outdated information, or
    potential misrepresentation.
    
    Detection Strategy:
    1. Extract revenue figures from financial risk findings (already analyzed by agents)
    2. Query vector store for additional revenue mentions in all documents
    3. Parse numeric values from both sources using regex patterns
    4. Compare all revenue figures and flag discrepancies > 10%
    
    Heuristic Logic:
    - Searches for common revenue patterns: "$X million", "$XM", "$X.XM ARR", etc.
    - Handles various formats: millions (M), thousands (K), with/without decimals
    - Normalizes all values to a common unit (dollars) for comparison
    - Uses 10% threshold as significant discrepancy (industry standard for due diligence)
    - Considers context: "revenue", "ARR", "annual revenue", "sales" keywords
    
    Limitations:
    - Simple regex-based extraction may miss complex phrasings
    - Cannot distinguish between different time periods (Q1 vs Q4 revenue)
    - May produce false positives if documents discuss projections vs actuals
    - Does not understand context like "target revenue" vs "actual revenue"
    
    These limitations are acceptable for MVP heuristic checks. A production system
    would use more sophisticated NLP or LLM-based extraction.
    
    Args:
        findings: List of RiskFinding objects from all agents
                 We primarily look at Financial agent findings for revenue mentions
        vector_store: FAISS VectorStore to query for additional revenue information
                     across all ingested documents
    
    Returns:
        List of Inconsistency objects describing detected revenue mismatches
        Returns empty list if no inconsistencies found or insufficient data
        
    Example:
        If financial_summary.pdf mentions "$2M ARR" and customer_contract.pdf
        mentions "$1.5M annual commitment", this function would detect a 25%
        discrepancy and flag it as a High severity inconsistency.
        
    Requirements Validation:
    - Requirement 6.1: Checks for revenue mismatches across multiple documents
    - Requirement 6.5: Uses rule-based heuristics for inconsistency detection
    """
    inconsistencies = []
    
    # Step 1: Extract revenue figures from financial findings
    # Financial agents may have already identified revenue-related risks
    revenue_from_findings = []
    
    for finding in findings:
        # Focus on financial findings that mention revenue
        if finding.agent_type == "Financial":
            # Look for revenue keywords in the finding
            if any(keyword in finding.risk_description.lower() or 
                   keyword in finding.evidence.lower() 
                   for keyword in ["revenue", "arr", "sales", "income"]):
                
                # Extract numeric values from the evidence text
                amounts = _extract_revenue_amounts(finding.evidence)
                
                for amount in amounts:
                    revenue_from_findings.append({
                        'amount': amount,
                        'source': finding.source_document,
                        'location': finding.source_location,
                        'context': finding.evidence[:100]  # First 100 chars for context
                    })
    
    # Step 2: Query vector store for additional revenue mentions
    # This catches revenue figures that might not have been flagged as risks
    revenue_queries = [
        "revenue annual recurring",
        "total revenue sales",
        "ARR MRR annual revenue",
        "financial performance revenue"
    ]
    
    revenue_from_retrieval = []
    
    for query in revenue_queries:
        try:
            # Retrieve relevant chunks (k=3 to avoid too many results)
            chunks = retrieve_relevant_chunks(vector_store, query, k=3)
            
            for doc, score in chunks:
                # Only consider highly relevant chunks (score < 1.0 is typically good)
                # This threshold may need tuning based on your embedding model
                if score < 1.0:
                    amounts = _extract_revenue_amounts(doc.page_content)
                    
                    for amount in amounts:
                        revenue_from_retrieval.append({
                            'amount': amount,
                            'source': doc.metadata.get('source', 'unknown'),
                            'location': f"Page {doc.metadata.get('page', '?')}",
                            'context': doc.page_content[:100]
                        })
        except Exception as e:
            # Log error but continue - retrieval failures shouldn't break the check
            print(f"Warning: Failed to retrieve chunks for query '{query}': {e}")
            continue
    
    # Step 3: Combine all revenue figures
    all_revenue_figures = revenue_from_findings + revenue_from_retrieval
    
    # Remove duplicates (same amount from same source)
    # This prevents flagging the same figure mentioned multiple times in one document
    unique_revenues = []
    seen = set()
    
    for rev in all_revenue_figures:
        key = (rev['amount'], rev['source'])
        if key not in seen:
            seen.add(key)
            unique_revenues.append(rev)
    
    # Step 4: Compare revenue figures and detect discrepancies
    # We need at least 2 different figures to detect inconsistency
    if len(unique_revenues) < 2:
        return inconsistencies
    
    # Compare each pair of revenue figures
    for i in range(len(unique_revenues)):
        for j in range(i + 1, len(unique_revenues)):
            rev1 = unique_revenues[i]
            rev2 = unique_revenues[j]
            
            # Skip if from the same document (not a cross-document inconsistency)
            if rev1['source'] == rev2['source']:
                continue
            
            # Calculate percentage difference
            # Use the larger value as the base to avoid division issues
            larger = max(rev1['amount'], rev2['amount'])
            smaller = min(rev1['amount'], rev2['amount'])
            
            if larger == 0:
                continue  # Avoid division by zero
            
            percent_diff = ((larger - smaller) / larger) * 100
            
            # Flag discrepancies > 10%
            if percent_diff > 10:
                # Determine severity based on magnitude of discrepancy
                if percent_diff > 30:
                    severity = "High"
                elif percent_diff > 20:
                    severity = "Medium"
                else:
                    severity = "Low"
                
                # Format the amounts for display
                rev1_formatted = _format_amount(rev1['amount'])
                rev2_formatted = _format_amount(rev2['amount'])
                
                inconsistency = Inconsistency(
                    issue_description=f"Revenue mismatch detected: {percent_diff:.1f}% discrepancy",
                    documents_involved=[rev1['source'], rev2['source']],
                    severity=severity,
                    details=(
                        f"{rev1['source']} ({rev1['location']}) reports {rev1_formatted}, "
                        f"but {rev2['source']} ({rev2['location']}) reports {rev2_formatted}. "
                        f"Discrepancy: {percent_diff:.1f}%. "
                        f"Context 1: '{rev1['context']}...' "
                        f"Context 2: '{rev2['context']}...'"
                    )
                )
                
                inconsistencies.append(inconsistency)
    
    return inconsistencies



def check_ip_ownership_conflicts(findings: List, vector_store: VectorStore) -> List[Inconsistency]:
    """
    Check for intellectual property (IP) ownership conflicts across multiple documents.
    
    This function implements a keyword-based heuristic approach to detect conflicting
    or ambiguous IP ownership claims across different business documents. IP ownership
    conflicts can indicate legal risks, unclear rights, or potential disputes that
    could affect the value or viability of an investment.
    
    Detection Strategy:
    1. Extract IP ownership statements from legal risk findings (already analyzed by agents)
    2. Query vector store for additional IP ownership mentions across all documents
    3. Use keyword matching to identify ownership claims and parties
    4. Compare ownership statements and flag conflicting claims
    
    Heuristic Logic:
    - Searches for IP-related keywords: "intellectual property", "IP", "patent", 
      "trademark", "copyright", "trade secret", "proprietary"
    - Identifies ownership indicators: "owned by", "belongs to", "property of",
      "rights held by", "assigned to", "licensed to"
    - Detects potential conflicts when:
      * Different parties claim ownership of the same IP
      * Ownership is ambiguous or unclear (e.g., "jointly owned", "disputed")
      * License vs. ownership confusion (e.g., "licensed" vs "owned")
      * Missing ownership documentation
    - Flags statements from different documents that contradict each other
    
    Keyword Categories:
    - IP Types: patent, trademark, copyright, trade secret, IP, intellectual property
    - Ownership Terms: owned, belongs, property of, rights, assigned, transferred
    - Ambiguity Terms: licensed, shared, joint, disputed, unclear, pending
    - Parties: company, founder, employee, contractor, vendor, third party
    
    Limitations:
    - Simple keyword matching may miss nuanced legal language
    - Cannot parse complex legal clauses or understand context fully
    - May not distinguish between different types of IP (patent vs trademark)
    - Cannot verify actual legal ownership (requires legal document review)
    - May produce false positives if documents discuss hypothetical scenarios
    
    These limitations are acceptable for MVP heuristic checks. A production system
    would use legal NLP models or require manual legal review.
    
    Args:
        findings: List of RiskFinding objects from all agents
                 We primarily look at Legal agent findings for IP mentions
        vector_store: FAISS VectorStore to query for additional IP ownership information
                     across all ingested documents
    
    Returns:
        List of Inconsistency objects describing detected IP ownership conflicts
        Returns empty list if no conflicts found or insufficient data
        
    Example:
        If customer_contract.pdf states "All IP owned by Customer" but
        internal_policy.pdf states "Company retains all IP rights", this function
        would detect a conflict and flag it as a High severity inconsistency.
        
    Requirements Validation:
    - Requirement 6.2: Checks for IP ownership conflicts across multiple documents
    - Requirement 6.5: Uses rule-based heuristics for inconsistency detection
    """
    inconsistencies = []
    
    # Step 1: Extract IP ownership statements from legal findings
    # Legal agents may have already identified IP-related risks
    ip_from_findings = []
    
    for finding in findings:
        # Focus on legal findings that mention IP
        if finding.agent_type == "Legal":
            # Look for IP keywords in the finding
            if any(keyword in finding.risk_description.lower() or 
                   keyword in finding.evidence.lower() 
                   for keyword in ["intellectual property", "ip", "patent", "trademark", 
                                  "copyright", "trade secret", "proprietary"]):
                
                # Extract ownership claims from the evidence text
                ownership_claims = _extract_ip_ownership_claims(finding.evidence)
                
                for claim in ownership_claims:
                    ip_from_findings.append({
                        'claim': claim,
                        'source': finding.source_document,
                        'location': finding.source_location,
                        'context': finding.evidence[:150]  # First 150 chars for context
                    })
    
    # Step 2: Query vector store for additional IP ownership mentions
    # This catches IP statements that might not have been flagged as risks
    ip_queries = [
        "intellectual property ownership rights",
        "patent trademark copyright owned",
        "IP rights belongs to",
        "proprietary technology ownership",
        "trade secret rights holder"
    ]
    
    ip_from_retrieval = []
    
    for query in ip_queries:
        try:
            # Retrieve relevant chunks (k=4 to get broader coverage)
            chunks = retrieve_relevant_chunks(vector_store, query, k=4)
            
            for doc, score in chunks:
                # Only consider highly relevant chunks
                # IP ownership is critical, so we use a stricter threshold
                if score < 0.8:
                    ownership_claims = _extract_ip_ownership_claims(doc.page_content)
                    
                    for claim in ownership_claims:
                        ip_from_retrieval.append({
                            'claim': claim,
                            'source': doc.metadata.get('source', 'unknown'),
                            'location': f"Page {doc.metadata.get('page', '?')}",
                            'context': doc.page_content[:150]
                        })
        except Exception as e:
            # Log error but continue - retrieval failures shouldn't break the check
            print(f"Warning: Failed to retrieve chunks for query '{query}': {e}")
            continue
    
    # Step 3: Combine all IP ownership statements
    all_ip_statements = ip_from_findings + ip_from_retrieval
    
    # Remove duplicates (same claim from same source)
    unique_ip_statements = []
    seen = set()
    
    for ip_stmt in all_ip_statements:
        # Use claim text and source as uniqueness key
        key = (ip_stmt['claim'].lower().strip(), ip_stmt['source'])
        if key not in seen:
            seen.add(key)
            unique_ip_statements.append(ip_stmt)
    
    # Step 4: Detect conflicts by comparing ownership claims
    # We need at least 2 statements to detect conflicts
    if len(unique_ip_statements) < 2:
        return inconsistencies
    
    # Compare each pair of IP ownership statements
    for i in range(len(unique_ip_statements)):
        for j in range(i + 1, len(unique_ip_statements)):
            stmt1 = unique_ip_statements[i]
            stmt2 = unique_ip_statements[j]
            
            # Skip if from the same document (not a cross-document inconsistency)
            if stmt1['source'] == stmt2['source']:
                continue
            
            # Check if the claims conflict
            conflict_detected, conflict_type, severity = _detect_ip_conflict(
                stmt1['claim'], stmt2['claim']
            )
            
            if conflict_detected:
                inconsistency = Inconsistency(
                    issue_description=f"IP ownership conflict detected: {conflict_type}",
                    documents_involved=[stmt1['source'], stmt2['source']],
                    severity=severity,
                    details=(
                        f"{stmt1['source']} ({stmt1['location']}) states: '{stmt1['claim']}'. "
                        f"However, {stmt2['source']} ({stmt2['location']}) states: '{stmt2['claim']}'. "
                        f"These statements appear to conflict regarding IP ownership. "
                        f"Context 1: '{stmt1['context']}...' "
                        f"Context 2: '{stmt2['context']}...'"
                    )
                )
                
                inconsistencies.append(inconsistency)
    
    return inconsistencies


def _extract_ip_ownership_claims(text: str) -> List[str]:
    """
    Extract IP ownership claims from text using keyword matching.
    
    This helper function identifies sentences or phrases that make claims about
    intellectual property ownership. It looks for combinations of IP-related
    keywords and ownership indicators.
    
    Detection Approach:
    1. Split text into sentences
    2. For each sentence, check if it contains both:
       - An IP-related keyword (patent, trademark, IP, etc.)
       - An ownership indicator (owned by, belongs to, rights, etc.)
    3. Extract and return matching sentences as ownership claims
    
    Args:
        text: Text to search for IP ownership claims
    
    Returns:
        List of strings, each representing an IP ownership claim
        Example: ["All IP owned by Company", "Patents belong to Founder"]
    """
    claims = []
    
    # IP-related keywords to look for
    ip_keywords = [
        'intellectual property', 'ip', 'patent', 'trademark', 'copyright',
        'trade secret', 'proprietary', 'technology', 'software', 'code'
    ]
    
    # Ownership indicator keywords
    ownership_keywords = [
        'owned', 'belongs', 'property of', 'rights', 'assigned', 'transferred',
        'held by', 'vested', 'retained', 'licensed', 'joint', 'shared'
    ]
    
    # Split text into sentences (simple approach using periods)
    # More sophisticated sentence splitting could use NLTK or spaCy
    sentences = re.split(r'[.!?]+', text)
    
    for sentence in sentences:
        sentence_lower = sentence.lower().strip()
        
        # Skip very short sentences (likely not meaningful claims)
        if len(sentence_lower) < 10:
            continue
        
        # Check if sentence contains both IP keyword and ownership keyword
        has_ip_keyword = any(keyword in sentence_lower for keyword in ip_keywords)
        has_ownership_keyword = any(keyword in sentence_lower for keyword in ownership_keywords)
        
        if has_ip_keyword and has_ownership_keyword:
            # Clean up the sentence and add to claims
            claim = sentence.strip()
            if claim:
                claims.append(claim)
    
    return claims


def _detect_ip_conflict(claim1: str, claim2: str) -> tuple[bool, str, str]:
    """
    Detect if two IP ownership claims conflict with each other.
    
    This helper function analyzes two IP ownership claims to determine if they
    contradict each other. It uses keyword-based heuristics to identify conflicts.
    
    Conflict Detection Logic:
    1. Ownership vs License: One claims ownership, other mentions licensing
    2. Different Parties: Different entities claim ownership of similar IP
    3. Ambiguity: One is clear, other is ambiguous (joint, disputed, unclear)
    4. Contradictory Terms: Direct contradictions (e.g., "owned by X" vs "owned by Y")
    
    Args:
        claim1: First IP ownership claim
        claim2: Second IP ownership claim
    
    Returns:
        Tuple of (conflict_detected: bool, conflict_type: str, severity: str)
        - conflict_detected: True if a conflict is detected
        - conflict_type: Description of the type of conflict
        - severity: "High", "Medium", or "Low" based on conflict severity
    """
    claim1_lower = claim1.lower()
    claim2_lower = claim2.lower()
    
    # Define conflict indicators
    ownership_strong = ['owned by', 'property of', 'belongs to', 'rights held by', 'assigned to']
    ownership_weak = ['licensed', 'joint', 'shared', 'disputed', 'unclear', 'pending']
    
    # Check for strong ownership claims in both
    claim1_has_strong = any(term in claim1_lower for term in ownership_strong)
    claim2_has_strong = any(term in claim2_lower for term in ownership_strong)
    
    # Check for weak/ambiguous ownership in both
    claim1_has_weak = any(term in claim1_lower for term in ownership_weak)
    claim2_has_weak = any(term in claim2_lower for term in ownership_weak)
    
    # Conflict Type 1: One strong ownership, one weak/ambiguous
    if claim1_has_strong and claim2_has_weak:
        return (True, "Ownership vs licensing/ambiguity conflict", "Medium")
    if claim2_has_strong and claim1_has_weak:
        return (True, "Ownership vs licensing/ambiguity conflict", "Medium")
    
    # Conflict Type 2: Both have strong ownership claims but mention different parties
    if claim1_has_strong and claim2_has_strong:
        # Extract potential party names (simple heuristic: capitalized words)
        parties1 = set(re.findall(r'\b[A-Z][a-z]+\b', claim1))
        parties2 = set(re.findall(r'\b[A-Z][a-z]+\b', claim2))
        
        # Also check for common party indicators
        party_indicators = ['company', 'customer', 'vendor', 'founder', 'employee', 'contractor']
        parties1_indicators = set(word for word in party_indicators if word in claim1_lower)
        parties2_indicators = set(word for word in party_indicators if word in claim2_lower)
        
        # If different parties are mentioned, it's a potential conflict
        if (parties1 and parties2 and parties1 != parties2) or \
           (parties1_indicators and parties2_indicators and parties1_indicators != parties2_indicators):
            return (True, "Different parties claim IP ownership", "High")
    
    # Conflict Type 3: Contradictory terms (e.g., "retained" vs "transferred")
    contradictory_pairs = [
        (['retained', 'kept'], ['transferred', 'assigned', 'sold']),
        (['exclusive', 'solely'], ['joint', 'shared', 'co-owned']),
        (['owned', 'property of'], ['licensed to', 'leased to'])
    ]
    
    for pair1, pair2 in contradictory_pairs:
        has_pair1_in_claim1 = any(term in claim1_lower for term in pair1)
        has_pair2_in_claim1 = any(term in claim1_lower for term in pair2)
        has_pair1_in_claim2 = any(term in claim2_lower for term in pair1)
        has_pair2_in_claim2 = any(term in claim2_lower for term in pair2)
        
        # If one claim has pair1 terms and other has pair2 terms, it's a conflict
        if (has_pair1_in_claim1 and has_pair2_in_claim2) or \
           (has_pair2_in_claim1 and has_pair1_in_claim2):
            return (True, "Contradictory IP ownership terms", "High")
    
    # No clear conflict detected
    return (False, "", "Low")



def check_scalability_vendor_conflicts(findings: List, vector_store: VectorStore) -> List[Inconsistency]:
    """
    Check for conflicts between scalability claims and vendor dependency statements.
    
    This function implements a keyword-based heuristic approach to detect contradictions
    between optimistic scalability claims and concerning vendor lock-in or dependency
    statements across different business documents. Such contradictions can indicate
    unrealistic operational assumptions or hidden risks that could affect scalability.
    
    Detection Strategy:
    1. Extract scalability claims from operational risk findings (already analyzed by agents)
    2. Query vector store for additional scalability and vendor dependency mentions
    3. Use keyword matching to identify positive scalability claims vs. vendor lock-in concerns
    4. Compare statements and flag contradictions
    
    Heuristic Logic:
    - Searches for scalability keywords: "scalable", "scale", "elastic", "flexible",
      "distributed", "cloud-native", "horizontal scaling", "auto-scale"
    - Searches for vendor lock-in keywords: "vendor lock-in", "single vendor",
      "proprietary", "dependent on", "tied to", "locked into", "cannot migrate"
    - Detects contradictions when:
      * Document claims high scalability but mentions critical vendor dependencies
      * Document claims flexibility but describes proprietary/locked-in infrastructure
      * Document claims easy scaling but mentions single-vendor constraints
      * Scalability claims contradict operational reality of vendor dependencies
    
    Keyword Categories:
    - Positive Scalability: scalable, elastic, flexible, distributed, cloud-native,
      horizontal scaling, auto-scale, easily scale, rapid growth
    - Vendor Lock-in: vendor lock-in, single vendor, proprietary, dependent on,
      tied to, locked into, cannot migrate, migration difficult, switching costs
    - Infrastructure: infrastructure, platform, hosting, cloud provider, database,
      storage, compute, services
    
    Limitations:
    - Simple keyword matching may miss nuanced operational descriptions
    - Cannot assess actual technical feasibility of scalability claims
    - May not distinguish between different types of dependencies (critical vs. minor)
    - Cannot evaluate whether vendor lock-in actually prevents scaling
    - May produce false positives if documents discuss mitigation strategies
    
    These limitations are acceptable for MVP heuristic checks. A production system
    would use technical architecture analysis or expert operational review.
    
    Args:
        findings: List of RiskFinding objects from all agents
                 We primarily look at Operational agent findings for scalability/vendor mentions
        vector_store: FAISS VectorStore to query for additional scalability and vendor information
                     across all ingested documents
    
    Returns:
        List of Inconsistency objects describing detected scalability-vendor contradictions
        Returns empty list if no contradictions found or insufficient data
        
    Example:
        If product_doc.pdf claims "Highly scalable cloud-native architecture" but
        internal_policy.pdf states "Critical dependency on single vendor's proprietary
        database with high migration costs", this function would detect a contradiction
        and flag it as a High severity inconsistency.
        
    Requirements Validation:
    - Requirement 6.3: Checks for conflicts between scalability claims and vendor dependencies
    - Requirement 6.5: Uses rule-based heuristics for inconsistency detection
    """
    inconsistencies = []
    
    # Step 1: Extract scalability and vendor statements from operational findings
    # Operational agents may have already identified scalability or vendor-related risks
    scalability_statements = []
    vendor_statements = []
    
    for finding in findings:
        # Focus on operational findings
        if finding.agent_type == "Operational":
            finding_text = (finding.risk_description + " " + finding.evidence).lower()
            
            # Check for scalability-related content
            if any(keyword in finding_text 
                   for keyword in ["scalability", "scalable", "scale", "elastic", 
                                  "flexible", "distributed", "cloud-native"]):
                
                # Extract scalability claims
                claims = _extract_scalability_claims(finding.evidence)
                
                for claim in claims:
                    scalability_statements.append({
                        'statement': claim,
                        'type': 'scalability',
                        'source': finding.source_document,
                        'location': finding.source_location,
                        'context': finding.evidence[:150]
                    })
            
            # Check for vendor dependency content
            if any(keyword in finding_text 
                   for keyword in ["vendor", "dependency", "dependent", "lock-in", 
                                  "proprietary", "single point", "tied to"]):
                
                # Extract vendor dependency statements
                statements = _extract_vendor_dependency_statements(finding.evidence)
                
                for stmt in statements:
                    vendor_statements.append({
                        'statement': stmt,
                        'type': 'vendor',
                        'source': finding.source_document,
                        'location': finding.source_location,
                        'context': finding.evidence[:150]
                    })
    
    # Step 2: Query vector store for additional scalability claims
    scalability_queries = [
        "scalable architecture elastic infrastructure",
        "horizontal scaling distributed system",
        "cloud-native flexible platform",
        "rapid growth scale capacity"
    ]
    
    for query in scalability_queries:
        try:
            chunks = retrieve_relevant_chunks(vector_store, query, k=3)
            
            for doc, score in chunks:
                if score < 1.0:
                    claims = _extract_scalability_claims(doc.page_content)
                    
                    for claim in claims:
                        scalability_statements.append({
                            'statement': claim,
                            'type': 'scalability',
                            'source': doc.metadata.get('source', 'unknown'),
                            'location': f"Page {doc.metadata.get('page', '?')}",
                            'context': doc.page_content[:150]
                        })
        except Exception as e:
            print(f"Warning: Failed to retrieve chunks for query '{query}': {e}")
            continue
    
    # Step 3: Query vector store for vendor dependency mentions
    vendor_queries = [
        "vendor lock-in dependency proprietary",
        "single vendor tied to platform",
        "migration difficult switching costs",
        "dependent on provider infrastructure"
    ]
    
    for query in vendor_queries:
        try:
            chunks = retrieve_relevant_chunks(vector_store, query, k=3)
            
            for doc, score in chunks:
                if score < 1.0:
                    statements = _extract_vendor_dependency_statements(doc.page_content)
                    
                    for stmt in statements:
                        vendor_statements.append({
                            'statement': stmt,
                            'type': 'vendor',
                            'source': doc.metadata.get('source', 'unknown'),
                            'location': f"Page {doc.metadata.get('page', '?')}",
                            'context': doc.page_content[:150]
                        })
        except Exception as e:
            print(f"Warning: Failed to retrieve chunks for query '{query}': {e}")
            continue
    
    # Step 4: Remove duplicates
    unique_scalability = []
    seen_scalability = set()
    
    for stmt in scalability_statements:
        key = (stmt['statement'].lower().strip(), stmt['source'])
        if key not in seen_scalability:
            seen_scalability.add(key)
            unique_scalability.append(stmt)
    
    unique_vendor = []
    seen_vendor = set()
    
    for stmt in vendor_statements:
        key = (stmt['statement'].lower().strip(), stmt['source'])
        if key not in seen_vendor:
            seen_vendor.add(key)
            unique_vendor.append(stmt)
    
    # Step 5: Detect contradictions between scalability claims and vendor dependencies
    # We need at least one of each type to detect contradictions
    if len(unique_scalability) == 0 or len(unique_vendor) == 0:
        return inconsistencies
    
    # Compare scalability claims against vendor dependency statements
    for scale_stmt in unique_scalability:
        for vendor_stmt in unique_vendor:
            
            # Skip if from the same document (not a cross-document inconsistency)
            if scale_stmt['source'] == vendor_stmt['source']:
                continue
            
            # Check if the statements contradict each other
            contradiction_detected, contradiction_type, severity = _detect_scalability_vendor_contradiction(
                scale_stmt['statement'], vendor_stmt['statement']
            )
            
            if contradiction_detected:
                inconsistency = Inconsistency(
                    issue_description=f"Scalability-vendor contradiction detected: {contradiction_type}",
                    documents_involved=[scale_stmt['source'], vendor_stmt['source']],
                    severity=severity,
                    details=(
                        f"{scale_stmt['source']} ({scale_stmt['location']}) claims: '{scale_stmt['statement']}'. "
                        f"However, {vendor_stmt['source']} ({vendor_stmt['location']}) states: '{vendor_stmt['statement']}'. "
                        f"These statements appear to contradict regarding scalability and vendor dependencies. "
                        f"Context 1: '{scale_stmt['context']}...' "
                        f"Context 2: '{vendor_stmt['context']}...'"
                    )
                )
                
                inconsistencies.append(inconsistency)
    
    return inconsistencies


def _extract_scalability_claims(text: str) -> List[str]:
    """
    Extract scalability claims from text using keyword matching.
    
    This helper function identifies sentences or phrases that make positive claims
    about system scalability, elasticity, or flexibility. It looks for combinations
    of scalability-related keywords and positive indicators.
    
    Detection Approach:
    1. Split text into sentences
    2. For each sentence, check if it contains:
       - A scalability keyword (scalable, elastic, distributed, etc.)
       - A positive indicator (highly, easily, seamlessly, etc.) OR
       - A capability statement (can scale, supports growth, etc.)
    3. Extract and return matching sentences as scalability claims
    
    Args:
        text: Text to search for scalability claims
    
    Returns:
        List of strings, each representing a scalability claim
        Example: ["Highly scalable cloud-native architecture", "Can easily scale to handle growth"]
    """
    claims = []
    
    # Scalability-related keywords
    scalability_keywords = [
        'scalable', 'scalability', 'scale', 'elastic', 'elasticity',
        'flexible', 'flexibility', 'distributed', 'cloud-native',
        'horizontal scaling', 'auto-scale', 'auto-scaling', 'growth capacity'
    ]
    
    # Positive indicators that suggest a claim
    positive_indicators = [
        'highly', 'easily', 'seamlessly', 'efficiently', 'rapidly',
        'can scale', 'able to scale', 'supports growth', 'handles growth',
        'designed to scale', 'built to scale', 'unlimited', 'infinite'
    ]
    
    # Split text into sentences
    sentences = re.split(r'[.!?]+', text)
    
    for sentence in sentences:
        sentence_lower = sentence.lower().strip()
        
        # Skip very short sentences
        if len(sentence_lower) < 15:
            continue
        
        # Check if sentence contains scalability keyword
        has_scalability_keyword = any(keyword in sentence_lower for keyword in scalability_keywords)
        
        # Check if sentence has positive indicator
        has_positive_indicator = any(indicator in sentence_lower for indicator in positive_indicators)
        
        # If both are present, it's likely a scalability claim
        if has_scalability_keyword and has_positive_indicator:
            claim = sentence.strip()
            if claim:
                claims.append(claim)
    
    return claims


def _extract_vendor_dependency_statements(text: str) -> List[str]:
    """
    Extract vendor dependency statements from text using keyword matching.
    
    This helper function identifies sentences or phrases that describe vendor
    lock-in, dependencies, or constraints related to third-party vendors or
    platforms. It looks for combinations of vendor-related keywords and
    dependency indicators.
    
    Detection Approach:
    1. Split text into sentences
    2. For each sentence, check if it contains:
       - A vendor keyword (vendor, provider, platform, etc.)
       - A dependency indicator (lock-in, dependent, tied to, etc.) OR
       - A constraint indicator (cannot migrate, difficult to switch, etc.)
    3. Extract and return matching sentences as vendor dependency statements
    
    Args:
        text: Text to search for vendor dependency statements
    
    Returns:
        List of strings, each representing a vendor dependency statement
        Example: ["Dependent on single cloud provider", "Vendor lock-in with proprietary database"]
    """
    statements = []
    
    # Vendor-related keywords
    vendor_keywords = [
        'vendor', 'provider', 'platform', 'supplier', 'third party',
        'third-party', 'service provider', 'cloud provider', 'hosting provider'
    ]
    
    # Dependency/constraint indicators
    dependency_indicators = [
        'lock-in', 'locked in', 'locked into', 'dependent on', 'dependency',
        'tied to', 'reliant on', 'relies on', 'single vendor', 'single provider',
        'proprietary', 'cannot migrate', 'difficult to migrate', 'migration difficult',
        'switching costs', 'cannot switch', 'difficult to switch', 'hard to switch',
        'single point of failure', 'critical dependency', 'heavily dependent'
    ]
    
    # Split text into sentences
    sentences = re.split(r'[.!?]+', text)
    
    for sentence in sentences:
        sentence_lower = sentence.lower().strip()
        
        # Skip very short sentences
        if len(sentence_lower) < 15:
            continue
        
        # Check if sentence contains vendor keyword
        has_vendor_keyword = any(keyword in sentence_lower for keyword in vendor_keywords)
        
        # Check if sentence has dependency indicator
        has_dependency_indicator = any(indicator in sentence_lower for indicator in dependency_indicators)
        
        # If both are present, it's likely a vendor dependency statement
        if has_vendor_keyword and has_dependency_indicator:
            statement = sentence.strip()
            if statement:
                statements.append(statement)
        
        # Also catch sentences with strong dependency indicators even without explicit vendor mention
        # (e.g., "locked into proprietary database")
        elif any(strong_indicator in sentence_lower 
                for strong_indicator in ['lock-in', 'locked in', 'locked into', 
                                        'proprietary', 'single point of failure']):
            statement = sentence.strip()
            if statement and len(statement) > 20:
                statements.append(statement)
    
    return statements


def _detect_scalability_vendor_contradiction(scalability_claim: str, vendor_statement: str) -> tuple[bool, str, str]:
    """
    Detect if a scalability claim contradicts a vendor dependency statement.
    
    This helper function analyzes a scalability claim and a vendor dependency
    statement to determine if they contradict each other. It uses keyword-based
    heuristics to identify contradictions.
    
    Contradiction Detection Logic:
    1. High Scalability + Critical Vendor Lock-in: Claims of easy scaling contradict
       statements about being locked into a single vendor
    2. Flexibility Claims + Proprietary Dependencies: Claims of flexibility contradict
       statements about proprietary or hard-to-migrate systems
    3. Cloud-Native + Single Provider: Claims of cloud-native architecture contradict
       statements about single cloud provider dependency
    4. Distributed System + Single Point of Failure: Claims of distributed architecture
       contradict statements about single points of failure
    
    Args:
        scalability_claim: A statement claiming scalability/flexibility
        vendor_statement: A statement describing vendor dependencies/lock-in
    
    Returns:
        Tuple of (contradiction_detected: bool, contradiction_type: str, severity: str)
        - contradiction_detected: True if a contradiction is detected
        - contradiction_type: Description of the type of contradiction
        - severity: "High", "Medium", or "Low" based on contradiction severity
    """
    claim_lower = scalability_claim.lower()
    vendor_lower = vendor_statement.lower()
    
    # Define strong scalability indicators
    strong_scalability = [
        'highly scalable', 'easily scale', 'seamlessly scale', 'unlimited',
        'infinite', 'cloud-native', 'distributed', 'elastic', 'flexible'
    ]
    
    # Define strong vendor lock-in indicators
    strong_lockin = [
        'vendor lock-in', 'locked in', 'locked into', 'cannot migrate',
        'difficult to migrate', 'single vendor', 'single provider',
        'proprietary', 'single point of failure', 'critical dependency'
    ]
    
    # Check for strong indicators in both statements
    has_strong_scalability = any(term in claim_lower for term in strong_scalability)
    has_strong_lockin = any(term in vendor_lower for term in strong_lockin)
    
    # Contradiction Type 1: Strong scalability claim + Strong vendor lock-in
    if has_strong_scalability and has_strong_lockin:
        # Determine severity based on specific terms
        if 'cannot migrate' in vendor_lower or 'single point of failure' in vendor_lower:
            return (True, "Scalability claims contradict critical vendor lock-in", "High")
        elif 'proprietary' in vendor_lower or 'locked in' in vendor_lower:
            return (True, "Scalability claims contradict vendor dependencies", "High")
        else:
            return (True, "Scalability claims contradict vendor constraints", "Medium")
    
    # Contradiction Type 2: Flexibility/cloud-native + Single provider dependency
    if ('flexible' in claim_lower or 'cloud-native' in claim_lower) and \
       ('single provider' in vendor_lower or 'single vendor' in vendor_lower):
        return (True, "Flexibility claims contradict single vendor dependency", "High")
    
    # Contradiction Type 3: Distributed/elastic + Single point of failure
    if ('distributed' in claim_lower or 'elastic' in claim_lower) and \
       'single point of failure' in vendor_lower:
        return (True, "Distributed architecture claims contradict single point of failure", "High")
    
    # Contradiction Type 4: Easy scaling + Migration difficulties
    if ('easily scale' in claim_lower or 'seamlessly scale' in claim_lower) and \
       ('difficult to migrate' in vendor_lower or 'switching costs' in vendor_lower):
        return (True, "Easy scaling claims contradict migration difficulties", "Medium")
    
    # Contradiction Type 5: General scalability + Vendor dependency (weaker signal)
    if ('scalable' in claim_lower or 'scale' in claim_lower) and \
       ('dependent on' in vendor_lower or 'reliant on' in vendor_lower):
        # This is a weaker contradiction - only flag if both are present
        return (True, "Scalability claims may conflict with vendor dependencies", "Low")
    
    # No clear contradiction detected
    return (False, "", "Low")



def run_all_checks(findings: List, vector_store: VectorStore) -> List[Inconsistency]:
    """
    Execute all cross-document consistency checks and aggregate results.
    
    This orchestration function runs all available heuristic-based cross-document
    checks to detect inconsistencies across multiple business documents. It provides
    a single entry point for executing all consistency validation logic and handles
    errors gracefully to ensure partial results are still returned if some checks fail.
    
    The function executes three types of checks:
    1. Revenue Consistency Check: Detects mismatches in revenue figures across documents
    2. IP Ownership Conflict Check: Detects conflicting IP ownership claims
    3. Scalability-Vendor Contradiction Check: Detects contradictions between scalability
       claims and vendor lock-in statements
    
    Error Handling Strategy:
    - Each check is executed independently in a try-except block
    - If a check fails, the error is logged but execution continues
    - Partial results from successful checks are still returned
    - This ensures that one failing check doesn't prevent other checks from running
    - Missing data is handled gracefully by individual check functions (they return empty lists)
    
    Design Rationale:
    - Centralized orchestration makes it easy to add new checks in the future
    - Independent execution prevents cascading failures
    - Graceful degradation ensures users get maximum value even with partial data
    - Logging provides visibility into which checks succeeded/failed for debugging
    
    Args:
        findings: List of RiskFinding objects from all agents (Financial, Legal, Operational)
                 These findings provide context and evidence for cross-document checks
        vector_store: FAISS VectorStore containing all ingested document chunks
                     Used by checks to query for additional information across documents
    
    Returns:
        List of Inconsistency objects from all executed checks
        Returns empty list if no inconsistencies found or all checks fail
        Returns partial results if some checks succeed and others fail
        
    Example Usage:
        # After running all risk agents
        all_findings = financial_findings + legal_findings + operational_findings
        
        # Run all cross-document checks
        inconsistencies = run_all_checks(all_findings, vector_store)
        
        # Process results
        if inconsistencies:
            print(f"Found {len(inconsistencies)} inconsistencies")
            for inc in inconsistencies:
                print(f"- {inc.issue_description} ({inc.severity})")
        else:
            print("No cross-document inconsistencies detected")
    
    Requirements Validation:
    - Requirement 6.1: Executes revenue consistency check
    - Requirement 6.2: Executes IP ownership conflict check
    - Requirement 6.3: Executes scalability-vendor contradiction check
    - Handles missing data gracefully (returns empty list if insufficient data)
    - Returns aggregated list of all detected inconsistencies
    """
    all_inconsistencies = []
    
    # Check 1: Revenue Consistency
    # Detects mismatches in revenue figures across documents
    try:
        print("Running revenue consistency check...")
        revenue_inconsistencies = check_revenue_consistency(findings, vector_store)
        all_inconsistencies.extend(revenue_inconsistencies)
        print(f"  Found {len(revenue_inconsistencies)} revenue inconsistencies")
    except Exception as e:
        # Log error but continue with other checks
        print(f"Warning: Revenue consistency check failed: {e}")
        print("  Continuing with remaining checks...")
    
    # Check 2: IP Ownership Conflicts
    # Detects conflicting IP ownership claims across documents
    try:
        print("Running IP ownership conflict check...")
        ip_inconsistencies = check_ip_ownership_conflicts(findings, vector_store)
        all_inconsistencies.extend(ip_inconsistencies)
        print(f"  Found {len(ip_inconsistencies)} IP ownership conflicts")
    except Exception as e:
        # Log error but continue with other checks
        print(f"Warning: IP ownership conflict check failed: {e}")
        print("  Continuing with remaining checks...")
    
    # Check 3: Scalability-Vendor Contradictions
    # Detects contradictions between scalability claims and vendor dependencies
    try:
        print("Running scalability-vendor contradiction check...")
        scalability_inconsistencies = check_scalability_vendor_conflicts(findings, vector_store)
        all_inconsistencies.extend(scalability_inconsistencies)
        print(f"  Found {len(scalability_inconsistencies)} scalability-vendor contradictions")
    except Exception as e:
        # Log error but continue (though this is the last check)
        print(f"Warning: Scalability-vendor contradiction check failed: {e}")
    
    # Summary
    print(f"\nCross-document checks complete: {len(all_inconsistencies)} total inconsistencies detected")
    
    return all_inconsistencies
