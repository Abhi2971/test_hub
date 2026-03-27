import { useState, useEffect } from 'react'
import { useNavigate } from 'react-router-dom'
import { useAuth } from '../../contexts/AuthContext'
import { useToast } from '../../contexts/ToastContext'
import { examService } from '../../services/examService'
import Button from '../../components/ui/Button'
import Card from '../../components/ui/Card'
import Badge from '../../components/ui/Badge'
import Loader from '../../components/ui/Loader'
import { Clock, FileText, Play, Lock, Calendar } from 'lucide-react'

export default function AvailableExams() {
  const navigate = useNavigate()
  const { user } = useAuth()
  const { showToast } = useToast()
  const [exams, setExams] = useState([])
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    if (user?.role !== 'student_registered' && user?.role !== 'student_assigned') {
      navigate('/dashboard')
      return
    }
    fetchAvailableExams()
  }, [user])

  const fetchAvailableExams = async () => {
    try {
      setLoading(true)
      const response = await examService.getExams({ status: 'active', limit: 50 })
      setExams(response.data?.items || [])
    } catch (error) {
      showToast('Failed to load exams', 'error')
    } finally {
      setLoading(false)
    }
  }

  const isExamAvailable = (exam) => {
    const now = new Date()
    if (exam.schedule_start && new Date(exam.schedule_start) > now) return { available: false, reason: 'Upcoming' }
    if (exam.schedule_end && new Date(exam.schedule_end) < now) return { available: false, reason: 'Expired' }
    return { available: true }
  }

  const handleStartExam = async (examId) => {
    try {
      const response = await examService.generateMagicLink(examId)
      navigate(`/exam/${examId}/start?token=${response.data.data.token}`)
    } catch (error) {
      showToast('Failed to start exam', 'error')
    }
  }

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold text-gray-900">Available Exams</h1>
        <p className="text-gray-500 mt-1">Exams assigned to you</p>
      </div>

      {loading ? (
        <div className="flex justify-center py-12">
          <Loader />
        </div>
      ) : exams.length === 0 ? (
        <Card>
          <div className="p-12 text-center">
            <FileText className="mx-auto text-gray-300 mb-4" size={48} />
            <p className="text-gray-500">No exams available</p>
          </div>
        </Card>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {exams.map((exam) => {
            const { available, reason } = isExamAvailable(exam)
            return (
              <Card key={exam.id} className="hover:shadow-lg transition-shadow">
                <div className="p-5">
                  <div className="flex items-start justify-between">
                    <div>
                      <h3 className="font-semibold text-gray-900">{exam.title}</h3>
                      <p className="text-sm text-gray-500 mt-1">{exam.subject}</p>
                    </div>
                    {available ? (
                      <Badge variant="success">Available</Badge>
                    ) : (
                      <Badge variant="neutral">
                        <Lock size={12} className="mr-1" />
                        {reason}
                      </Badge>
                    )}
                  </div>

                  <div className="mt-4 grid grid-cols-2 gap-4 text-sm">
                    <div className="flex items-center gap-2 text-gray-600">
                      <Clock size={14} />
                      <span>{exam.duration} min</span>
                    </div>
                    <div className="flex items-center gap-2 text-gray-600">
                      <FileText size={14} />
                      <span>{exam.question_count || 0} questions</span>
                    </div>
                    <div className="flex items-center gap-2 text-gray-600">
                      <span>Marks: {exam.total_marks}</span>
                    </div>
                    {exam.schedule_end && (
                      <div className="flex items-center gap-2 text-gray-600">
                        <Calendar size={14} />
                        <span>Due: {new Date(exam.schedule_end).toLocaleDateString()}</span>
                      </div>
                    )}
                  </div>

                  <div className="mt-4 pt-4 border-t border-gray-100">
                    {available ? (
                      <Button
                        className="w-full"
                        leftIcon={<Play size={18} />}
                        onClick={() => handleStartExam(exam.id)}
                      >
                        Start Exam
                      </Button>
                    ) : (
                      <Button variant="secondary" className="w-full" disabled leftIcon={<Lock size={18} />}>
                        {reason}
                      </Button>
                    )}
                  </div>
                </div>
              </Card>
            )
          })}
        </div>
      )}
    </div>
  )
}