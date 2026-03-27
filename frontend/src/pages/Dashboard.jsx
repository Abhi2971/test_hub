import { useState, useEffect } from 'react'
import { Link } from 'react-router-dom'
import { useAuth } from '../contexts/AuthContext'
import api from '../services/api'

export default function Dashboard() {
  const { user } = useAuth()
  const [stats, setStats] = useState({ exams: 0, students: 0, attempts: 0, passRate: 0 })
  const [recentExams, setRecentExams] = useState([])
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    const fetchData = async () => {
      try {
        const [examsRes] = await Promise.all([
          api.get('/exams', { params: { page: 1, limit: 5 } }),
        ])
        setRecentExams(examsRes.data.data?.items || [])
      } catch {
      } finally {
        setLoading(false)
      }
    }
    fetchData()
  }, [])

  const statCards = [
    { label: 'Total Exams', value: stats.exams, icon: 'M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2', color: 'bg-blue-50 text-blue-600' },
    { label: 'Students', value: stats.students, icon: 'M12 4.354a4 4 0 110 5.292M15 21H3v-1a6 6 0 0112 0v1zm0 0h6v-1a6 6 0 00-9-5.197M13 7a4 4 0 11-8 0 4 4 0 018 0z', color: 'bg-green-50 text-green-600' },
    { label: 'Attempts', value: stats.attempts, icon: 'M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2m-6 9l2 2 4-4', color: 'bg-purple-50 text-purple-600' },
    { label: 'Pass Rate', value: `${stats.passRate}%`, icon: 'M13 7h8m0 0v8m0-8l-8 8-4-4-6 6', color: 'bg-amber-50 text-amber-600' },
  ]

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">
            Welcome back, {user?.first_name}!
          </h1>
          <p className="text-gray-500 mt-1">Here's what's happening with your exams</p>
        </div>
        <Link
          to="/exams/create"
          className="inline-flex items-center gap-2 px-4 py-2.5 bg-primary text-white rounded-lg font-medium hover:bg-primary-dark transition"
        >
          <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 4v16m8-8H4" />
          </svg>
          New Exam
        </Link>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        {statCards.map((card, i) => (
          <div key={i} className="bg-white rounded-xl border border-gray-200 p-5">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-gray-500">{card.label}</p>
                <p className="text-2xl font-bold text-gray-900 mt-1">{loading ? '-' : card.value}</p>
              </div>
              <div className={`w-12 h-12 rounded-lg flex items-center justify-center ${card.color}`}>
                <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d={card.icon} />
                </svg>
              </div>
            </div>
          </div>
        ))}
      </div>

      <div className="bg-white rounded-xl border border-gray-200">
        <div className="px-6 py-4 border-b border-gray-200 flex items-center justify-between">
          <h3 className="font-semibold text-gray-900">Recent Exams</h3>
          <Link to="/exams" className="text-sm text-primary hover:underline">View all</Link>
        </div>
        <div className="divide-y divide-gray-100">
          {loading ? (
            <div className="p-6 text-center text-gray-400">Loading...</div>
          ) : recentExams.length === 0 ? (
            <div className="p-6 text-center">
              <p className="text-gray-400 mb-3">No exams yet</p>
              <Link to="/exams/create" className="text-sm text-primary hover:underline">Create your first exam</Link>
            </div>
          ) : (
            recentExams.map((exam) => (
              <Link key={exam.id} to={`/exams/${exam.id}`} className="flex items-center justify-between px-6 py-4 hover:bg-gray-50 transition">
                <div>
                  <p className="font-medium text-gray-900">{exam.title}</p>
                  <p className="text-sm text-gray-500 mt-0.5">{exam.total_marks} marks · {exam.question_count || 0} questions</p>
                </div>
                <span className={`px-2.5 py-1 rounded-full text-xs font-medium ${
                  exam.status === 'active' ? 'bg-green-100 text-green-700' :
                  exam.status === 'draft' ? 'bg-gray-100 text-gray-600' :
                  exam.status === 'published' ? 'bg-blue-100 text-blue-700' :
                  'bg-gray-100 text-gray-500'
                }`}>
                  {exam.status}
                </span>
              </Link>
            ))
          )}
        </div>
      </div>
    </div>
  )
}
