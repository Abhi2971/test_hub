import { useState, useEffect } from 'react'
import { Link } from 'react-router-dom'
import { resultService } from '../../services/resultService'

export default function ResultList() {
  const [results, setResults] = useState([])
  const [loading, setLoading] = useState(true)
  const [page, setPage] = useState(1)

  const fetchResults = async () => {
    setLoading(true)
    try {
      const response = await resultService.getResults({ page, limit: 20 })
      setResults(response.data?.items || [])
    } catch {}
    finally { setLoading(false) }
  }

  useEffect(() => { fetchResults() }, [page])

  return (
    <div className="space-y-5">
      <div className="bg-white rounded-xl border border-gray-200 overflow-hidden">
        <table className="w-full">
          <thead className="bg-gray-50 border-b border-gray-200">
            <tr>
              {['Student', 'Exam', 'Score', 'Grade', 'Status', 'Date', ''].map((h) => (
                <th key={h} className="text-left px-6 py-3 text-xs font-semibold text-gray-500 uppercase">{h}</th>
              ))}
            </tr>
          </thead>
          <tbody className="divide-y divide-gray-100">
            {loading ? (
              <tr><td colSpan={7} className="px-6 py-8 text-center text-gray-400">Loading...</td></tr>
            ) : results.length === 0 ? (
              <tr><td colSpan={7} className="px-6 py-8 text-center text-gray-400">No results found</td></tr>
            ) : results.map((r) => (
              <tr key={r.id} className="hover:bg-gray-50">
                <td className="px-6 py-4 text-sm font-medium text-gray-900">{r.student_name || r.student?.full_name || '-'}</td>
                <td className="px-6 py-4 text-sm text-gray-600">{r.exam_title || r.exam?.title || '-'}</td>
                <td className="px-6 py-4 text-sm text-gray-900">{r.score} / {r.total_marks}</td>
                <td className="px-6 py-4">
                  <span className={`px-2.5 py-0.5 rounded-full text-sm font-bold ${
                    r.grade === 'A+' || r.grade === 'A' ? 'bg-green-100 text-green-700' :
                    r.grade === 'B' ? 'bg-blue-100 text-blue-700' :
                    r.grade === 'C' || r.grade === 'D' ? 'bg-amber-100 text-amber-700' :
                    'bg-red-100 text-red-700'
                  }`}>{r.grade}</span>
                </td>
                <td className="px-6 py-4">
                  <span className={`px-2.5 py-0.5 rounded-full text-xs font-medium ${r.passed ? 'bg-green-100 text-green-700' : 'bg-red-100 text-red-600'}`}>
                    {r.passed ? 'Passed' : 'Failed'}
                  </span>
                </td>
                <td className="px-6 py-4 text-sm text-gray-500">{new Date(r.created_at).toLocaleDateString()}</td>
                <td className="px-6 py-4">
                  <Link to={`/results/${r.id}`} className="text-primary hover:underline text-sm">View</Link>
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
