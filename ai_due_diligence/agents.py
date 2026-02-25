"""
Risk Analysis Agents Module

This module provides the base RiskAgent class and specialized risk analysis agents
for the AI Due Diligence Engine. Each agent analyzes a specific risk category
(Financial, Legal, or Operational) by querying the vector store and using an LLM
to identify potential risks with supporting evidence.

Architecture:
- RiskAgent: Abstract base class defining the agent interface
- RiskFinding: Data structure for risk analysis results
- Specialized agents (FinancialRiskAgent, LegalRiskAgent, OperationalRiskAgent)
  inherit from RiskAgent and implement category-specific analysis logic
"""

from dataclasses import dataclass
from typing import List, Any
from abc import ABC, abstractmethod


@dataclass
class RiskFinding:
    """
    Represents a single risk identified during due diligence analysis.
    
    This data structure captures all essential information about a risk,
    including its description, severity level, supporting evidence, and
    source citation for traceability.
    
    Attributes:
        risk_description: Clear description of the identified risk
        severity: Risk severity level - must be "Low", "Medium", or "High"
        evidence: Supporting evidence text extracted from documents
        source_document: Name of the source document containing the evidence
        source_location: Specific location in document (page number or section)
        agent_type: Type of agent that identified this risk
                   ("Financial", "Legal", or "Operational")
    
    Example:
        finding = RiskFinding(
            risk_description="Revenue projections lack supporting data",
            severity="High",
            evidence="Q4 revenue target of $5M mentioned without methodology",
            source_document="financial_summary.pdf",
            source_location="Page 3",
            agent_type="Financial"
        )
    """
    risk_description: str
    severity: str  # "Low" | "Medium" | "High"
    evidence: str
    source_document: str
    source_location: str
    agent_type: str  # "Financial" | "Legal" | "Operational"


class RiskAgent(ABC):
    """
    Abstract base class for risk analysis agents.
    
    This class defines the interface that all specialized risk agents must implement.
    Each agent is responsible for analyzing documents in a specific risk category
    by querying the vector store for relevant information and using an LLM to
    identify and assess risks.
    
    The agent workflow:
    1. Execute queries against the vector store to retrieve relevant document chunks
    2. Pass retrieved chunks to the LLM with category-specific analysis prompts
    3. Parse LLM responses into structured RiskFinding objects
    4. Return findings with evidence citations for traceability
    
    Attributes:
        agent_type: The risk category this agent analyzes
                   ("Financial", "Legal", or "Operational")
        llm: Language model instance for risk analysis
        vector_store: FAISS vector store containing document embeddings
    
    Usage:
        Subclasses must implement the analyze() method to provide
        category-specific risk analysis logic.
    """
    
    def __init__(self, agent_type: str, llm: Any, vector_store: Any):
        """
        Initialize a risk analysis agent.
        
        Args:
            agent_type: The risk category this agent analyzes
                       ("Financial", "Legal", or "Operational")
            llm: Language model instance (e.g., OpenAI GPT-4) for analyzing
                 retrieved document chunks and identifying risks
            vector_store: FAISS vector store containing embedded document chunks
                         with metadata for retrieval and citation
        
        Example:
            from langchain.llms import OpenAI
            
            llm = OpenAI(model="gpt-4", temperature=0)
            agent = FinancialRiskAgent(
                agent_type="Financial",
                llm=llm,
                vector_store=vector_store
            )
        """
        self.agent_type = agent_type
        self.llm = llm
        self.vector_store = vector_store
    
    @abstractmethod
    def analyze(self) -> List[RiskFinding]:
        """
        Analyze documents for risks in this agent's category.
        
        This method must be implemented by subclasses to provide category-specific
        risk analysis logic. The implementation should:
        
        1. Define query templates relevant to the risk category
        2. Retrieve relevant document chunks from the vector store
        3. Format chunks with citations for LLM analysis
        4. Construct category-specific prompts for the LLM
        5. Parse LLM responses into RiskFinding objects
        6. Handle errors gracefully (empty results, malformed responses, etc.)
        
        Returns:
            List of RiskFinding objects, each representing an identified risk
            with supporting evidence and source citations. Returns empty list
            if no risks are identified or if analysis fails.
        
        Raises:
            NotImplementedError: If called on the base class directly
        
        Example implementation pattern:
            def analyze(self) -> List[RiskFinding]:
                findings = []
                
                # Define queries for this risk category
                queries = [
                    "revenue and growth projections",
                    "cost structure and burn rate"
                ]
                
                # Retrieve and analyze for each query
                for query in queries:
                    chunks = retrieve_relevant_chunks(self.vector_store, query)
                    llm_response = self.llm.analyze(chunks)
                    findings.extend(parse_findings(llm_response))
                
                return findings
        """
        pass


