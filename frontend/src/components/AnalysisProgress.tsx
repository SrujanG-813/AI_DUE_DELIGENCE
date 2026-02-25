import { Loader2 } from 'lucide-react'

interface AnalysisProgressProps {
  progress: number
  message: string
}

export default function AnalysisProgress({ progress, message }: AnalysisProgressProps) {
  const stages = [
    { name: 'Loading Documents', threshold: 20 },
    { name: 'Creating Embeddings', threshold: 40 },
    { name: 'Analyzing Financial Risks', threshold: 60 },
    { name: 'Analyzing Legal Risks', threshold: 75 },
    { name: 'Analyzing Operational Risks', threshold: 85 },
    { name: 'Generating Report', threshold: 95 },
    { name: 'Complete', threshold: 100 },
  ]

  const currentStage = stages.findIndex(stage => progress < stage.threshold)
  const activeStageIndex = currentStage === -1 ? stages.length - 1 : Math.max(0, currentStage - 1)

  return (
    <div className="max-w-3xl mx-auto animate-fade-in">
      <div className="glass-effect rounded-2xl p-12 text-center">
        {/* Animated Icon */}
        <div className="w-24 h-24 bg-gradient-to-br from-blue-500 to-indigo-600 rounded-full flex items-center justify-center mx-auto mb-8 shadow-2xl animate-pulse-slow">
          <Loader2 className="w-12 h-12 text-white animate-spin" />
        </div>

        {/* Title */}
        <h2 className="text-3xl font-bold gradient-text mb-4">
          Analyzing Your Documents
        </h2>
        <p className="text-gray-600 mb-8">
          Our AI agents are working hard to identify risks and generate insights...
        </p>

        {/* Progress Bar */}
        <div className="mb-8">
          <div className="flex justify-between items-center mb-2">
            <span className="text-sm font-medium text-gray-700">{message}</span>
            <span className="text-sm font-bold text-blue-600">{progress}%</span>
          </div>
          <div className="w-full h-3 bg-gray-200 rounded-full overflow-hidden">
            <div
              className="h-full bg-gradient-to-r from-blue-500 to-indigo-600 rounded-full transition-all duration-500 ease-out"
              style={{ width: `${progress}%` }}
            />
          </div>
        </div>

        {/* Stages */}
        <div className="space-y-3">
          {stages.map((stage, index) => (
            <div
              key={stage.name}
              className={`flex items-center p-3 rounded-xl transition-all duration-300 ${
                index === activeStageIndex
                  ? 'bg-blue-50 border-2 border-blue-200'
                  : index < activeStageIndex
                  ? 'bg-green-50 border-2 border-green-200'
                  : 'bg-gray-50 border-2 border-gray-200'
              }`}
            >
              <div
                className={`w-8 h-8 rounded-full flex items-center justify-center mr-3 ${
                  index === activeStageIndex
                    ? 'bg-blue-500 animate-pulse'
                    : index < activeStageIndex
                    ? 'bg-green-500'
                    : 'bg-gray-300'
                }`}
              >
                {index < activeStageIndex ? (
                  <svg className="w-5 h-5 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
                  </svg>
                ) : index === activeStageIndex ? (
                  <Loader2 className="w-5 h-5 text-white animate-spin" />
                ) : (
                  <span className="text-white text-sm font-bold">{index + 1}</span>
                )}
              </div>
              <span
                className={`font-medium ${
                  index === activeStageIndex
                    ? 'text-blue-700'
                    : index < activeStageIndex
                    ? 'text-green-700'
                    : 'text-gray-500'
                }`}
              >
                {stage.name}
              </span>
            </div>
          ))}
        </div>

        {/* Fun Fact */}
        <div className="mt-8 p-4 bg-gradient-to-r from-blue-50 to-indigo-50 rounded-xl border border-blue-100">
          <p className="text-sm text-gray-600">
            <span className="font-semibold text-blue-600">💡 Did you know?</span> Our AI analyzes 
            documents using GPT-4 and generates evidence-backed findings with full citation traceability.
          </p>
        </div>
      </div>
    </div>
  )
}
