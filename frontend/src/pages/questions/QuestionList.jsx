import { useState, useEffect } from 'react'
import { Link } from 'react-router-dom'
import { questionService } from '../../services/questionService'

export default function QuestionList() {
  const [questions, setQuestions] = useState([])
  const [loading, setLoading] = useState(true)
  const [filter, setFilter] = useState({ difficulty: '', type: '', reviewed: '' })
  const [page, setPage] = useState(1)

  const fetchQuestions = async () => {
    setLoading(true)
    try {
      const params = { page, limit: 20, ...filter }
      Object.keys(params).forEach((k) => { if (!params[k]) delete params[k] })
      const response = await questionService.getQuestions(params)
      setQuestions(response.data?.items || [])
    } catch {}
    finally { setLoading(false) }
  }

  useEffect(() => { fetchQuestions() }, [filter, page])

  const handleDelete = async (id, e) => {
    e.preventDefault()
    if (!confirm('Delete this question?')) return
    try { await questionService.deleteQuestion(id); fetchQuestions() } catch {}
  }

  return (
    <div className="space-y-5">
      <div className="flex items-center justify-between">
        <div className="flex gap-2">
          {['all', 'easy', 'medium', 'hard'].map((d) => (
            <button key={d} onClick={() => { setFilter({ ...filter, difficulty: d === 'all' ? '' : d }); setPage(1) }}
              className={`px-3 py-1.5 rounded-lg text-sm font-medium transition ${filter.difficulty === (d === 'all' ? '' : d) ? 'bg-primary text-white' : 'bg-white border border-gray-200 text-gray-600 hover:bg-gray-50'}`}>
              {d.charAt(0).toUpperCase() + d.slice(1)}
            </button>
          ))}
        </div>
        <Link to="/questions/create" className="inline-flex items-center gap-2 px-4 py-2 bg-primary text-white rounded-lg text-sm font-medium hover:bg-primary-dark">
          <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 4v16m8-8H4" />
          </svg>
          Add Question
        </Link>
      </div>

      <div className="bg-white rounded-xl border border-gray-200 overflow-hidden">
        <table className="w-full">
          <thead className="bg-gray-50 border-b border-gray-200">
            <tr>
              {['Question', 'Type', 'Difficulty', 'Topic', 'Status', 'Actions'].map((h) => (
                <th key={h} className="text-left px-6 py-3 text-xs font-semibold text-gray-500 uppercase">{h}</th>
              ))}
            </tr>
          </thead>
          <tbody className="divide-y divide-gray-100">
            {loading ? (
              <tr><td colSpan={6} className="px-6 py-8 text-center text-gray-400">Loading...</td></tr>
            ) : questions.length === 0 ? (
              <tr><td colSpan={6} className="px-6 py-8 text-center text-gray-400">No questions found</td></tr>
            ) : questions.map((q) => (
              <tr key={q.id} className="hover:bg-gray-50">
                <td className="px-6 py-4 max-w-md">
                  <p className="text-sm text-gray-900 line-clamp-2">{q.text}</p>
                </td>
                <td className="px-6 py-4 text-sm text-gray-600 capitalize">{q.question_type}</td>
                <td className="px-6 py-4">
                  <span className={`px-2 py-0.5 rounded-full text-xs font-medium ${
                    q.difficulty === 'easy' ? 'bg-green-100 text-green-700' :
                    q.difficulty === 'medium' ? 'bg-amber-100 text-amber-700' :
                    'bg-red-100 text-red-700'
                  }`}>{q.difficulty}</span>
                </td>
                <td className="px-6 py-4 text-sm text-gray-600">{q.topic || '-'}</td>
                <td className="px-6 py-4">
                  <span className={`px-2 py-0.5 rounded-full text-xs font-medium ${
                    q.is_reviewed ? (q.is_approved ? 'bg-green-100 text-green-700' : 'bg-red-100 text-red-700') : 'bg-gray-100 text-gray-600'
                  }`}>{q.is_reviewed ? (q.is_approved ? 'Approved' : 'Rejected') : 'Pending'}</span>
                </td>
                <td className="px-6 py-4">
                  <div className="flex gap-1">
                    <Link to={`/questions/${q.id}`} className="text-gray-400 hover:text-primary p-1">
                      <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" />
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M2.458 12C3.732 7.943 7.523 5 12 5c4.478 0 8.268 2.943 9.542 7-1.274 4.057-5.064 7-9.542 7-4.477 0-8.268-2.943-9.542-7z" />
                      </svg>
                    </Link>
                    <button onClick={(e) => handleDelete(q.id, e)} className="text-gray-400 hover:text-red-600 p-1">
                      <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" />
                      </svg>
                    </button>
                  </div>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      {page > 1 && <button onClick={() => setPage(p => p - 1)} className="px-4 py-2 border border-gray-200 rounded-lg text-sm hover:bg-gray-50">Previous</button>}
    </div>
  )
}
