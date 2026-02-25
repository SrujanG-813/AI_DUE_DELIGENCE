import { Inconsistency } from '../types'
import { AlertTriangle, FileText } from 'lucide-react'

interface InconsistenciesCardProps {
  inconsistencies: Inconsistency[]
}

export default function InconsistenciesCard({ inconsistencies }: InconsistenciesCardProps) {
  const getSeverityColor = (severity: string) => {
    if (severity === 'High') return 'bg-red-100 text-red-700 border-red-300'
    if (severity === 'Medium') return 'bg-yellow-100 text-yellow-700 border-yellow-300'
    return 'bg-green-100 text-green-700 border-green-300'
  }

  if (inconsistencies.length === 0) {
    return (
      <div className="glass-effect rounded-2xl p-12 text-center">
        <div className="w-20 h-20 bg-gradient-to-br from-green-500 to-teal-600 rounded-full flex items-center justify-center mx-auto mb-4">
          <FileText className="w-10 h-10 text-white" />
        </div>
        <h3 className="text-2xl font-bold text-gray-800 mb-2">No Inconsistencies Found</h3>
        <p className="text-gray-600">All documents appear to be consistent with each other</p>
      </div>
    )
  }

  return (
    <div className="space-y-6">
      <div className="glass-effect rounded-2xl p-6 bg-gradient-to-r from-orange-500 to-red-500 text-white">
        <div className="flex items-center space-x-3 mb-2">
          <AlertTriangle className="w-8 h-8" />
          <h3 className="text-2xl font-bold">Cross-Document Inconsistencies</h3>
        </div>
        <p className="text-white/90">{inconsistencies.length} inconsistencies detected across documents</p>
      </div>

      <div className="space-y-4">
        {inconsistencies.map((inconsistency, index) => (
          <div
            key={index}
            className="glass-effect rounded-xl p-6 card-hover border-l-4 border-orange-500"
          >
            <div className="flex items-start justify-between mb-4">
              <div className={`px-3 py-1 rounded-full border-2 ${getSeverityColor(inconsistency.severity)} font-semibold text-sm`}>
                {inconsistency.severity}
              </div>
              <span className="text-sm text-gray-500">Inconsistency #{index + 1}</span>
            </div>

            <h4 className="text-lg font-bold text-gray-800 mb-3">
              {inconsistency.issue_description}
            </h4>

            <div className="bg-orange-50 border-l-4 border-orange-300 rounded-lg p-4 mb-4">
              <p className="text-sm font-medium text-gray-700 mb-2">Details:</p>
              <p className="text-gray-600 text-sm leading-relaxed">
                {inconsistency.details}
              </p>
            </div>

            <div className="flex flex-wrap gap-2">
              <span className="text-sm font-medium text-gray-700">Documents Involved:</span>
              {inconsistency.documents_involved.map((doc, idx) => (
                <span
                  key={idx}
                  className="px-3 py-1 bg-gray-100 text-gray-700 rounded-full text-sm font-medium"
                >
                  {doc}
                </span>
              ))}
            </div>
          </div>
        ))}
      </div>
    </div>
  )
}
