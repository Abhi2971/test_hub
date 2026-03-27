import { useState, useEffect } from 'react'
import { useParams, useNavigate } from 'react-router-dom'
import { resultService } from '../../services/resultService'

export default function ResultDetail() {
  const { id } = useParams()
  const navigate = useNavigate()
  const [result, setResult] = useState(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    resultService.getResult(id)
      .then((r) => setResult(r.data))
      .catch(() => navigate('/results'))
      .finally(() => setLoading(false))
  }, [id])

  if (loading) return <div className="flex justify-center py-12"><div className="animate-spin rounded-full h-10 w-10 border-b-2 border-primary"></div></div>
  if (!result) return null

  const data = result.data

  const gradeColor = {
    'A+': 'bg-green-100 text-green-700',
    'A': 'bg-green-100 text-green-700',
    'B': 'bg-blue-100 text-blue-700',
    'C': 'bg-amber-100 text-amber-700',
    'D': 'bg-amber-100 text-amber-700',
    'F': 'bg-red-100 text-red-700',
  }

  return (
    <div className="space-y-6 max-w-3xl">
      <div className="bg-white rounded-xl border border-gray-200 p-6">
        <div className="flex items-center justify-between mb-6">
          <h1 className="text-xl font-bold text-gray-900">{data.exam_title} — Results</h1>
          <span className={`px-3 py-1 rounded-full text-lg font-bold ${gradeColor[data.grade] || 'bg-gray-100'}`}>{data.grade}</span>
        </div>

        <div className="grid grid-cols-3 gap-4 mb-6">
          {[
            { label: 'Score', value: `${data.score} / ${data.total_marks}` },
            { label: 'Percentage', value: `${data.percentage}%` },
            { label: 'Status', value: data.passed ? 'Passed' : 'Failed' },
          ].map((item, i) => (
            <div key={i} className="bg-gray-50 rounded-lg p-4 text-center">
              <p className="text-2xl font-bold text-gray-900">{item.value}</p>
              <p className="text-sm text-gray-500 mt-1">{item.label}</p>
            </div>
          ))}
        </div>

        <div className="flex gap-3">
          {data.certificate_url && (
            <a href={data.certificate_url} target="_blank" rel="noreferrer"
              className="px-4 py-2 bg-green-600 text-white rounded-lg text-sm font-medium hover:bg-green-700">
              View Certificate
            </a>
          )}
          <button onClick={() => navigate('/results')}
            className="px-4 py-2 border border-gray-300 text-gray-600 rounded-lg text-sm font-medium hover:bg-gray-50">
            Back to Results
          </button>
        </div>
      </div>

      {data.per_question_analysis && data.per_question_analysis.length > 0 && (
        <div className="bg-white rounded-xl border border-gray-200">
          <div className="border-b border-gray-200 px-6 py-4">
            <h2 className="font-semibold text-gray-900">Question Analysis</h2>
          </div>
          <div className="divide-y divide-gray-100">
            {data.per_question_analysis.map((q, i) => (
              <div key={i} className="px-6 py-4 flex items-start justify-between">
                <div className="flex-1">
                  <p className="text-sm text-gray-900">{q.question_text}</p>
                  <p className="text-xs text-gray-400 mt-1">Your answer: {q.student_answer} · Correct: {q.correct_answer}</p>
                </div>
                <span className={`ml-4 px-2.5 py-0.5 rounded-full text-xs font-medium ${q.correct ? 'bg-green-100 text-green-700' : 'bg-red-100 text-red-600'}`}>
                  {q.correct ? '+' : '-'} {q.marks_obtained}/{q.max_marks}
                </span>
              </div>
            ))}
          </div>
        </div>
      )}

      {data.ai_recommendation && (
        <div className="bg-white rounded-xl border border-gray-200 p-6">
          <h2 className="font-semibold text-gray-900 mb-3">AI Recommendations</h2>
          <div className="space-y-2">
            {(data.ai_recommendation.study_topics || data.ai_recommendation.recommendations || []).map((item, i) => (
              <div key={i} className="flex items-start gap-2 text-sm">
                <span className="text-primary mt-1">•</span>
                <span className="text-gray-700">{item.topic || item}</span>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  )
}
