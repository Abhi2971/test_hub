import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, ReferenceLine, Dot } from 'recharts'

export default function AttemptTimeline({ data = [], title }) {
  if (!data || data.length === 0) {
    return (
      <div className="bg-white dark:bg-gray-800 rounded-lg p-6 shadow-sm">
        <h3 className="text-lg font-semibold text-gray-800 dark:text-white mb-4">{title || 'Performance Over Time'}</h3>
        <div className="flex items-center justify-center h-48 text-gray-500">
          No data available
        </div>
      </div>
    )
  }

  const CustomTooltip = ({ active, payload, label }) => {
    if (active && payload && payload.length) {
      return (
        <div className="bg-white dark:bg-gray-800 border border-gray-200 dark:border-gray-700 rounded-lg p-3 shadow-sm">
          <p className="font-medium text-gray-800 dark:text-white mb-2">{label}</p>
          <p className="text-sm text-gray-600 dark:text-gray-300">Score: {payload[0]?.value || 0}%</p>
          {payload[0]?.payload?.score !== undefined && (
            <p className="text-sm text-gray-500">Points: {payload[0]?.payload?.score}</p>
          )}
        </div>
      )
    }
    return null
  }

  return (
    <div className="bg-white dark:bg-gray-800 rounded-lg p-6 shadow-sm">
      <h3 className="text-lg font-semibold text-gray-800 dark:text-white mb-4">{title || 'Performance Over Time'}</h3>
      <div className="h-80">
        <ResponsiveContainer width="100%" height="100%">
          <LineChart data={data} margin={{ top: 20, right: 30, left: 0, bottom: 5 }}>
            <CartesianGrid strokeDasharray="3 3" stroke="#e5e7eb" />
            <XAxis
              dataKey="date"
              tick={{ fontSize: 12, fill: '#6b7280' }}
              axisLine={{ stroke: '#e5e7eb' }}
            />
            <YAxis
              domain={[0, 100]}
              tick={{ fontSize: 12, fill: '#6b7280' }}
              axisLine={{ stroke: '#e5e7eb' }}
              tickFormatter={(value) => `${value}%`}
            />
            <Tooltip content={<CustomTooltip />} />
            <ReferenceLine
              y={60}
              stroke="#f59e0b"
              strokeDasharray="5 5"
              label={{
                value: 'Pass (60%)',
                position: 'right',
                fill: '#f59e0b',
                fontSize: 12,
              }}
            />
            <Line
              type="monotone"
              dataKey="percentage"
              name="Score"
              stroke="#3b82f6"
              strokeWidth={2}
              dot={{ fill: '#3b82f6', strokeWidth: 2, r: 4 }}
              activeDot={{ r: 6, fill: '#3b82f6' }}
            />
          </LineChart>
        </ResponsiveContainer>
      </div>
    </div>
  )
}