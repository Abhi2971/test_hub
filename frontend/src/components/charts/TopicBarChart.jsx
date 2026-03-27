import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, Legend } from 'recharts'

export default function TopicBarChart({ data = [], title }) {
  if (!data || data.length === 0) {
    return (
      <div className="bg-white dark:bg-gray-800 rounded-lg p-6 shadow-sm">
        <h3 className="text-lg font-semibold text-gray-800 dark:text-white mb-4">{title || 'Topic Performance'}</h3>
        <div className="flex items-center justify-center h-48 text-gray-500">
          No data available
        </div>
      </div>
    )
  }

  const CustomTooltip = ({ active, payload, label }) => {
    if (active && payload && payload.length) {
      const correct = payload.find(p => p.dataKey === 'correct')?.value || 0
      const wrong = payload.find(p => p.dataKey === 'wrong')?.value || 0
      const total = correct + wrong
      const percentage = total > 0 ? Math.round((correct / total) * 100) : 0
      return (
        <div className="bg-white dark:bg-gray-800 border border-gray-200 dark:border-gray-700 rounded-lg p-3 shadow-sm">
          <p className="font-medium text-gray-800 dark:text-white mb-2">{label}</p>
          <p className="text-sm text-green-600">Correct: {correct}</p>
          <p className="text-sm text-red-600">Wrong: {wrong}</p>
          <p className="text-sm text-gray-600 dark:text-gray-300">Percentage: {percentage}%</p>
        </div>
      )
    }
    return null
  }

  return (
    <div className="bg-white dark:bg-gray-800 rounded-lg p-6 shadow-sm">
      <h3 className="text-lg font-semibold text-gray-800 dark:text-white mb-4">{title || 'Topic Performance'}</h3>
      <div className="h-80">
        <ResponsiveContainer width="100%" height="100%">
          <BarChart data={data} margin={{ top: 20, right: 30, left: 0, bottom: 5 }}>
            <CartesianGrid strokeDasharray="3 3" stroke="#e5e7eb" />
            <XAxis
              dataKey="topic"
              tick={{ fontSize: 12, fill: '#6b7280' }}
              axisLine={{ stroke: '#e5e7eb' }}
            />
            <YAxis
              tick={{ fontSize: 12, fill: '#6b7280' }}
              axisLine={{ stroke: '#e5e7eb' }}
            />
            <Tooltip content={<CustomTooltip />} />
            <Legend
              verticalAlign="top"
              height={36}
              formatter={(value) => (
                <span className="text-gray-600 dark:text-gray-300">{value}</span>
              )}
            />
            <Bar dataKey="correct" name="Correct" fill="#22c55e" radius={[4, 4, 0, 0]} />
            <Bar dataKey="wrong" name="Wrong" fill="#ef4444" radius={[4, 4, 0, 0]} />
          </BarChart>
        </ResponsiveContainer>
      </div>
    </div>
  )
}