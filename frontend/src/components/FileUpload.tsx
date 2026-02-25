import { useCallback } from 'react'
import { useDropzone } from 'react-dropzone'
import { Upload, File, X, AlertCircle } from 'lucide-react'
import clsx from 'clsx'

interface FileUploadProps {
  files: File[]
  onFilesSelected: (files: File[]) => void
  onAnalyze: () => void
  error: string | null
}

export default function FileUpload({ files, onFilesSelected, onAnalyze, error }: FileUploadProps) {
  const onDrop = useCallback((acceptedFiles: File[]) => {
    onFilesSelected([...files, ...acceptedFiles])
  }, [files, onFilesSelected])

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop,
    accept: {
      'application/pdf': ['.pdf'],
      'text/plain': ['.txt'],
    },
  })

  const removeFile = (index: number) => {
    const newFiles = files.filter((_, i) => i !== index)
    onFilesSelected(newFiles)
  }

  const formatFileSize = (bytes: number) => {
    if (bytes === 0) return '0 Bytes'
    const k = 1024
    const sizes = ['Bytes', 'KB', 'MB', 'GB']
    const i = Math.floor(Math.log(bytes) / Math.log(k))
    return Math.round(bytes / Math.pow(k, i) * 100) / 100 + ' ' + sizes[i]
  }

  return (
    <div className="max-w-4xl mx-auto">
      {/* Dropzone */}
      <div
        {...getRootProps()}
        className={clsx(
          'glass-effect rounded-2xl p-12 border-2 border-dashed transition-all duration-300 cursor-pointer',
          isDragActive 
            ? 'border-blue-500 bg-blue-50/50 scale-105' 
            : 'border-gray-300 hover:border-blue-400 hover:bg-blue-50/30'
        )}
      >
        <input {...getInputProps()} />
        <div className="text-center">
          <div className="w-20 h-20 bg-gradient-to-br from-blue-500 to-indigo-600 rounded-2xl flex items-center justify-center mx-auto mb-6 shadow-lg">
            <Upload className="w-10 h-10 text-white" />
          </div>
          
          {isDragActive ? (
            <p className="text-xl font-semibold text-blue-600 mb-2">
              Drop your files here...
            </p>
          ) : (
            <>
              <p className="text-xl font-semibold text-gray-800 mb-2">
                Drag & drop your documents here
              </p>
              <p className="text-gray-600 mb-4">
                or click to browse your files
              </p>
              <p className="text-sm text-gray-500">
                Supports PDF and TXT files • Max 10 files
              </p>
            </>
          )}
        </div>
      </div>

      {/* Error Message */}
      {error && (
        <div className="mt-6 glass-effect rounded-xl p-4 border-l-4 border-red-500 bg-red-50/50 animate-slide-up">
          <div className="flex items-center">
            <AlertCircle className="w-5 h-5 text-red-500 mr-3" />
            <p className="text-red-700 font-medium">{error}</p>
          </div>
        </div>
      )}

      {/* File List */}
      {files.length > 0 && (
        <div className="mt-8 space-y-3 animate-slide-up">
          <h3 className="text-lg font-semibold text-gray-800 mb-4">
            Uploaded Files ({files.length})
          </h3>
          
          {files.map((file, index) => (
            <div
              key={index}
              className="glass-effect rounded-xl p-4 flex items-center justify-between card-hover"
            >
              <div className="flex items-center space-x-4 flex-1">
                <div className="w-12 h-12 bg-gradient-to-br from-blue-100 to-indigo-100 rounded-lg flex items-center justify-center">
                  <File className="w-6 h-6 text-blue-600" />
                </div>
                <div className="flex-1 min-w-0">
                  <p className="font-medium text-gray-800 truncate">
                    {file.name}
                  </p>
                  <p className="text-sm text-gray-500">
                    {formatFileSize(file.size)}
                  </p>
                </div>
              </div>
              
              <button
                onClick={() => removeFile(index)}
                className="ml-4 p-2 hover:bg-red-50 rounded-lg transition-colors group"
              >
                <X className="w-5 h-5 text-gray-400 group-hover:text-red-500" />
              </button>
            </div>
          ))}

          {/* Analyze Button */}
          <button
            onClick={onAnalyze}
            disabled={files.length === 0}
            className="w-full btn-primary mt-6 py-4 text-lg disabled:opacity-50 disabled:cursor-not-allowed"
          >
            <span className="flex items-center justify-center">
              <svg className="w-6 h-6 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 10V3L4 14h7v7l9-11h-7z" />
              </svg>
              Start AI Analysis
            </span>
          </button>
        </div>
      )}
    </div>
  )
}