class FinancialRiskAgent(RiskAgent):
    """
    Specialized agent for analyzing financial risks in due diligence documents.

    This agent focuses on identifying risks related to:
    - Revenue claims and projections (overly optimistic, unsupported)
    - Growth rates and sustainability concerns
    - Cost structures and burn rate issues
    - Missing or incomplete financial data
    - Financial assumptions and their validity

    The agent queries the vector store for financial information and uses an LLM
    to assess the credibility, completeness, and risk level of financial claims.

    Financial Risk Focus Areas:
    1. Revenue Analysis:
       - Are revenue figures supported by data?
       - Are projections realistic or overly optimistic?
       - Are there red flags in revenue recognition?

    2. Growth Analysis:
       - Are growth rates sustainable?
       - What assumptions underlie growth projections?
       - Are there market or competitive risks to growth?

    3. Cost Structure:
       - Are costs well-documented?
       - Is burn rate sustainable?
       - Are there hidden or underestimated costs?

    4. Data Completeness:
       - Are key financial metrics missing?
       - Is there sufficient detail for due diligence?
       - Are there gaps in financial reporting?

    Requirements Validation:
    - Requirement 3.1: Retrieves chunks related to revenue, growth, and costs
    - Requirement 3.2: Identifies overly optimistic language
    - Requirement 3.3: Flags missing critical financial information
    - Requirement 3.4: Provides evidence references for each risk
    - Requirement 3.5: Assigns severity levels (Low/Medium/High)
    """

    def __init__(self, llm: Any, vector_store: Any):
        """
        Initialize the Financial Risk Agent.

        Args:
            llm: Language model instance for financial risk analysis
            vector_store: FAISS vector store containing document embeddings
        """
        super().__init__(agent_type="Financial", llm=llm, vector_store=vector_store)

    def analyze(self) -> List[RiskFinding]:
        """
        Analyze documents for financial risks.

        This method executes multiple queries to retrieve financial information,
        then uses the LLM to identify risks, assess severity, and provide
        evidence-backed findings.

        Workflow:
        1. Define query templates for different financial focus areas
        2. For each query, retrieve relevant document chunks
        3. Format chunks with citations for LLM analysis
        4. Construct a financial risk analysis prompt
        5. Call LLM to analyze the retrieved information
        6. Parse LLM JSON response into RiskFinding objects
        7. Handle parsing errors gracefully
        8. Return all identified financial risks

        Returns:
            List of RiskFinding objects representing identified financial risks.
            Returns empty list if no risks found or if analysis fails.

        Example:
            agent = FinancialRiskAgent(llm, vector_store)
            findings = agent.analyze()
            for finding in findings:
                print(f"{finding.severity}: {finding.risk_description}")
        """
        import json
        import logging
        from ai_due_diligence.retriever import retrieve_relevant_chunks, format_chunks_with_citations

        logger = logging.getLogger(__name__)
        logger.info("Starting financial risk analysis...")

        # Define query templates for financial risk focus areas
        # Each query targets a specific aspect of financial due diligence
        # Requirements 3.1: Retrieve chunks related to revenue, growth, and costs
        query_templates = [
            "revenue projections and revenue growth",
            "financial performance and growth rate",
            "cost structure and operating expenses and burn rate",
            "financial data and financial metrics and financial statements"
        ]

        # Collect all retrieved chunks across queries
        all_chunks = []

        # Execute each query and collect results
        for query in query_templates:
            try:
                logger.debug(f"Executing financial query: '{query}'")

                # Retrieve top 5 most relevant chunks for this query
                # k=5 provides good coverage without overwhelming the LLM
                chunks = retrieve_relevant_chunks(
                    vector_store=self.vector_store,
                    query=query,
                    k=5
                )

                if chunks:
                    all_chunks.extend(chunks)
                    logger.debug(f"Retrieved {len(chunks)} chunks for query: '{query}'")
                else:
                    logger.warning(f"No chunks retrieved for query: '{query}'")

            except Exception as e:
                logger.error(f"Failed to retrieve chunks for query '{query}': {str(e)}")
                # Continue with other queries even if one fails
                continue

        # If no chunks were retrieved at all, return empty findings
        if not all_chunks:
            logger.warning("No financial information retrieved from documents")
            return []

        # Remove duplicate chunks (same content retrieved by multiple queries)
        # Use chunk_id from metadata to identify duplicates
        unique_chunks = []
        seen_chunk_ids = set()

        for doc, score in all_chunks:
            chunk_id = doc.metadata.get('chunk_id', id(doc))
            if chunk_id not in seen_chunk_ids:
                unique_chunks.append((doc, score))
                seen_chunk_ids.add(chunk_id)

        logger.info(f"Retrieved {len(unique_chunks)} unique chunks for financial analysis")

        # Format chunks with citations for LLM analysis
        # Requirement 3.4: Provide evidence references
        formatted_chunks = format_chunks_with_citations(unique_chunks)

        # Construct the LLM prompt for financial risk analysis
        # The prompt instructs the LLM to:
        # - Identify financial risks (Requirements 3.2, 3.3)
        # - Assign severity levels (Requirement 3.5)
        # - Provide evidence and citations (Requirement 3.4)
        prompt = f"""You are a financial risk analyst conducting investment due diligence.

Analyze the following document excerpts and identify potential FINANCIAL risks related to:
- Revenue claims and projections (overly optimistic, unsupported, unrealistic)
- Growth rates and sustainability
- Cost structures and burn rate
- Missing or incomplete financial data
- Questionable financial assumptions

Document Excerpts:
{formatted_chunks}

For each financial risk you identify:
1. Describe the risk clearly and specifically
2. Explain why it's concerning from an investment perspective
3. Assign a severity level: "High", "Medium", or "Low"
   - High: Critical issue that could significantly impact investment decision
   - Medium: Notable concern that requires further investigation
   - Low: Minor issue or area for clarification
4. Quote the specific evidence from the documents
5. Reference the source document and page/location

Output your findings in valid JSON format as an array of objects:
[
  {{
    "risk_description": "Clear description of the financial risk",
    "severity": "High",
    "evidence": "Direct quote or paraphrase from the document",
    "source_document": "filename.pdf",
    "source_location": "Page 3"
  }}
]

If you find no significant financial risks, return an empty array: []

IMPORTANT: Return ONLY valid JSON. Do not include any explanatory text before or after the JSON."""

        # Call the LLM to analyze the financial information
        try:
            logger.debug("Calling LLM for financial risk analysis...")

            # Invoke the LLM with the constructed prompt
            # The LLM should return a JSON array of risk findings
            llm_response = self.llm.invoke(prompt)

            # Extract the text content from the LLM response
            # Handle different response formats (string vs object with content attribute)
            if hasattr(llm_response, 'content'):
                response_text = llm_response.content
            else:
                response_text = str(llm_response)

            logger.debug(f"LLM response received ({len(response_text)} characters)")

        except Exception as e:
            logger.error(f"LLM invocation failed: {str(e)}")
            return []

        # Parse the LLM response into RiskFinding objects
        # Handle parsing errors gracefully (Requirement: Handle parsing errors gracefully)
        findings = []

        try:
            # Clean the response text to extract JSON
            # Remove markdown code blocks if present
            response_text = response_text.strip()
            if response_text.startswith("```json"):
                response_text = response_text[7:]  # Remove ```json
            if response_text.startswith("```"):
                response_text = response_text[3:]  # Remove ```
            if response_text.endswith("```"):
                response_text = response_text[:-3]  # Remove trailing ```
            response_text = response_text.strip()

            # Parse JSON response
            parsed_response = json.loads(response_text)

            # Validate that response is a list
            if not isinstance(parsed_response, list):
                logger.error(f"LLM response is not a list: {type(parsed_response)}")
                return []

            logger.info(f"Parsed {len(parsed_response)} financial risk findings from LLM")

            # Convert each parsed finding into a RiskFinding object
            for idx, finding_dict in enumerate(parsed_response):
                try:
                    # Validate required fields
                    required_fields = [
                        'risk_description', 'severity', 'evidence',
                        'source_document', 'source_location'
                    ]

                    missing_fields = [
                        field for field in required_fields
                        if field not in finding_dict
                    ]

                    if missing_fields:
                        logger.warning(
                            f"Finding {idx+1} missing fields: {missing_fields}. Skipping."
                        )
                        continue

                    # Validate severity level
                    severity = finding_dict['severity']
                    if severity not in ['Low', 'Medium', 'High']:
                        logger.warning(
                            f"Invalid severity '{severity}' in finding {idx+1}. "
                            f"Defaulting to 'Medium'."
                        )
                        severity = 'Medium'

                    # Create RiskFinding object
                    # Requirement 3.5: Assign severity levels
                    finding = RiskFinding(
                        risk_description=finding_dict['risk_description'],
                        severity=severity,
                        evidence=finding_dict['evidence'],
                        source_document=finding_dict['source_document'],
                        source_location=finding_dict['source_location'],
                        agent_type=self.agent_type
                    )

                    findings.append(finding)
                    logger.debug(
                        f"Created finding: {severity} - "
                        f"{finding_dict['risk_description'][:50]}..."
                    )

                except Exception as e:
                    logger.error(
                        f"Failed to create RiskFinding from dict {idx+1}: {str(e)}"
                    )
                    # Continue processing other findings
                    continue

            logger.info(
                f"Financial risk analysis complete. "
                f"Identified {len(findings)} financial risks."
            )

        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse LLM response as JSON: {str(e)}")
            logger.debug(f"Raw LLM response: {response_text[:500]}...")
            # Return empty list on parsing failure
            return []

        except Exception as e:
            logger.error(f"Unexpected error during response parsing: {str(e)}")
            return []

        return findings




