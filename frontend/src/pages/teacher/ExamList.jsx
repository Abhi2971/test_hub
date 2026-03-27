import { useState, useEffect } from 'react'
import { useNavigate } from 'react-router-dom'
import { useAuth } from '../../contexts/AuthContext'
import { useToast } from '../../contexts/ToastContext'
import { examService } from '../../services/examService'
import Button from '../../components/ui/Button'
import Card from '../../components/ui/Card'
import Badge from '../../components/ui/Badge'
import Loader from '../../components/ui/Loader'
import { Plus, Edit, Eye, BarChart3, Users } from 'lucide-react'

const statusColors = {
  draft: 'gray',
  published: 'blue',
  active: 'green',
  closed: 'red'
}

export default function ExamList() {
  const navigate = useNavigate()
  const { user } = useAuth()
  const { showToast } = useToast()
  const [exams, setExams] = useState([])
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    if (user?.role !== 'teacher') {
      navigate('/dashboard')
      return
    }
    fetchExams()
  }, [user])

  const fetchExams = async () => {
    try {
      setLoading(true)
      const response = await examService.getExams({ limit: 50 })
      setExams(response.data?.items || [])
    } catch (error) {
      showToast('Failed to load exams', 'error')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">My Exams</h1>
          <p className="text-gray-500 mt-1">Manage your created exams</p>
        </div>
        <Button leftIcon={<Plus size={18} />} onClick={() => navigate('/dashboard/teacher/exams/create')}>
          Create Exam
        </Button>
      </div>

      {loading ? (
        <div className="flex justify-center py-12">
          <Loader />
        </div>
      ) : exams.length === 0 ? (
        <Card>
          <div className="p-12 text-center">
            <p className="text-gray-500 mb-4">No exams created yet</p>
            <Button onClick={() => navigate('/dashboard/teacher/exams/create')}>
              Create Your First Exam
            </Button>
          </div>
        </Card>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {exams.map((exam) => (
            <Card key={exam.id} className="hover:shadow-lg transition-shadow">
              <div className="p-5">
                <div className="flex items-start justify-between">
                  <div>
                    <h3 className="font-semibold text-gray-900">{exam.title}</h3>
                    <p className="text-sm text-gray-500 mt-1">{exam.subject}</p>
                  </div>
                  <Badge variant={statusColors[exam.status] || 'neutral'}>
                    {exam.status}
                  </Badge>
                </div>

                <div className="grid grid-cols-3 gap-4 mt-4 text-center">
                  <div>
                    <p className="text-lg font-semibold text-gray-900">{exam.question_count || 0}</p>
                    <p className="text-xs text-gray-500">Questions</p>
                  </div>
                  <div>
                    <p className="text-lg font-semibold text-gray-900">{exam.attempts_count || 0}</p>
                    <p className="text-xs text-gray-500">Attempts</p>
                  </div>
                  <div>
                    <p className="text-lg font-semibold text-gray-900">
                      {exam.avg_score ? exam.avg_score.toFixed(0) + '%' : '-'}
                    </p>
                    <p className="text-xs text-gray-500">Avg Score</p>
                  </div>
                </div>

                <div className="flex gap-2 mt-4 pt-4 border-t border-gray-100">
                  {exam.status === 'draft' && (
                    <Button
                      variant="secondary"
                      size="sm"
                      className="flex-1"
                      leftIcon={<Edit size={14} />}
                      onClick={() => navigate(`/dashboard/teacher/exams/${exam.id}/edit`)}
                    >
                      Edit
                    </Button>
                  )}
                  <Button
                    variant="secondary"
                    size="sm"
                    className="flex-1"
                    leftIcon={<Eye size={14} />}
                    onClick={() => navigate(`/dashboard/teacher/exams/${exam.id}`)}
                  >
                    View
                  </Button>
                  <Button
                    variant="secondary"
                    size="sm"
                    className="flex-1"
                    leftIcon={<BarChart3 size={14} />}
                    onClick={() => navigate(`/dashboard/teacher/exams/${exam.id}/results`)}
                  >
                    Results
                  </Button>
                  {exam.status === 'published' && (
                    <Button
                      size="sm"
                      className="flex-1"
                      leftIcon={<Users size={14} />}
                      onClick={() => navigate(`/dashboard/teacher/exams/${exam.id}/monitor`)}
                    >
                      Monitor
                    </Button>
                  )}
                </div>
              </div>
            </Card>
          ))}
        </div>
      )}
    </div>
  )
}