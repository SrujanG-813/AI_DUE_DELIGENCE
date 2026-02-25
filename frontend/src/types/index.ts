export interface RiskFinding {
  risk_description: string
  severity: 'High' | 'Medium' | 'Low'
  evidence: string
  source_document: string
  source_location: string
  agent_type: 'Financial' | 'Legal' | 'Operational'
}

export interface Inconsistency {
  issue_description: string
  documents_involved: string[]
  severity: 'High' | 'Medium' | 'Low'
  details: string
}

export interface AnalysisResults {
  documents_loaded: number
  chunks_created: number
  financial_findings: RiskFinding[]
  legal_findings: RiskFinding[]
  operational_findings: RiskFinding[]
  inconsistencies: Inconsistency[]
  risk_score: number
  risk_classification: 'Low Risk' | 'Medium Risk' | 'High Risk'
  memo: string
}

export interface ProgressUpdate {
  progress: number
  message: string
}