class LegalRiskAgent(RiskAgent):
    """
    Specialized agent for analyzing legal and contract risks in due diligence documents.

    This agent focuses on identifying risks related to:
    - Contract termination clauses (one-sided, unfavorable terms)
    - Liability and indemnification terms (inadequate limits, broad obligations)
    - Intellectual property ownership (unclear rights, conflicts)
    - Unusual or problematic contractual obligations
    - Legal compliance and regulatory risks

    The agent queries the vector store for legal and contract information and uses
    an LLM to assess the fairness, completeness, and risk level of legal terms.

    Legal Risk Focus Areas:
    1. Contract Termination:
       - Are termination clauses one-sided or unfavorable?
       - Are there early termination penalties?
       - Can the company exit contracts reasonably?

    2. Liability and Indemnification:
       - Are liability limits adequate?
       - Are indemnification obligations reasonable?
       - Are there uncapped liability exposures?

    3. Intellectual Property:
       - Is IP ownership clearly defined?
       - Are there IP assignment or licensing issues?
       - Are there potential IP conflicts?

    4. Contractual Obligations:
       - Are there unusual or burdensome obligations?
       - Are contract terms balanced or one-sided?
       - Are there hidden legal risks?

    Requirements Validation:
    - Requirement 4.1: Retrieves chunks related to contracts, termination, liability, IP
    - Requirement 4.2: Identifies one-sided or unusual clauses
    - Requirement 4.3: Flags inadequate liability limits
    - Requirement 4.4: Provides evidence references for each risk
    - Requirement 4.5: Assigns severity levels (Low/Medium/High)
    """

    def __init__(self, llm: Any, vector_store: Any):
        """
        Initialize the Legal Risk Agent.

        Args:
            llm: Language model instance for legal risk analysis
            vector_store: FAISS vector store containing document embeddings
        """
        super().__init__(agent_type="Legal", llm=llm, vector_store=vector_store)

    def analyze(self) -> List[RiskFinding]:
        """
        Analyze documents for legal and contract risks.

        This method executes multiple queries to retrieve legal information,
        then uses the LLM to identify risks, assess severity, and provide
        evidence-backed findings.

        Workflow:
        1. Define query templates for different legal focus areas
        2. For each query, retrieve relevant document chunks
        3. Format chunks with citations for LLM analysis
        4. Construct a legal risk analysis prompt
        5. Call LLM to analyze the retrieved information
        6. Parse LLM JSON response into RiskFinding objects
        7. Handle parsing errors gracefully
        8. Return all identified legal risks

        Returns:
            List of RiskFinding objects representing identified legal risks.
            Returns empty list if no risks found or if analysis fails.

        Example:
            agent = LegalRiskAgent(llm, vector_store)
            findings = agent.analyze()
            for finding in findings:
                print(f"{finding.severity}: {finding.risk_description}")
        """
        import json
        import logging
        from ai_due_diligence.retriever import retrieve_relevant_chunks, format_chunks_with_citations

        logger = logging.getLogger(__name__)
        logger.info("Starting legal risk analysis...")

        # Define query templates for legal risk focus areas
        # Each query targets a specific aspect of legal due diligence
        # Requirements 4.1: Retrieve chunks related to contracts, termination, liability, IP
        query_templates = [
            "contract terms and termination clauses and cancellation",
            "liability and indemnification and insurance",
            "intellectual property and IP ownership and IP rights",
            "legal obligations and contractual commitments"
        ]

        # Collect all retrieved chunks across queries
        all_chunks = []

        # Execute each query and collect results
        for query in query_templates:
            try:
                logger.debug(f"Executing legal query: '{query}'")

                # Retrieve top 5 most relevant chunks for this query
                # k=5 provides good coverage without overwhelming the LLM
                chunks = retrieve_relevant_chunks(
                    vector_store=self.vector_store,
                    query=query,
                    k=5
                )

                if chunks:
                    all_chunks.extend(chunks)
                    logger.debug(f"Retrieved {len(chunks)} chunks for query: '{query}'")
                else:
                    logger.warning(f"No chunks retrieved for query: '{query}'")

            except Exception as e:
                logger.error(f"Failed to retrieve chunks for query '{query}': {str(e)}")
                # Continue with other queries even if one fails
                continue

        # If no chunks were retrieved at all, return empty findings
        if not all_chunks:
            logger.warning("No legal information retrieved from documents")
            return []

        # Remove duplicate chunks (same content retrieved by multiple queries)
        # Use chunk_id from metadata to identify duplicates
        unique_chunks = []
        seen_chunk_ids = set()

        for doc, score in all_chunks:
            chunk_id = doc.metadata.get('chunk_id', id(doc))
            if chunk_id not in seen_chunk_ids:
                unique_chunks.append((doc, score))
                seen_chunk_ids.add(chunk_id)

        logger.info(f"Retrieved {len(unique_chunks)} unique chunks for legal analysis")

        # Format chunks with citations for LLM analysis
        # Requirement 4.4: Provide evidence references
        formatted_chunks = format_chunks_with_citations(unique_chunks)

        # Construct the LLM prompt for legal risk analysis
        # The prompt instructs the LLM to:
        # - Identify legal risks (Requirements 4.2, 4.3)
        # - Assign severity levels (Requirement 4.5)
        # - Provide evidence and citations (Requirement 4.4)
        prompt = f"""You are a legal risk analyst conducting investment due diligence.

Analyze the following document excerpts and identify potential LEGAL risks related to:
- Contract termination clauses (one-sided, unfavorable, restrictive)
- Liability and indemnification terms (inadequate limits, broad obligations, uncapped exposure)
- Intellectual property ownership (unclear rights, conflicts, licensing issues)
- Unusual or problematic contractual obligations
- Legal compliance and regulatory concerns

Document Excerpts:
{formatted_chunks}

For each legal risk you identify:
1. Describe the risk clearly and specifically
2. Explain why it's concerning from a legal/investment perspective
3. Assign a severity level: "High", "Medium", or "Low"
   - High: Critical legal issue that could significantly impact investment decision
   - Medium: Notable legal concern that requires further investigation
   - Low: Minor legal issue or area for clarification
4. Quote the specific evidence from the documents
5. Reference the source document and page/location

Output your findings in valid JSON format as an array of objects:
[
  {{
    "risk_description": "Clear description of the legal risk",
    "severity": "High",
    "evidence": "Direct quote or paraphrase from the document",
    "source_document": "filename.pdf",
    "source_location": "Page 3"
  }}
]

If you find no significant legal risks, return an empty array: []

IMPORTANT: Return ONLY valid JSON. Do not include any explanatory text before or after the JSON."""

        # Call the LLM to analyze the legal information
        try:
            logger.debug("Calling LLM for legal risk analysis...")

            # Invoke the LLM with the constructed prompt
            # The LLM should return a JSON array of risk findings
            llm_response = self.llm.invoke(prompt)

            # Extract the text content from the LLM response
            # Handle different response formats (string vs object with content attribute)
            if hasattr(llm_response, 'content'):
                response_text = llm_response.content
            else:
                response_text = str(llm_response)

            logger.debug(f"LLM response received ({len(response_text)} characters)")

        except Exception as e:
            logger.error(f"LLM invocation failed: {str(e)}")
            return []

        # Parse the LLM response into RiskFinding objects
        # Handle parsing errors gracefully (Requirement: Handle parsing errors gracefully)
        findings = []

        try:
            # Clean the response text to extract JSON
            # Remove markdown code blocks if present
            response_text = response_text.strip()
            if response_text.startswith("```json"):
                response_text = response_text[7:]  # Remove ```json
            if response_text.startswith("```"):
                response_text = response_text[3:]  # Remove ```
            if response_text.endswith("```"):
                response_text = response_text[:-3]  # Remove trailing ```
            response_text = response_text.strip()

            # Parse JSON response
            parsed_response = json.loads(response_text)

            # Validate that response is a list
            if not isinstance(parsed_response, list):
                logger.error(f"LLM response is not a list: {type(parsed_response)}")
                return []

            logger.info(f"Parsed {len(parsed_response)} legal risk findings from LLM")

            # Convert each parsed finding into a RiskFinding object
            for idx, finding_dict in enumerate(parsed_response):
                try:
                    # Validate required fields
                    required_fields = [
                        'risk_description', 'severity', 'evidence',
                        'source_document', 'source_location'
                    ]

                    missing_fields = [
                        field for field in required_fields
                        if field not in finding_dict
                    ]

                    if missing_fields:
                        logger.warning(
                            f"Finding {idx+1} missing fields: {missing_fields}. Skipping."
                        )
                        continue

                    # Validate severity level
                    severity = finding_dict['severity']
                    if severity not in ['Low', 'Medium', 'High']:
                        logger.warning(
                            f"Invalid severity '{severity}' in finding {idx+1}. "
                            f"Defaulting to 'Medium'."
                        )
                        severity = 'Medium'

                    # Create RiskFinding object
                    # Requirement 4.5: Assign severity levels
                    finding = RiskFinding(
                        risk_description=finding_dict['risk_description'],
                        severity=severity,
                        evidence=finding_dict['evidence'],
                        source_document=finding_dict['source_document'],
                        source_location=finding_dict['source_location'],
                        agent_type=self.agent_type
                    )

                    findings.append(finding)
                    logger.debug(
                        f"Created finding: {severity} - "
                        f"{finding_dict['risk_description'][:50]}..."
                    )

                except Exception as e:
                    logger.error(
                        f"Failed to create RiskFinding from dict {idx+1}: {str(e)}"
                    )
                    # Continue processing other findings
                    continue

            logger.info(
                f"Legal risk analysis complete. "
                f"Identified {len(findings)} legal risks."
            )

        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse LLM response as JSON: {str(e)}")
            logger.debug(f"Raw LLM response: {response_text[:500]}...")
            # Return empty list on parsing failure
            return []

        except Exception as e:
            logger.error(f"Unexpected error during response parsing: {str(e)}")
            return []

        return findings



