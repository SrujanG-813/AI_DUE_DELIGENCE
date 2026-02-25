import { useState } from 'react'
import { AnalysisResults } from '../types'
import { Download, RefreshCw, TrendingUp, AlertTriangle, CheckCircle, FileText } from 'lucide-react'
import RiskChart from './RiskChart'
import FindingsCard from './FindingsCard'
import InconsistenciesCard from './InconsistenciesCard'
import RiskMemoViewer from './RiskMemoViewer'

interface ResultsDashboardProps {
  results: AnalysisResults
  onReset: () => void
}

export default function ResultsDashboard({ results, onReset }: ResultsDashboardProps) {
  const [activeTab, setActiveTab] = useState<'overview' | 'financial' | 'legal' | 'operational' | 'inconsistencies' | 'memo'>('overview')

  const getRiskColor = (classification: string) => {
    if (classification === 'High Risk') return 'from-red-500 to-red-600'
    if (classification === 'Medium Risk') return 'from-yellow-500 to-orange-500'
    return 'from-green-500 to-green-600'
  }

  const getRiskIcon = (classification: string) => {
    if (classification === 'High Risk') return <AlertTriangle className="w-8 h-8" />
    if (classification === 'Medium Risk') return <TrendingUp className="w-8 h-8" />
    return <CheckCircle className="w-8 h-8" />
  }

  const totalFindings = 
    results.financial_findings.length +
    results.legal_findings.length +
    results.operational_findings.length

  const downloadReport = () => {
    const blob = new Blob([results.memo], { type: 'text/markdown' })
    const url = URL.createObjectURL(blob)
    const a = document.createElement('a')
    a.href = url
    a.download = `risk-memo-${new Date().toISOString().split('T')[0]}.md`
    document.body.appendChild(a)
    a.click()
    document.body.removeChild(a)
    URL.revokeObjectURL(url)
  }

  return (
    <div className="animate-fade-in">
      {/* Header Actions */}
      <div className="flex justify-between items-center mb-8">
        <h2 className="text-3xl font-bold gradient-text">Analysis Results</h2>
        <div className="flex space-x-3">
          <button
            onClick={downloadReport}
            className="btn-secondary flex items-center space-x-2"
          >
            <Download className="w-5 h-5" />
            <span>Download Report</span>
          </button>
          <button
            onClick={onReset}
            className="btn-primary flex items-center space-x-2"
          >
            <RefreshCw className="w-5 h-5" />
            <span>New Analysis</span>
          </button>
        </div>
      </div>

      {/* Risk Score Card */}
      <div className={`glass-effect rounded-2xl p-8 mb-8 bg-gradient-to-r ${getRiskColor(results.risk_classification)} text-white shadow-2xl`}>
        <div className="flex items-center justify-between">
          <div>
            <p className="text-white/80 text-sm font-medium mb-2">Overall Risk Assessment</p>
            <h3 className="text-4xl font-bold mb-2">{results.risk_classification}</h3>
            <p className="text-white/90">Risk Score: {results.risk_score} points</p>
          </div>
          <div className="w-20 h-20 bg-white/20 rounded-2xl flex items-center justify-center backdrop-blur-sm">
            {getRiskIcon(results.risk_classification)}
          </div>
        </div>
      </div>

      {/* Stats Grid */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-6 mb-8">
        <div className="glass-effect rounded-xl p-6 card-hover">
          <div className="flex items-center justify-between mb-2">
            <p className="text-gray-600 text-sm font-medium">Documents</p>
            <FileText className="w-5 h-5 text-blue-500" />
          </div>
          <p className="text-3xl font-bold text-gray-800">{results.documents_loaded}</p>
        </div>

        <div className="glass-effect rounded-xl p-6 card-hover">
          <div className="flex items-center justify-between mb-2">
            <p className="text-gray-600 text-sm font-medium">Total Findings</p>
            <AlertTriangle className="w-5 h-5 text-orange-500" />
          </div>
          <p className="text-3xl font-bold text-gray-800">{totalFindings}</p>
        </div>

        <div className="glass-effect rounded-xl p-6 card-hover">
          <div className="flex items-center justify-between mb-2">
            <p className="text-gray-600 text-sm font-medium">Inconsistencies</p>
            <TrendingUp className="w-5 h-5 text-red-500" />
          </div>
          <p className="text-3xl font-bold text-gray-800">{results.inconsistencies.length}</p>
        </div>

        <div className="glass-effect rounded-xl p-6 card-hover">
          <div className="flex items-center justify-between mb-2">
            <p className="text-gray-600 text-sm font-medium">Chunks Analyzed</p>
            <CheckCircle className="w-5 h-5 text-green-500" />
          </div>
          <p className="text-3xl font-bold text-gray-800">{results.chunks_created}</p>
        </div>
      </div>

      {/* Tabs */}
      <div className="glass-effect rounded-2xl p-2 mb-8 flex flex-wrap gap-2">
        {[
          { id: 'overview', label: 'Overview', icon: TrendingUp },
          { id: 'financial', label: 'Financial', count: results.financial_findings.length },
          { id: 'legal', label: 'Legal', count: results.legal_findings.length },
          { id: 'operational', label: 'Operational', count: results.operational_findings.length },
          { id: 'inconsistencies', label: 'Inconsistencies', count: results.inconsistencies.length },
          { id: 'memo', label: 'Full Report', icon: FileText },
        ].map((tab) => (
          <button
            key={tab.id}
            onClick={() => setActiveTab(tab.id as any)}
            className={`flex-1 min-w-[120px] px-4 py-3 rounded-xl font-medium transition-all duration-300 ${
              activeTab === tab.id
                ? 'bg-gradient-to-r from-blue-600 to-indigo-600 text-white shadow-lg'
                : 'text-gray-600 hover:bg-gray-100'
            }`}
          >
            <span className="flex items-center justify-center space-x-2">
              <span>{tab.label}</span>
              {tab.count !== undefined && (
                <span className={`px-2 py-0.5 rounded-full text-xs ${
                  activeTab === tab.id ? 'bg-white/20' : 'bg-gray-200'
                }`}>
                  {tab.count}
                </span>
              )}
            </span>
          </button>
        ))}
      </div>

      {/* Tab Content */}
      <div className="animate-slide-up">
        {activeTab === 'overview' && (
          <RiskChart results={results} />
        )}

        {activeTab === 'financial' && (
          <FindingsCard
            title="Financial Risk Findings"
            findings={results.financial_findings}
            color="blue"
          />
        )}

        {activeTab === 'legal' && (
          <FindingsCard
            title="Legal Risk Findings"
            findings={results.legal_findings}
            color="purple"
          />
        )}

        {activeTab === 'operational' && (
          <FindingsCard
            title="Operational Risk Findings"
            findings={results.operational_findings}
            color="green"
          />
        )}

        {activeTab === 'inconsistencies' && (
          <InconsistenciesCard inconsistencies={results.inconsistencies} />
        )}

        {activeTab === 'memo' && (
          <RiskMemoViewer memo={results.memo} />
        )}
      </div>
    </div>
  )
}
