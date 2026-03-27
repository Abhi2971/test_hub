import { useState, useEffect } from 'react'
import { Link } from 'react-router-dom'
import { examService } from '../../services/examService'

export default function ExamList() {
  const [exams, setExams] = useState([])
  const [loading, setLoading] = useState(true)
  const [filter, setFilter] = useState('all')
  const [page, setPage] = useState(1)
  const [totalPages, setTotalPages] = useState(1)

  const fetchExams = async () => {
    setLoading(true)
    try {
      const params = { page, limit: 10 }
      if (filter !== 'all') params.status = filter
      const response = await examService.getExams(params)
      setExams(response.data?.items || [])
      setTotalPages(response.data?.total_pages || 1)
    } catch (err) {
      console.error(err)
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => { fetchExams() }, [filter, page])

  const handleDelete = async (id, e) => {
    e.preventDefault()
    if (!confirm('Delete this exam?')) return
    try {
      await examService.deleteExam(id)
      fetchExams()
    } catch {}
  }

  const handlePublish = async (id, e) => {
    e.preventDefault()
    try {
      await examService.publishExam(id)
      fetchExams()
    } catch {}
  }

  const statusColors = {
    draft: 'bg-gray-100 text-gray-600',
    published: 'bg-blue-100 text-blue-700',
    active: 'bg-green-100 text-green-700',
    closed: 'bg-red-100 text-red-600',
    cancelled: 'bg-gray-100 text-gray-400',
  }

  return (
    <div className="space-y-5">
      <div className="flex items-center justify-between">
        <div className="flex gap-2">
          {['all', 'draft', 'published', 'active', 'closed'].map((s) => (
            <button
              key={s}
              onClick={() => { setFilter(s); setPage(1) }}
              className={`px-3 py-1.5 rounded-lg text-sm font-medium transition ${
                filter === s ? 'bg-primary text-white' : 'bg-white border border-gray-200 text-gray-600 hover:bg-gray-50'
              }`}
            >
              {s === 'all' ? 'All' : s.charAt(0).toUpperCase() + s.slice(1)}
            </button>
          ))}
        </div>
        <Link to="/exams/create" className="inline-flex items-center gap-2 px-4 py-2 bg-primary text-white rounded-lg text-sm font-medium hover:bg-primary-dark transition">
          <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 4v16m8-8H4" />
          </svg>
          New Exam
        </Link>
      </div>

      <div className="bg-white rounded-xl border border-gray-200 overflow-hidden">
        <table className="w-full">
          <thead className="bg-gray-50 border-b border-gray-200">
            <tr>
              {['Title', 'Status', 'Questions', 'Marks', 'Duration', 'Attempts', 'Actions'].map((h) => (
                <th key={h} className="text-left px-6 py-3 text-xs font-semibold text-gray-500 uppercase tracking-wider">{h}</th>
              ))}
            </tr>
          </thead>
          <tbody className="divide-y divide-gray-100">
            {loading ? (
              <tr><td colSpan={7} className="px-6 py-8 text-center text-gray-400">Loading...</td></tr>
            ) : exams.length === 0 ? (
              <tr><td colSpan={7} className="px-6 py-8 text-center text-gray-400">No exams found</td></tr>
            ) : exams.map((exam) => (
              <tr key={exam.id} className="hover:bg-gray-50">
                <td className="px-6 py-4">
                  <Link to={`/exams/${exam.id}`} className="font-medium text-gray-900 hover:text-primary">
                    {exam.title}
                  </Link>
                  {exam.description && (
                    <p className="text-sm text-gray-400 truncate max-w-xs">{exam.description}</p>
                  )}
                </td>
                <td className="px-6 py-4">
                  <span className={`px-2.5 py-1 rounded-full text-xs font-medium ${statusColors[exam.status] || ''}`}>
                    {exam.status}
                  </span>
                </td>
                <td className="px-6 py-4 text-sm text-gray-600">{exam.question_count || 0}</td>
                <td className="px-6 py-4 text-sm text-gray-600">{exam.total_marks}</td>
                <td className="px-6 py-4 text-sm text-gray-600">{exam.duration_minutes} min</td>
                <td className="px-6 py-4 text-sm text-gray-600">{exam.attempt_count || 0}</td>
                <td className="px-6 py-4">
                  <div className="flex items-center gap-2">
                    <Link to={`/exams/${exam.id}`} className="text-gray-400 hover:text-primary p-1" title="View">
                      <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" />
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M2.458 12C3.732 7.943 7.523 5 12 5c4.478 0 8.268 2.943 9.542 7-1.274 4.057-5.064 7-9.542 7-4.477 0-8.268-2.943-9.542-7z" />
                      </svg>
                    </Link>
                    <Link to={`/exams/${exam.id}/edit`} className="text-gray-400 hover:text-primary p-1" title="Edit">
                      <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M11 5H6a2 2 0 00-2 2v11a2 2 0 002 2h11a2 2 0 002-2v-5m-1.414-9.414a2 2 0 112.828 2.828L11.828 15H9v-2.828l8.586-8.586z" />
                      </svg>
                    </Link>
                    {exam.status === 'draft' && (
                      <button onClick={(e) => handlePublish(exam.id, e)} className="text-gray-400 hover:text-green-600 p-1" title="Publish">
                        <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
                        </svg>
                      </button>
                    )}
                    <button onClick={(e) => handleDelete(exam.id, e)} className="text-gray-400 hover:text-red-600 p-1" title="Delete">
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

      {totalPages > 1 && (
        <div className="flex items-center justify-center gap-2">
          <button disabled={page <= 1} onClick={() => setPage(p => p - 1)}
            className="px-3 py-1.5 border border-gray-200 rounded-lg text-sm disabled:opacity-50 hover:bg-gray-50">
            Previous
          </button>
          <span className="text-sm text-gray-500">Page {page} of {totalPages}</span>
          <button disabled={page >= totalPages} onClick={() => setPage(p => p + 1)}
            className="px-3 py-1.5 border border-gray-200 rounded-lg text-sm disabled:opacity-50 hover:bg-gray-50">
            Next
          </button>
        </div>
      )}
    </div>
  )
}
