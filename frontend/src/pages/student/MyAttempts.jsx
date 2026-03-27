import { useState, useEffect } from 'react'
import { useNavigate } from 'react-router-dom'
import { useAuth } from '../../contexts/AuthContext'
import { useToast } from '../../contexts/ToastContext'
import { resultService } from '../../services/resultService'
import Button from '../../components/ui/Button'
import Card from '../../components/ui/Card'
import Badge from '../../components/ui/Badge'
import Pagination from '../../components/ui/Pagination'
import Loader from '../../components/ui/Loader'
import { Eye, Clock, CheckCircle, AlertCircle } from 'lucide-react'

export default function MyAttempts() {
  const navigate = useNavigate()
  const { user } = useAuth()
  const { showToast } = useToast()
  const [attempts, setAttempts] = useState([])
  const [loading, setLoading] = useState(true)
  const [pagination, setPagination] = useState({ page: 1, limit: 20, total: 0 })

  useEffect(() => {
    if (user?.role !== 'student_registered' && user?.role !== 'student_assigned') {
      navigate('/dashboard')
      return
    }
    fetchAttempts()
  }, [user, pagination.page])

  const fetchAttempts = async () => {
    try {
      setLoading(true)
      const response = await resultService.getResults({ page: pagination.page, limit: pagination.limit })
      setAttempts(response.data.data?.items || [])
      setPagination(prev => ({ ...prev, total: response.data.data?.total || 0 }))
    } catch (error) {
      showToast('Failed to load attempts', 'error')
    } finally {
      setLoading(false)
    }
  }

  const getStatusBadge = (attempt) => {
    if (attempt.status === 'submitted') {
      return <Badge variant="success">Submitted</Badge>
    }
    if (attempt.status === 'auto_submitted') {
      return <Badge variant="warning">Auto-submitted</Badge>
    }
    return <Badge variant="info">In Progress</Badge>
  }

  const getGrade = (percentage) => {
    if (percentage >= 90) return 'S'
    if (percentage >= 80) return 'A'
    if (percentage >= 70) return 'B'
    if (percentage >= 60) return 'C'
    if (percentage >= 50) return 'D'
    return 'F'
  }

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold text-gray-900">My Attempts</h1>
        <p className="text-gray-500 mt-1">View your exam attempts and results</p>
      </div>

      {loading ? (
        <div className="flex justify-center py-12">
          <Loader />
        </div>
      ) : attempts.length === 0 ? (
        <Card>
          <div className="p-12 text-center">
            <Clock className="mx-auto text-gray-300 mb-4" size={48} />
            <p className="text-gray-500">No exam attempts yet</p>
          </div>
        </Card>
      ) : (
        <Card>
          <div className="overflow-x-auto">
            <table className="w-full">
              <thead className="bg-gray-50 border-b border-gray-200">
                <tr>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Exam</th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Score</th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Percentage</th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Grade</th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Status</th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Completed</th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Actions</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-gray-100">
                {attempts.map((attempt) => {
                  const percentage = attempt.percentage || ((attempt.score / attempt.total_marks) * 100)
                  const passed = percentage >= 35

                  return (
                    <tr key={attempt.id} className="hover:bg-gray-50">
                      <td className="px-6 py-4">
                        <div>
                          <p className="font-medium text-gray-900">{attempt.exam?.title || 'Exam'}</p>
                          <p className="text-xs text-gray-500">{attempt.exam?.subject}</p>
                        </div>
                      </td>
                      <td className="px-6 py-4 text-gray-900">
                        {attempt.score} / {attempt.total_marks || 100}
                      </td>
                      <td className="px-6 py-4 text-gray-900">
                        {percentage.toFixed(1)}%
                      </td>
                      <td className="px-6 py-4">
                        <span className={`inline-flex items-center justify-center w-8 h-8 rounded-full font-bold text-sm ${
                          passed ? 'bg-green-100 text-green-700' : 'bg-red-100 text-red-700'
                        }`}>
                          {getGrade(percentage)}
                        </span>
                      </td>
                      <td className="px-6 py-4">
                        {getStatusBadge(attempt)}
                      </td>
                      <td className="px-6 py-4 text-gray-600 text-sm">
                        {attempt.completed_at ? new Date(attempt.completed_at).toLocaleString() : '-'}
                      </td>
                      <td className="px-6 py-4">
                        <Button
                          size="sm"
                          variant="secondary"
                          leftIcon={<Eye size={14} />}
                          onClick={() => navigate(`/dashboard/student/results/${attempt.id}`)}
                        >
                          View
                        </Button>
                      </td>
                    </tr>
                  )
                })}
              </tbody>
            </table>
          </div>

          <div className="p-4 border-t border-gray-200">
            <Pagination
              page={pagination.page}
              totalPages={Math.ceil(pagination.total / pagination.limit)}
              onPageChange={(page) => setPagination(prev => ({ ...prev, page }))}
              perPage={pagination.limit}
              onPerPageChange={(limit) => setPagination(prev => ({ ...prev, limit, page: 1 }))}
              total={pagination.total}
            />
          </div>
        </Card>
      )}
    </div>
  )
}