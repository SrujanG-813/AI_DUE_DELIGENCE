import { useState } from 'react'
import Header from './components/Header'
import FileUpload from './components/FileUpload'
import AnalysisProgress from './components/AnalysisProgress'
import ResultsDashboard from './components/ResultsDashboard'
import { AnalysisResults } from './types'

function App() {
  const [files, setFiles] = useState<File[]>([])
  const [isAnalyzing, setIsAnalyzing] = useState(false)
  const [progress, setProgress] = useState(0)
  const [progressMessage, setProgressMessage] = useState('')
  const [results, setResults] = useState<AnalysisResults | null>(null)
  const [error, setError] = useState<string | null>(null)

  const handleFilesSelected = (selectedFiles: File[]) => {
    setFiles(selectedFiles)
    setResults(null)
    setError(null)
  }

  const handleAnalyze = async () => {
    if (files.length === 0) {
      setError('Please upload at least one document')
      return
    }

    setIsAnalyzing(true)
    setProgress(0)
    setError(null)
    setProgressMessage('Preparing documents...')

    try {
      const formData = new FormData()
      files.forEach(file => {
        formData.append('files', file)
      })

      // Simulate progress updates
      const progressInterval = setInterval(() => {
        setProgress(prev => {
          if (prev >= 90) {
            clearInterval(progressInterval)
            return 90
          }
          return prev + 10
        })
      }, 1000)

      const response = await fetch('/api/analyze', {
        method: 'POST',
        body: formData,
      })

      clearInterval(progressInterval)

      if (!response.ok) {
        const errorData = await response.json().catch(() => ({ detail: 'Unknown error' }))
        throw new Error(errorData.detail || `Server error: ${response.status}`)
      }

      const data: AnalysisResults = await response.json()
      
      setProgress(100)
      setProgressMessage('Analysis complete!')
      setResults(data)
      
      setTimeout(() => {
        setIsAnalyzing(false)
      }, 500)

    } catch (err) {
      setError(err instanceof Error ? err.message : 'An error occurred during analysis')
      setIsAnalyzing(false)
      setProgress(0)
    }
  }

  const handleReset = () => {
    setFiles([])
    setResults(null)
    setError(null)
    setProgress(0)
    setProgressMessage('')
  }

  return (
    <div className="min-h-screen">
      <Header />
      
      <main className="container mx-auto px-4 py-8 max-w-7xl">
        {!results && !isAnalyzing && (
          <div className="animate-fade-in">
            <div className="text-center mb-12">
              <h2 className="text-4xl font-bold gradient-text mb-4">
                AI-Powered Investment Risk Analysis
              </h2>
              <p className="text-gray-600 text-lg max-w-2xl mx-auto">
                Upload your business documents and let our AI agents analyze financial, legal, 
                and operational risks with evidence-backed findings.
              </p>
            </div>

            <FileUpload 
              files={files}
              onFilesSelected={handleFilesSelected}
              onAnalyze={handleAnalyze}
              error={error}
            />

            {/* Features Section */}
            <div className="mt-16 grid md:grid-cols-3 gap-8">
              <div className="glass-effect rounded-2xl p-6 card-hover">
                <div className="w-12 h-12 bg-gradient-to-br from-blue-500 to-indigo-600 rounded-xl flex items-center justify-center mb-4">
                  <svg className="w-6 h-6 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
                  </svg>
                </div>
                <h3 className="text-xl font-bold text-gray-800 mb-2">Multi-Document Analysis</h3>
                <p className="text-gray-600">
                  Process multiple PDFs and text files simultaneously for comprehensive risk assessment.
                </p>
              </div>

              <div className="glass-effect rounded-2xl p-6 card-hover">
                <div className="w-12 h-12 bg-gradient-to-br from-purple-500 to-pink-600 rounded-xl flex items-center justify-center mb-4">
                  <svg className="w-6 h-6 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9.663 17h4.673M12 3v1m6.364 1.636l-.707.707M21 12h-1M4 12H3m3.343-5.657l-.707-.707m2.828 9.9a5 5 0 117.072 0l-.548.547A3.374 3.374 0 0014 18.469V19a2 2 0 11-4 0v-.531c0-.895-.356-1.754-.988-2.386l-.548-.547z" />
                  </svg>
                </div>
                <h3 className="text-xl font-bold text-gray-800 mb-2">AI-Powered Insights</h3>
                <p className="text-gray-600">
                  Specialized AI agents analyze financial, legal, and operational dimensions with precision.
                </p>
              </div>

              <div className="glass-effect rounded-2xl p-6 card-hover">
                <div className="w-12 h-12 bg-gradient-to-br from-green-500 to-teal-600 rounded-xl flex items-center justify-center mb-4">
                  <svg className="w-6 h-6 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
                  </svg>
                </div>
                <h3 className="text-xl font-bold text-gray-800 mb-2">Evidence-Based Reports</h3>
                <p className="text-gray-600">
                  Every finding includes citations to source documents with page references for full traceability.
                </p>
              </div>
            </div>
          </div>
        )}

        {isAnalyzing && (
          <AnalysisProgress 
            progress={progress}
            message={progressMessage}
          />
        )}

        {results && !isAnalyzing && (
          <ResultsDashboard 
            results={results}
            onReset={handleReset}
          />
        )}
      </main>

      {/* Footer */}
      <footer className="mt-20 py-8 border-t border-gray-200">
        <div className="container mx-auto px-4 text-center text-gray-600">
          <p className="mb-2">AI Due Diligence Engine v2.0</p>
          <p className="text-sm">Powered by GPT-4, LangChain, and FAISS</p>
        </div>
      </footer>
    </div>
  )
}

export default App