class OperationalRiskAgent(RiskAgent):
    """
    Specialized agent for analyzing operational risks in due diligence documents.

    This agent focuses on identifying risks related to:
    - Key personnel dependencies (single points of failure, knowledge concentration)
    - Vendor dependencies and lock-in (critical vendor reliance, switching costs)
    - Scalability concerns (infrastructure limits, growth bottlenecks)
    - Operational bottlenecks and inefficiencies
    - Business continuity and resilience issues

    The agent queries the vector store for operational information and uses
    an LLM to assess the robustness, scalability, and risk level of operational
    structures and dependencies.

    Operational Risk Focus Areas:
    1. Key Personnel:
       - Are there single points of failure in the team?
       - Is knowledge concentrated in few individuals?
       - What happens if key people leave?

    2. Vendor Dependencies:
       - Are there critical vendor dependencies?
       - Is there vendor lock-in risk?
       - Are there alternative vendors available?

    3. Scalability:
       - Can the infrastructure scale with growth?
       - Are there operational bottlenecks?
       - What are the scaling limitations?

    4. Business Continuity:
       - Are there backup systems and processes?
       - How resilient is the operation to disruptions?
       - Are there documented contingency plans?

    Requirements Validation:
    - Requirement 5.1: Retrieves chunks related to personnel, vendors, scalability
    - Requirement 5.2: Identifies single points of failure
    - Requirement 5.3: Flags vendor lock-in risks
    - Requirement 5.4: Provides evidence references for each risk
    - Requirement 5.5: Assigns severity levels (Low/Medium/High)
    """

    def __init__(self, llm: Any, vector_store: Any):
        """
        Initialize the Operational Risk Agent.

        Args:
            llm: Language model instance for operational risk analysis
            vector_store: FAISS vector store containing document embeddings
        """
        super().__init__(agent_type="Operational", llm=llm, vector_store=vector_store)

    def analyze(self) -> List[RiskFinding]:
        """
        Analyze documents for operational risks.

        This method executes multiple queries to retrieve operational information,
        then uses the LLM to identify risks, assess severity, and provide
        evidence-backed findings.

        Workflow:
        1. Define query templates for different operational focus areas
        2. For each query, retrieve relevant document chunks
        3. Format chunks with citations for LLM analysis
        4. Construct an operational risk analysis prompt
        5. Call LLM to analyze the retrieved information
        6. Parse LLM JSON response into RiskFinding objects
        7. Handle parsing errors gracefully
        8. Return all identified operational risks

        Returns:
            List of RiskFinding objects representing identified operational risks.
            Returns empty list if no risks found or if analysis fails.

        Example:
            agent = OperationalRiskAgent(llm, vector_store)
            findings = agent.analyze()
            for finding in findings:
                print(f"{finding.severity}: {finding.risk_description}")
        """
        import json
        import logging
        from ai_due_diligence.retriever import retrieve_relevant_chunks, format_chunks_with_citations

        logger = logging.getLogger(__name__)
        logger.info("Starting operational risk analysis...")

        # Define query templates for operational risk focus areas
        # Each query targets a specific aspect of operational due diligence
        # Requirements 5.1: Retrieve chunks related to personnel, vendors, scalability
        query_templates = [
            "key personnel and team members and employees and staffing",
            "vendor dependencies and third-party services and suppliers",
            "scalability and infrastructure and capacity and growth limitations",
            "operational processes and business continuity and contingency plans"
        ]

        # Collect all retrieved chunks across queries
        all_chunks = []

        # Execute each query and collect results
        for query in query_templates:
            try:
                logger.debug(f"Executing operational query: '{query}'")

                # Retrieve top 5 most relevant chunks for this query
                # k=5 provides good coverage without overwhelming the LLM
                chunks = retrieve_relevant_chunks(
                    vector_store=self.vector_store,
                    query=query,
                    k=5
                )

                if chunks:
                    all_chunks.extend(chunks)
                    logger.debug(f"Retrieved {len(chunks)} chunks for query: '{query}'")
                else:
                    logger.warning(f"No chunks retrieved for query: '{query}'")

            except Exception as e:
                logger.error(f"Failed to retrieve chunks for query '{query}': {str(e)}")
                # Continue with other queries even if one fails
                continue

        # If no chunks were retrieved at all, return empty findings
        if not all_chunks:
            logger.warning("No operational information retrieved from documents")
            return []

        # Remove duplicate chunks (same content retrieved by multiple queries)
        # Use chunk_id from metadata to identify duplicates
        unique_chunks = []
        seen_chunk_ids = set()

        for doc, score in all_chunks:
            chunk_id = doc.metadata.get('chunk_id', id(doc))
            if chunk_id not in seen_chunk_ids:
                unique_chunks.append((doc, score))
                seen_chunk_ids.add(chunk_id)

        logger.info(f"Retrieved {len(unique_chunks)} unique chunks for operational analysis")

        # Format chunks with citations for LLM analysis
        # Requirement 5.4: Provide evidence references
        formatted_chunks = format_chunks_with_citations(unique_chunks)

        # Construct the LLM prompt for operational risk analysis
        # The prompt instructs the LLM to:
        # - Identify operational risks (Requirements 5.2, 5.3)
        # - Assign severity levels (Requirement 5.5)
        # - Provide evidence and citations (Requirement 5.4)
        prompt = f"""You are an operational risk analyst conducting investment due diligence.

Analyze the following document excerpts and identify potential OPERATIONAL risks related to:
- Key personnel dependencies (single points of failure, knowledge concentration, succession risks)
- Vendor dependencies and lock-in (critical vendor reliance, switching costs, vendor concentration)
- Scalability concerns (infrastructure limits, growth bottlenecks, capacity constraints)
- Operational bottlenecks and inefficiencies
- Business continuity and resilience issues

Document Excerpts:
{formatted_chunks}

For each operational risk you identify:
1. Describe the risk clearly and specifically
2. Explain why it's concerning from an operational/investment perspective
3. Assign a severity level: "High", "Medium", or "Low"
   - High: Critical operational issue that could significantly impact business continuity or growth
   - Medium: Notable operational concern that requires further investigation
   - Low: Minor operational issue or area for improvement
4. Quote the specific evidence from the documents
5. Reference the source document and page/location

Output your findings in valid JSON format as an array of objects:
[
  {{
    "risk_description": "Clear description of the operational risk",
    "severity": "High",
    "evidence": "Direct quote or paraphrase from the document",
    "source_document": "filename.pdf",
    "source_location": "Page 3"
  }}
]

If you find no significant operational risks, return an empty array: []

IMPORTANT: Return ONLY valid JSON. Do not include any explanatory text before or after the JSON."""

        # Call the LLM to analyze the operational information
        try:
            logger.debug("Calling LLM for operational risk analysis...")

            # Invoke the LLM with the constructed prompt
            # The LLM should return a JSON array of risk findings
            llm_response = self.llm.invoke(prompt)

            # Extract the text content from the LLM response
            # Handle different response formats (string vs object with content attribute)
            if hasattr(llm_response, 'content'):
                response_text = llm_response.content
            else:
                response_text = str(llm_response)

            logger.debug(f"LLM response received ({len(response_text)} characters)")

        except Exception as e:
            logger.error(f"LLM invocation failed: {str(e)}")
            return []

        # Parse the LLM response into RiskFinding objects
        # Handle parsing errors gracefully (Requirement: Handle parsing errors gracefully)
        findings = []

        try:
            # Clean the response text to extract JSON
            # Remove markdown code blocks if present
            response_text = response_text.strip()
            if response_text.startswith("```json"):
                response_text = response_text[7:]  # Remove ```json
            if response_text.startswith("```"):
                response_text = response_text[3:]  # Remove ```
            if response_text.endswith("```"):
                response_text = response_text[:-3]  # Remove trailing ```
            response_text = response_text.strip()

            # Parse JSON response
            parsed_response = json.loads(response_text)

            # Validate that response is a list
            if not isinstance(parsed_response, list):
                logger.error(f"LLM response is not a list: {type(parsed_response)}")
                return []

            logger.info(f"Parsed {len(parsed_response)} operational risk findings from LLM")

            # Convert each parsed finding into a RiskFinding object
            for idx, finding_dict in enumerate(parsed_response):
                try:
                    # Validate required fields
                    required_fields = [
                        'risk_description', 'severity', 'evidence',
                        'source_document', 'source_location'
                    ]

                    missing_fields = [
                        field for field in required_fields
                        if field not in finding_dict
                    ]

                    if missing_fields:
                        logger.warning(
                            f"Finding {idx+1} missing fields: {missing_fields}. Skipping."
                        )
                        continue

                    # Validate severity level
                    severity = finding_dict['severity']
                    if severity not in ['Low', 'Medium', 'High']:
                        logger.warning(
                            f"Invalid severity '{severity}' in finding {idx+1}. "
                            f"Defaulting to 'Medium'."
                        )
                        severity = 'Medium'

                    # Create RiskFinding object
                    # Requirement 5.5: Assign severity levels
                    finding = RiskFinding(
                        risk_description=finding_dict['risk_description'],
                        severity=severity,
                        evidence=finding_dict['evidence'],
                        source_document=finding_dict['source_document'],
                        source_location=finding_dict['source_location'],
                        agent_type=self.agent_type
                    )

                    findings.append(finding)
                    logger.debug(
                        f"Created finding: {severity} - "
                        f"{finding_dict['risk_description'][:50]}..."
                    )

                except Exception as e:
                    logger.error(
                        f"Failed to create RiskFinding from dict {idx+1}: {str(e)}"
                    )
                    # Continue processing other findings
                    continue

            logger.info(
                f"Operational risk analysis complete. "
                f"Identified {len(findings)} operational risks."
            )

        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse LLM response as JSON: {str(e)}")
            logger.debug(f"Raw LLM response: {response_text[:500]}...")
            # Return empty list on parsing failure
            return []

        except Exception as e:
            logger.error(f"Unexpected error during response parsing: {str(e)}")
            return []

        return findings
