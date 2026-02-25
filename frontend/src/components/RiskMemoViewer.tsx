import ReactMarkdown from 'react-markdown'
import { FileText } from 'lucide-react'

interface RiskMemoViewerProps {
  memo: string
}

export default function RiskMemoViewer({ memo }: RiskMemoViewerProps) {
  return (
    <div className="glass-effect rounded-2xl p-8">
      <div className="flex items-center space-x-3 mb-6 pb-6 border-b border-gray-200">
        <div className="w-12 h-12 bg-gradient-to-br from-blue-600 to-indigo-600 rounded-xl flex items-center justify-center">
          <FileText className="w-6 h-6 text-white" />
        </div>
        <div>
          <h3 className="text-2xl font-bold text-gray-800">Complete Risk Memo</h3>
          <p className="text-gray-600 text-sm">Full analysis report with all findings and evidence</p>
        </div>
      </div>

      <div className="prose prose-slate max-w-none">
        <ReactMarkdown
          components={{
            h1: ({ children }) => (
              <h1 className="text-4xl font-bold gradient-text mb-6 mt-8">{children}</h1>
            ),
            h2: ({ children }) => (
              <h2 className="text-3xl font-bold text-gray-800 mb-4 mt-8 pb-2 border-b-2 border-blue-200">{children}</h2>
            ),
            h3: ({ children }) => (
              <h3 className="text-2xl font-bold text-gray-700 mb-3 mt-6">{children}</h3>
            ),
            h4: ({ children }) => (
              <h4 className="text-xl font-semibold text-gray-700 mb-2 mt-4">{children}</h4>
            ),
            p: ({ children }) => (
              <p className="text-gray-600 leading-relaxed mb-4">{children}</p>
            ),
            ul: ({ children }) => (
              <ul className="list-disc list-inside space-y-2 mb-4 text-gray-600">{children}</ul>
            ),
            ol: ({ children }) => (
              <ol className="list-decimal list-inside space-y-2 mb-4 text-gray-600">{children}</ol>
            ),
            li: ({ children }) => (
              <li className="ml-4">{children}</li>
            ),
            strong: ({ children }) => (
              <strong className="font-bold text-gray-800">{children}</strong>
            ),
            em: ({ children }) => (
              <em className="italic text-gray-700">{children}</em>
            ),
            blockquote: ({ children }) => (
              <blockquote className="border-l-4 border-blue-500 pl-4 py-2 my-4 bg-blue-50 rounded-r-lg">
                {children}
              </blockquote>
            ),
            code: ({ children }) => (
              <code className="bg-gray-100 px-2 py-1 rounded text-sm font-mono text-gray-800">
                {children}
              </code>
            ),
            pre: ({ children }) => (
              <pre className="bg-gray-900 text-gray-100 p-4 rounded-lg overflow-x-auto mb-4">
                {children}
              </pre>
            ),
            hr: () => (
              <hr className="my-8 border-t-2 border-gray-200" />
            ),
            table: ({ children }) => (
              <div className="overflow-x-auto mb-4">
                <table className="min-w-full divide-y divide-gray-200 border border-gray-200 rounded-lg">
                  {children}
                </table>
              </div>
            ),
            thead: ({ children }) => (
              <thead className="bg-gray-50">{children}</thead>
            ),
            tbody: ({ children }) => (
              <tbody className="bg-white divide-y divide-gray-200">{children}</tbody>
            ),
            tr: ({ children }) => (
              <tr>{children}</tr>
            ),
            th: ({ children }) => (
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                {children}
              </th>
            ),
            td: ({ children }) => (
              <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-600">
                {children}
              </td>
            ),
          }}
        >
          {memo}
        </ReactMarkdown>
      </div>
    </div>
  )
}
