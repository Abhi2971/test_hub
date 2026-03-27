import { useState, useEffect } from 'react'
import { useNavigate, useParams } from 'react-router-dom'
import { useAuth } from '../../contexts/AuthContext'
import { useToast } from '../../contexts/ToastContext'
import { attemptService } from '../../services/attemptService'
import { examService } from '../../services/examService'
import Button from '../../components/ui/Button'
import Card from '../../components/ui/Card'
import Badge from '../../components/ui/Badge'
import Modal from '../../components/ui/Modal'
import Loader from '../../components/ui/Loader'
import { RefreshCw, AlertTriangle, CheckCircle, XCircle, Clock, User, Eye, PlayCircle } from 'lucide-react'

export default function LiveMonitor() {
  const navigate = useNavigate()
  const { examId } = useParams()
  const { user } = useAuth()
  const { showToast } = useToast()
  const [exam, setExam] = useState(null)
  const [attempts, setAttempts] = useState([])
  const [loading, setLoading] = useState(true)
  const [polling, setPolling] = useState(null)
  const [countdown, setCountdown] = useState(5)
  const [forceSubmitModal, setForceSubmitModal] = useState(null)
  const [allowReattemptModal, setAllowReattemptModal] = useState(null)

  useEffect(() => {
    if (user?.role !== 'teacher') {
      navigate('/dashboard')
      return
    }
    fetchExam()
    startPolling()
    return () => {
      if (polling) clearInterval(polling)
    }
  }, [user, examId])

  useEffect(() => {
    const timer = setInterval(() => {
      setCountdown(prev => prev > 0 ? prev - 1 : 5)
    }, 1000)
    return () => clearInterval(timer)
  }, [])

  const fetchExam = async () => {
    try {
      const response = await examService.getExam(examId)
      setExam(response.data.data)
    } catch (error) {
      showToast('Failed to load exam', 'error')
    }
  }

  const fetchLiveAttempts = async () => {
    try {
      const response = await attemptService.getLiveAttempts(examId)
      setAttempts(response.data.data || [])
    } catch (error) {
      console.error('Failed to fetch live attempts', error)
    }
  }

  const startPolling = () => {
    fetchLiveAttempts()
    setLoading(false)
    const poll = setInterval(() => {
      fetchLiveAttempts()
    }, 5000)
    setPolling(poll)
  }

  const handleForceSubmit = async (attemptId) => {
    try {
      await attemptService.submitAttempt(attemptId)
      showToast('Attempt submitted', 'success')
      setForceSubmitModal(null)
      fetchLiveAttempts()
    } catch (error) {
      showToast('Failed to submit attempt', 'error')
    }
  }

  const handleAllowReattempt = async (attemptId) => {
    try {
      await attemptService.allowReattempt(attemptId)
      showToast('Re-attempt allowed', 'success')
      setAllowReattemptModal(null)
      fetchLiveAttempts()
    } catch (error) {
      showToast('Failed to allow re-attempt', 'error')
    }
  }

  const activeCount = attempts.filter(a => a.status === 'in_progress').length
  const submittedCount = attempts.filter(a => a.status === 'submitted').length
  const violationCount = attempts.filter(a => a.violations >= (exam?.tab_switch_limit || 5) - 1).length

  const getRowClass = (attempt) => {
    if (attempt.status === 'submitted') return 'bg-gray-50'
    if (attempt.violations >= (exam?.tab_switch_limit || 5) - 1) return 'bg-red-50'
    if (attempt.violations > 0) return 'bg-amber-50'
    return ''
  }

  const getStatusBadge = (attempt) => {
    if (attempt.status === 'submitted') {
      return attempt.auto_submitted ? (
        <Badge variant="warning">Auto-submitted</Badge>
      ) : (
        <Badge variant="success">Submitted</Badge>
      )
    }
    if (attempt.violations >= (exam?.tab_switch_limit || 5) - 1) {
      return <Badge variant="danger">Near Limit</Badge>
    }
    return <Badge variant="info">Active</Badge>
  }

  const formatTime = (seconds) => {
    const mins = Math.floor(seconds / 60)
    const secs = seconds % 60
    return `${mins}:${secs.toString().padStart(2, '0')}`
  }

  if (loading) {
    return <Loader text="Loading monitor..." />
  }

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">Live Monitor</h1>
          <p className="text-gray-500 mt-1">{exam?.title}</p>
        </div>
        <div className="flex items-center gap-4">
          <div className="flex items-center gap-2 text-sm text-gray-600">
            <RefreshCw size={16} className="animate-spin" />
            Refreshing in {countdown}s
          </div>
          <Button variant="secondary" onClick={fetchLiveAttempts} leftIcon={<RefreshCw size={16} />}>
            Refresh
          </Button>
        </div>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <Card className="p-4">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 bg-blue-100 rounded-lg flex items-center justify-center">
              <PlayCircle className="text-blue-600" size={20} />
            </div>
            <div>
              <p className="text-2xl font-bold text-gray-900">{activeCount}</p>
              <p className="text-sm text-gray-500">Active</p>
            </div>
          </div>
        </Card>
        <Card className="p-4">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 bg-green-100 rounded-lg flex items-center justify-center">
              <CheckCircle className="text-green-600" size={20} />
            </div>
            <div>
              <p className="text-2xl font-bold text-gray-900">{submittedCount}</p>
              <p className="text-sm text-gray-500">Submitted</p>
            </div>
          </div>
        </Card>
        <Card className="p-4">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 bg-red-100 rounded-lg flex items-center justify-center">
              <AlertTriangle className="text-red-600" size={20} />
            </div>
            <div>
              <p className="text-2xl font-bold text-gray-900">{violationCount}</p>
              <p className="text-sm text-gray-500">Near Violation</p>
            </div>
          </div>
        </Card>
        <Card className="p-4">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 bg-purple-100 rounded-lg flex items-center justify-center">
              <User className="text-purple-600" size={20} />
            </div>
            <div>
              <p className="text-2xl font-bold text-gray-900">{attempts.length}</p>
              <p className="text-sm text-gray-500">Total</p>
            </div>
          </div>
        </Card>
      </div>

      <Card>
        <div className="overflow-x-auto">
          <table className="w-full">
            <thead className="bg-gray-50 border-b border-gray-200">
              <tr>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Student</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Started</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Progress</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Tab Switches</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Status</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Actions</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-gray-100">
              {attempts.length === 0 ? (
                <tr>
                  <td colSpan={6} className="px-6 py-8 text-center text-gray-500">
                    No active attempts
                  </td>
                </tr>
              ) : (
                attempts.map((attempt) => (
                  <tr key={attempt.id} className={getRowClass(attempt)}>
                    <td className="px-6 py-4">
                      <div className="flex items-center gap-3">
                        <div className="w-8 h-8 rounded-full bg-gray-200 flex items-center justify-center">
                          <User size={14} className="text-gray-500" />
                        </div>
                        <div>
                          <p className="font-medium text-gray-900">
                            {attempt.student?.first_name} {attempt.student?.last_name}
                          </p>
                          <p className="text-xs text-gray-500">{attempt.student?.email}</p>
                        </div>
                      </div>
                    </td>
                    <td className="px-6 py-4 text-sm text-gray-600">
                      {attempt.started_at ? new Date(attempt.started_at).toLocaleTimeString() : '-'}
                    </td>
                    <td className="px-6 py-4">
                      <div className="flex items-center gap-2">
                        <span className="text-sm text-gray-600">
                          {attempt.answered || 0}/{attempt.total_questions || 0}
                        </span>
                        <div className="w-20 bg-gray-200 rounded-full h-2">
                          <div
                            className="bg-blue-600 h-2 rounded-full"
                            style={{
                              width: `${((attempt.answered || 0) / (attempt.total_questions || 1)) * 100}%`
                            }}
                          />
                        </div>
                      </div>
                    </td>
                    <td className="px-6 py-4">
                      <div className="flex items-center gap-1">
                        {attempt.violations > 0 && <AlertTriangle size={14} className="text-amber-500" />}
                        <span className={`font-medium ${
                          attempt.violations >= (exam?.tab_switch_limit || 5) - 1 ? 'text-red-600' : 'text-gray-900'
                        }`}>
                          {attempt.violations || 0}
                        </span>
                        <span className="text-gray-400">/ {exam?.tab_switch_limit || 5}</span>
                      </div>
                    </td>
                    <td className="px-6 py-4">
                      {getStatusBadge(attempt)}
                    </td>
                    <td className="px-6 py-4">
                      {attempt.status === 'in_progress' && (
                        <Button
                          size="sm"
                          variant="danger"
                          onClick={() => setForceSubmitModal(attempt)}
                        >
                          Force Submit
                        </Button>
                      )}
                      {attempt.status === 'submitted' && attempt.auto_submitted && (
                        <Button
                          size="sm"
                          variant="secondary"
                          onClick={() => setAllowReattemptModal(attempt)}
                        >
                          Allow Re-attempt
                        </Button>
                      )}
                      <Button
                        size="sm"
                        variant="ghost"
                        onClick={() => navigate(`/dashboard/teacher/attempts/${attempt.id}`)}
                        leftIcon={<Eye size={14} />}
                      >
                        View
                      </Button>
                    </td>
                  </tr>
                ))
              )}
            </tbody>
          </table>
        </div>
      </Card>

      <Modal
        isOpen={!!forceSubmitModal}
        onClose={() => setForceSubmitModal(null)}
        title="Force Submit"
        footer={
          <div className="flex gap-3">
            <Button variant="secondary" onClick={() => setForceSubmitModal(null)}>Cancel</Button>
            <Button variant="danger" onClick={() => handleForceSubmit(forceSubmitModal.id)}>Submit</Button>
          </div>
        }
      >
        <p>Are you sure you want to force submit this attempt?</p>
        <p className="text-sm text-gray-500 mt-2">
          Student: {forceSubmitModal?.student?.first_name} {forceSubmitModal?.student?.last_name}
        </p>
      </Modal>

      <Modal
        isOpen={!!allowReattemptModal}
        onClose={() => setAllowReattemptModal(null)}
        title="Allow Re-attempt"
        footer={
          <div className="flex gap-3">
            <Button variant="secondary" onClick={() => setAllowReattemptModal(null)}>Cancel</Button>
            <Button onClick={() => handleAllowReattempt(allowReattemptModal.id)}>Allow</Button>
          </div>
        }
      >
        <p>Allow this student to attempt the exam again?</p>
        <p className="text-sm text-gray-500 mt-2">
          Student: {allowReattemptModal?.student?.first_name} {allowReattemptModal?.student?.last_name}
        </p>
      </Modal>
    </div>
  )
}