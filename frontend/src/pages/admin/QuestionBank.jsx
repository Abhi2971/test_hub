import { useState, useEffect } from 'react'
import { useNavigate } from 'react-router-dom'
import { useAuth } from '../../contexts/AuthContext'
import { useToast } from '../../contexts/ToastContext'
import api from '../../services/api'
import Button from '../../components/ui/Button'
import Card from '../../components/ui/Card'
import Badge from '../../components/ui/Badge'
import Select from '../../components/ui/Select'
import Input from '../../components/ui/Input'
import Pagination from '../../components/ui/Pagination'
import Loader from '../../components/ui/Loader'
import { Search, Check, X, Plus, Brain } from 'lucide-react'

const difficultyColors = {
  easy: 'success',
  medium: 'warning',
  hard: 'danger'
}

export default function QuestionBank() {
  const navigate = useNavigate()
  const { user } = useAuth()
  const { showToast } = useToast()
  const [questions, setQuestions] = useState([])
  const [loading, setLoading] = useState(true)
  const [pagination, setPagination] = useState({ page: 1, limit: 20, total: 0 })
  const [filters, setFilters] = useState({
    topic: '',
    difficulty: '',
    source: '',
    reviewed: ''
  })
  const [searchQuery, setSearchQuery] = useState('')

  useEffect(() => {
    if (!['admin_college', 'admin_public', 'super_admin', 'teacher'].includes(user?.role)) {
      navigate('/dashboard')
      return
    }
    fetchQuestions()
  }, [user, pagination.page, pagination.limit, filters])

  const fetchQuestions = async () => {
    try {
      setLoading(true)
      const params = {
        page: pagination.page,
        limit: pagination.limit,
        ...(filters.topic && { topic: filters.topic }),
        ...(filters.difficulty && { difficulty: filters.difficulty }),
        ...(filters.source && { source: filters.source }),
        ...(filters.reviewed && { reviewed: filters.reviewed }),
        ...(searchQuery && { search: searchQuery })
      }
      const response = await api.get('/questions', { params })
      setQuestions(response.data.data?.items || [])
      setPagination(prev => ({
        ...prev,
        total: response.data.data?.total || 0
      }))
    } catch (error) {
      showToast('Failed to load questions', 'error')
    } finally {
      setLoading(false)
    }
  }

  const handleApprove = async (questionId) => {
    try {
      await api.patch(`/questions/${questionId}`, { reviewed: true, status: 'approved' })
      showToast('Question approved', 'success')
      fetchQuestions()
    } catch (error) {
      showToast('Failed to approve question', 'error')
    }
  }

  const handleReject = async (questionId) => {
    try {
      await api.patch(`/questions/${questionId}`, { reviewed: true, status: 'rejected' })
      showToast('Question rejected', 'success')
      fetchQuestions()
    } catch (error) {
      showToast('Failed to reject question', 'error')
    }
  }

  const handleBulkApprove = async (questionIds) => {
    try {
      await api.post('/questions/bulk-approve', { question_ids: questionIds })
      showToast(`${questionIds.length} questions approved`, 'success')
      fetchQuestions()
    } catch (error) {
      showToast('Failed to approve questions', 'error')
    }
  }

  const handleBulkReject = async (questionIds) => {
    try {
      await api.post('/questions/bulk-reject', { question_ids: questionIds })
      showToast(`${questionIds.length} questions rejected`, 'success')
      fetchQuestions()
    } catch (error) {
      showToast('Failed to reject questions', 'error')
    }
  }

  const [selectedQuestions, setSelectedQuestions] = useState([])

  const toggleSelect = (questionId) => {
    setSelectedQuestions(prev =>
      prev.includes(questionId)
        ? prev.filter(id => id !== questionId)
        : [...prev, questionId]
    )
  }

  const selectAll = () => {
    if (selectedQuestions.length === questions.length) {
      setSelectedQuestions([])
    } else {
      setSelectedQuestions(questions.map(q => q.id))
    }
  }

  const topicOptions = [
    { value: '', label: 'All Topics' },
    { value: 'math', label: 'Mathematics' },
    { value: 'science', label: 'Science' },
    { value: 'english', label: 'English' },
    { value: 'history', label: 'History' },
    { value: 'geography', label: 'Geography' }
  ]

  const difficultyOptions = [
    { value: '', label: 'All Difficulties' },
    { value: 'easy', label: 'Easy' },
    { value: 'medium', label: 'Medium' },
    { value: 'hard', label: 'Hard' }
  ]

  const sourceOptions = [
    { value: '', label: 'All Sources' },
    { value: 'manual', label: 'Manual' },
    { value: 'ai', label: 'AI Generated' }
  ]

  const reviewedOptions = [
    { value: '', label: 'All Status' },
    { value: 'pending', label: 'Pending Review' },
    { value: 'reviewed', label: 'Reviewed' }
  ]

  const aiQuestions = questions.filter(q => q.ai_generated && !q.reviewed)

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">Question Bank</h1>
          <p className="text-gray-500 mt-1">Manage and review questions</p>
        </div>
        <Button leftIcon={<Plus size={18} />} onClick={() => navigate('/dashboard/admin/questions/create')}>
          Add Question
        </Button>
      </div>

      {aiQuestions.length > 0 && (
        <Card className="bg-purple-50 border-purple-200">
          <div className="p-4 flex items-center justify-between">
            <div className="flex items-center gap-3">
              <Brain className="text-purple-600" size={24} />
              <div>
                <p className="font-medium text-purple-900">{aiQuestions.length} AI-generated questions pending review</p>
                <p className="text-sm text-purple-700">Review and approve or reject AI-generated questions</p>
              </div>
            </div>
            <div className="flex gap-2">
              <Button size="sm" variant="success" onClick={() => handleBulkApprove(aiQuestions.map(q => q.id))}>
                Approve All
              </Button>
              <Button size="sm" variant="danger" onClick={() => handleBulkReject(aiQuestions.map(q => q.id))}>
                Reject All
              </Button>
            </div>
          </div>
        </Card>
      )}

      <Card>
        <div className="p-4 border-b border-gray-200">
          <div className="flex flex-col md:flex-row gap-4">
            <div className="flex-1 relative">
              <Search className="absolute left-3 top-1/2 -translate-y-1/2 text-gray-400" size={18} />
              <input
                type="text"
                placeholder="Search questions..."
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                onKeyDown={(e) => e.key === 'Enter' && fetchQuestions()}
                className="w-full pl-10 pr-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-200"
              />
            </div>
            <div className="flex gap-2">
              <Select options={topicOptions} value={filters.topic} onChange={(v) => setFilters(f => ({ ...f, topic: v }))} className="w-36" />
              <Select options={difficultyOptions} value={filters.difficulty} onChange={(v) => setFilters(f => ({ ...f, difficulty: v }))} className="w-36" />
              <Select options={sourceOptions} value={filters.source} onChange={(v) => setFilters(f => ({ ...f, source: v }))} className="w-36" />
              <Select options={reviewedOptions} value={filters.reviewed} onChange={(v) => setFilters(f => ({ ...f, reviewed: v }))} className="w-40" />
            </div>
          </div>
        </div>

        {selectedQuestions.length > 0 && (
          <div className="p-3 bg-blue-50 border-b border-blue-100 flex items-center justify-between">
            <span className="text-sm text-blue-700">{selectedQuestions.length} questions selected</span>
            <div className="flex gap-2">
              <Button size="sm" variant="success" onClick={() => handleBulkApprove(selectedQuestions)}>Approve Selected</Button>
              <Button size="sm" variant="danger" onClick={() => handleBulkReject(selectedQuestions)}>Reject Selected</Button>
            </div>
          </div>
        )}

        {loading ? (
          <div className="p-8 flex justify-center">
            <Loader />
          </div>
        ) : (
          <div className="overflow-x-auto">
            <table className="w-full">
              <thead className="bg-gray-50 border-b border-gray-200">
                <tr>
                  <th className="px-4 py-3 text-left">
                    <input
                      type="checkbox"
                      checked={selectedQuestions.length === questions.length && questions.length > 0}
                      onChange={selectAll}
                      className="rounded border-gray-300"
                    />
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Question</th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Topic</th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Difficulty</th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Usage</th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Source</th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Actions</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-gray-100">
                {questions.length === 0 ? (
                  <tr>
                    <td colSpan={7} className="px-6 py-8 text-center text-gray-500">
                      No questions found
                    </td>
                  </tr>
                ) : (
                  questions.map((question) => (
                    <tr key={question.id} className="hover:bg-gray-50">
                      <td className="px-4 py-4">
                        <input
                          type="checkbox"
                          checked={selectedQuestions.includes(question.id)}
                          onChange={() => toggleSelect(question.id)}
                          className="rounded border-gray-300"
                        />
                      </td>
                      <td className="px-6 py-4 max-w-md">
                        <p className="text-sm text-gray-900 line-clamp-2">{question.text}</p>
                      </td>
                      <td className="px-6 py-4 text-gray-600">{question.topic || '-'}</td>
                      <td className="px-6 py-4">
                        <Badge variant={difficultyColors[question.difficulty] || 'neutral'}>
                          {question.difficulty}
                        </Badge>
                      </td>
                      <td className="px-6 py-4 text-gray-600">{question.usage_count || 0}</td>
                      <td className="px-6 py-4">
                        {question.ai_generated ? (
                          <Badge variant="info">
                            <Brain size={12} className="mr-1" />
                            AI
                          </Badge>
                        ) : (
                          <Badge variant="neutral">Manual</Badge>
                        )}
                      </td>
                      <td className="px-6 py-4">
                        {question.ai_generated && !question.reviewed ? (
                          <div className="flex items-center gap-1">
                            <button
                              onClick={() => handleApprove(question.id)}
                              className="p-1.5 text-green-600 hover:bg-green-50 rounded"
                              title="Approve"
                            >
                              <Check size={16} />
                            </button>
                            <button
                              onClick={() => handleReject(question.id)}
                              className="p-1.5 text-red-600 hover:bg-red-50 rounded"
                              title="Reject"
                            >
                              <X size={16} />
                            </button>
                          </div>
                        ) : (
                          <span className="text-xs text-gray-400">Reviewed</span>
                        )}
                      </td>
                    </tr>
                  ))
                )}
              </tbody>
            </table>
          </div>
        )}

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
    </div>
  )
}