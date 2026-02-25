import { RiskFinding } from '../types'
import { AlertCircle, AlertTriangle, Info, FileText } from 'lucide-react'

interface FindingsCardProps {
  title: string
  findings: RiskFinding[]
  color: 'blue' | 'purple' | 'green'
}

export default function FindingsCard({ title, findings, color }: FindingsCardProps) {
  const colorClasses = {
    blue: {
      bg: 'from-blue-500 to-blue-600',
      light: 'bg-blue-50',
      border: 'border-blue-200',
      text: 'text-blue-700',
    },
    purple: {
      bg: 'from-purple-500 to-purple-600',
      light: 'bg-purple-50',
      border: 'border-purple-200',
      text: 'text-purple-700',
    },
    green: {
      bg: 'from-green-500 to-green-600',
      light: 'bg-green-50',
      border: 'border-green-200',
      text: 'text-green-700',
    },
  }

  const getSeverityIcon = (severity: string) => {
    if (severity === 'High') return <AlertCircle className="w-5 h-5" />
    if (severity === 'Medium') return <AlertTriangle className="w-5 h-5" />
    return <Info className="w-5 h-5" />
  }

  const getSeverityColor = (severity: string) => {
    if (severity === 'High') return 'bg-red-100 text-red-700 border-red-300'
    if (severity === 'Medium') return 'bg-yellow-100 text-yellow-700 border-yellow-300'
    return 'bg-green-100 text-green-700 border-green-300'
  }

  if (findings.length === 0) {
    return (
      <div className="glass-effect rounded-2xl p-12 text-center">
        <div className={`w-20 h-20 bg-gradient-to-br ${colorClasses[color].bg} rounded-full flex items-center justify-center mx-auto mb-4`}>
          <FileText className="w-10 h-10 text-white" />
        </div>
        <h3 className="text-2xl font-bold text-gray-800 mb-2">{title}</h3>
        <p className="text-gray-600">No risks identified in this category</p>
      </div>
    )
  }

  return (
    <div className="space-y-6">
      <div className={`glass-effect rounded-2xl p-6 bg-gradient-to-r ${colorClasses[color].bg} text-white`}>
        <h3 className="text-2xl font-bold mb-2">{title}</h3>
        <p className="text-white/90">{findings.length} findings identified</p>
      </div>

      <div className="space-y-4">
        {findings.map((finding, index) => (
          <div
            key={index}
            className="glass-effect rounded-xl p-6 card-hover"
          >
            <div className="flex items-start justify-between mb-4">
              <div className="flex items-center space-x-3">
                <div className={`px-3 py-1 rounded-full border-2 ${getSeverityColor(finding.severity)} font-semibold text-sm flex items-center space-x-2`}>
                  {getSeverityIcon(finding.severity)}
                  <span>{finding.severity}</span>
                </div>
                <span className="text-sm text-gray-500">Finding #{index + 1}</span>
              </div>
            </div>

            <h4 className="text-lg font-bold text-gray-800 mb-3">
              {finding.risk_description}
            </h4>

            <div className={`${colorClasses[color].light} ${colorClasses[color].border} border-l-4 rounded-lg p-4 mb-4`}>
              <p className="text-sm font-medium text-gray-700 mb-1">Evidence:</p>
              <p className="text-gray-600 text-sm leading-relaxed">
                {finding.evidence}
              </p>
            </div>

            <div className="flex items-center justify-between text-sm">
              <div className="flex items-center space-x-2 text-gray-600">
                <FileText className="w-4 h-4" />
                <span className="font-medium">{finding.source_document}</span>
              </div>
              <span className="text-gray-500">{finding.source_location}</span>
            </div>
          </div>
        ))}
      </div>
    </div>
  )
}
