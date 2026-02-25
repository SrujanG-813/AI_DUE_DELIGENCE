import { AnalysisResults } from '../types'
import { PieChart, Pie, Cell, ResponsiveContainer, Legend, Tooltip, BarChart, Bar, XAxis, YAxis, CartesianGrid } from 'recharts'

interface RiskChartProps {
  results: AnalysisResults
}

export default function RiskChart({ results }: RiskChartProps) {
  const countBySeverity = (findings: any[]) => {
    return {
      High: findings.filter(f => f.severity === 'High').length,
      Medium: findings.filter(f => f.severity === 'Medium').length,
      Low: findings.filter(f => f.severity === 'Low').length,
    }
  }

  const financialCounts = countBySeverity(results.financial_findings)
  const legalCounts = countBySeverity(results.legal_findings)
  const operationalCounts = countBySeverity(results.operational_findings)

  const categoryData = [
    {
      name: 'Financial',
      High: financialCounts.High,
      Medium: financialCounts.Medium,
      Low: financialCounts.Low,
      total: results.financial_findings.length,
    },
    {
      name: 'Legal',
      High: legalCounts.High,
      Medium: legalCounts.Medium,
      Low: legalCounts.Low,
      total: results.legal_findings.length,
    },
    {
      name: 'Operational',
      High: operationalCounts.High,
      Medium: operationalCounts.Medium,
      Low: operationalCounts.Low,
      total: results.operational_findings.length,
    },
  ]

  const totalFindings = results.financial_findings.length + results.legal_findings.length + results.operational_findings.length

  const pieData = [
    { name: 'Financial', value: results.financial_findings.length, color: '#3b82f6' },
    { name: 'Legal', value: results.legal_findings.length, color: '#8b5cf6' },
    { name: 'Operational', value: results.operational_findings.length, color: '#10b981' },
  ]

  return (
    <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
      {/* Findings by Category - Pie Chart */}
      <div className="glass-effect rounded-2xl p-6">
        <h3 className="text-xl font-bold text-gray-800 mb-6">Findings by Category</h3>
        <ResponsiveContainer width="100%" height={300}>
          <PieChart>
            <Pie
              data={pieData}
              cx="50%"
              cy="50%"
              labelLine={false}
              label={({ name, percent }) => `${name}: ${(percent * 100).toFixed(0)}%`}
              outerRadius={100}
              fill="#8884d8"
              dataKey="value"
            >
              {pieData.map((entry, index) => (
                <Cell key={`cell-${index}`} fill={entry.color} />
              ))}
            </Pie>
            <Tooltip />
            <Legend />
          </PieChart>
        </ResponsiveContainer>
        <div className="mt-6 grid grid-cols-3 gap-4">
          {pieData.map((item) => (
            <div key={item.name} className="text-center">
              <div className="w-12 h-12 rounded-full mx-auto mb-2" style={{ backgroundColor: item.color }} />
              <p className="text-sm font-medium text-gray-700">{item.name}</p>
              <p className="text-2xl font-bold text-gray-800">{item.value}</p>
            </div>
          ))}
        </div>
      </div>

      {/* Severity Distribution - Bar Chart */}
      <div className="glass-effect rounded-2xl p-6">
        <h3 className="text-xl font-bold text-gray-800 mb-6">Severity Distribution</h3>
        <ResponsiveContainer width="100%" height={300}>
          <BarChart data={categoryData}>
            <CartesianGrid strokeDasharray="3 3" stroke="#e5e7eb" />
            <XAxis dataKey="name" stroke="#6b7280" />
            <YAxis stroke="#6b7280" />
            <Tooltip />
            <Legend />
            <Bar dataKey="High" stackId="a" fill="#ef4444" />
            <Bar dataKey="Medium" stackId="a" fill="#f59e0b" />
            <Bar dataKey="Low" stackId="a" fill="#22c55e" />
          </BarChart>
        </ResponsiveContainer>
        <div className="mt-6 flex justify-around">
          <div className="text-center">
            <div className="w-4 h-4 bg-red-500 rounded mx-auto mb-1" />
            <p className="text-xs text-gray-600">High Risk</p>
          </div>
          <div className="text-center">
            <div className="w-4 h-4 bg-yellow-500 rounded mx-auto mb-1" />
            <p className="text-xs text-gray-600">Medium Risk</p>
          </div>
          <div className="text-center">
            <div className="w-4 h-4 bg-green-500 rounded mx-auto mb-1" />
            <p className="text-xs text-gray-600">Low Risk</p>
          </div>
        </div>
      </div>

      {/* Summary Cards */}
      <div className="lg:col-span-2 grid grid-cols-1 md:grid-cols-3 gap-6">
        <div className="glass-effect rounded-xl p-6 border-l-4 border-red-500">
          <p className="text-gray-600 text-sm font-medium mb-2">High Severity Findings</p>
          <p className="text-4xl font-bold text-red-600">
            {financialCounts.High + legalCounts.High + operationalCounts.High}
          </p>
          <p className="text-sm text-gray-500 mt-2">Require immediate attention</p>
        </div>

        <div className="glass-effect rounded-xl p-6 border-l-4 border-yellow-500">
          <p className="text-gray-600 text-sm font-medium mb-2">Medium Severity Findings</p>
          <p className="text-4xl font-bold text-yellow-600">
            {financialCounts.Medium + legalCounts.Medium + operationalCounts.Medium}
          </p>
          <p className="text-sm text-gray-500 mt-2">Should be reviewed</p>
        </div>

        <div className="glass-effect rounded-xl p-6 border-l-4 border-green-500">
          <p className="text-gray-600 text-sm font-medium mb-2">Low Severity Findings</p>
          <p className="text-4xl font-bold text-green-600">
            {financialCounts.Low + legalCounts.Low + operationalCounts.Low}
          </p>
          <p className="text-sm text-gray-500 mt-2">Minor concerns</p>
        </div>
      </div>
    </div>
  )
}
