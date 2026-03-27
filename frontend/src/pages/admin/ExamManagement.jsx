import { useState, useEffect } from 'react'
import { useNavigate } from 'react-router-dom'
import { useAuth } from '../../contexts/AuthContext'
import { useToast } from '../../contexts/ToastContext'
import { examService } from '../../services/examService'
import Button from '../../components/ui/Button'
import Card from '../../components/ui/Card'
import Badge from '../../components/ui/Badge'
import Select from '../../components/ui/Select'
import Pagination from '../../components/ui/Pagination'
import Loader from '../../components/ui/Loader'
import { Plus, Eye, Check, X, Archive, BarChart3, Edit, CheckCircle, Users } from 'lucide-react'

const statusColors = {
  draft: 'gray',
  pending: 'warning',
  published: 'blue',
  active: 'success',
  closed: 'danger',
  rejected: 'danger'
}

export default function ExamManagement() {
  const navigate = useNavigate()
  const { user } = useAuth()
  const { showToast } = useToast()
  const [exams, setExams] = useState([])
  const [loading, setLoading] = useState(true)
  const [pagination, setPagination] = useState({ page: 1, limit: 10, total: 0 })
  const [statusFilter, setStatusFilter] = useState('all')
  const [selectedExam, setSelectedExam] = useState(null)
  const [examResults, setExamResults] = useState(null)
  const [resultsLoading, setResultsLoading] = useState(false)
  const [activeTab, setActiveTab] = useState('all')

  useEffect(() => {
    if (!['admin_college', 'admin_public', 'super_admin'].includes(user?.role)) {
      navigate('/dashboard')
      return
    }
    fetchExams()
  }, [user, pagination.page, pagination.limit, statusFilter, activeTab])

  useEffect(() => {
    const fetchResults = async () => {
      if (selectedExam) {
        setResultsLoading(true)
        try {
          const response = await examService.getExamResults(selectedExam.id)
          setExamResults(response?.data || response || {})
        } catch (error) {
          console.error('Failed to load exam results:', error)
          setExamResults({})
        } finally {
          setResultsLoading(false)
        }
      }
    }
    fetchResults()
  }, [selectedExam])

  const fetchExams = async () => {
    try {
      setLoading(true)
      const params = {
        page: pagination.page,
        limit: pagination.limit,
        status: statusFilter !== 'all' ? statusFilter : undefined,
        exam_type: activeTab !== 'all' ? activeTab : undefined
      }
      const response = await examService.getExams(params)
      setExams(response?.data?.items || response?.items || [])
      setPagination(prev => ({
        ...prev,
        total: response?.data?.total || response?.total || 0
      }))
    } catch (error) {
      showToast('Failed to load exams', 'error')
    } finally {
      setLoading(false)
    }
  }

  const handleApprove = async (examId) => {
    try {
      await examService.approveExam(examId)
      showToast('Exam approved', 'success')
      fetchExams()
    } catch (error) {
      showToast('Failed to approve exam', 'error')
    }
  }

  const handleReject = async (examId) => {
    if (!confirm('Are you sure you want to reject this exam?')) return
    try {
      await examService.rejectExam(examId)
      showToast('Exam rejected', 'success')
      fetchExams()
    } catch (error) {
      showToast('Failed to reject exam', 'error')
    }
  }

  const handleArchive = async (examId) => {
    try {
      await examService.closeExam(examId)
      showToast('Exam archived', 'success')
      fetchExams()
    } catch (error) {
      showToast('Failed to archive exam', 'error')
    }
  }

  const statusOptions = [
    { value: 'all', label: 'All Status' },
    { value: 'pending', label: 'Pending' },
    { value: 'published', label: 'Published' },
    { value: 'active', label: 'Active' },
    { value: 'closed', label: 'Closed' },
    { value: 'draft', label: 'Draft' }
  ]

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">
            {user?.role === 'super_admin' ? 'All Exams' : 'Exam Management'}
          </h1>
          <p className="text-gray-500 mt-1">
            {user?.role === 'super_admin'
              ? 'View all exams across institutes'
              : 'Manage all exams in your institute'}
          </p>
        </div>
        {user?.role !== 'super_admin' && (
          <Button leftIcon={<Plus size={18} />} onClick={() => navigate('/dashboard/admin/exams/create')}>
            Create Exam
          </Button>
        )}
      </div>

      {/* Tabs for filtering by exam type */}
      {user?.role === 'super_admin' && (
        <div className="border-b border-gray-200">
          <nav className="flex gap-8">
            {[
              { key: 'all', label: 'All Exams' },
              { key: 'public', label: 'Platform Admin Exams' },
              { key: 'institute', label: 'College Admin Exams' }
            ].map(({ key, label }) => (
              <button
                key={key}
                onClick={() => { setActiveTab(key); setPagination(p => ({ ...p, page: 1 })) }}
                className={`pb-3 text-sm font-medium border-b-2 transition-colors ${activeTab === key
                    ? 'border-blue-500 text-blue-600'
                    : 'border-transparent text-gray-500 hover:text-gray-700'
                  }`}
              >
                {label}
              </button>
            ))}
          </nav>
        </div>
      )}

      <Card>
        <div className="p-4 border-b border-gray-200">
          <div className="flex justify-end">
            <Select
              options={statusOptions}
              value={statusFilter}
              onChange={setStatusFilter}
              className="w-40"
            />
          </div>
        </div>

        {loading ? (
          <div className="p-8 flex justify-center">
            <Loader />
          </div>
        ) : (
          <div className="overflow-x-auto">
            <table className="w-full">
              <thead className="bg-gray-50 border-b border-gray-200">
                <tr>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Title</th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Type</th>
                  {user?.role === 'super_admin' && (
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Created By</th>
                  )}
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Questions</th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Duration</th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Status</th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Attempts</th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Actions</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-gray-100">
                {exams.length === 0 ? (
                  <tr>
                    <td colSpan={user?.role === 'super_admin' ? 8 : 7} className="px-6 py-8 text-center text-gray-500">
                      No exams found
                    </td>
                  </tr>
                ) : (
                  exams.map((exam) => (
                    <tr key={exam.id} className="hover:bg-gray-50 cursor-pointer" onClick={() => setSelectedExam(exam)}>
                      <td className="px-6 py-4">
                        <div className="font-medium text-gray-900">{exam.title}</div>
                        <div className="text-xs text-gray-500 mt-0.5">{exam.subject}</div>
                      </td>
                      <td className="px-6 py-4 text-gray-600">
                        <Badge variant="neutral" size="sm">{exam.exam_type || 'Standard'}</Badge>
                      </td>
                      {user?.role === 'super_admin' && (
                        <td className="px-6 py-4 text-gray-600">
                          <Badge
                            variant={exam.exam_type === 'public' ? 'primary' : 'secondary'}
                            size="sm"
                          >
                            {exam.exam_type === 'public' ? 'Platform Admin' : 'College Admin'}
                          </Badge>
                        </td>
                      )}
                      <td className="px-6 py-4 text-gray-600">{exam.question_count || 0}</td>
                      <td className="px-6 py-4 text-gray-600">{exam.duration_minutes || exam.duration || 60} min</td>
                      <td className="px-6 py-4">
                        <Badge variant={statusColors[exam.status] || 'neutral'}>
                          {exam.status}
                        </Badge>
                      </td>
                      <td className="px-6 py-4 text-gray-600">{exam.attempts_count || 0}</td>
                      <td className="px-6 py-4">
                        <div className="flex items-center gap-2">
                          {user?.role !== 'super_admin' && exam.status === 'pending' && (
                            <>
                              <button
                                onClick={(e) => { e.stopPropagation(); handleApprove(exam.id) }}
                                className="p-1.5 text-green-600 hover:bg-green-50 rounded"
                                title="Approve"
                              >
                                <Check size={16} />
                              </button>
                              <button
                                onClick={(e) => { e.stopPropagation(); handleReject(exam.id) }}
                                className="p-1.5 text-red-600 hover:bg-red-50 rounded"
                                title="Reject"
                              >
                                <X size={16} />
                              </button>
                            </>
                          )}
                          {user?.role !== 'super_admin' && ['published', 'active'].includes(exam.status) && (
                            <button
                              onClick={(e) => { e.stopPropagation(); handleArchive(exam.id) }}
                              className="p-1.5 text-gray-500 hover:text-amber-600 hover:bg-amber-50 rounded"
                              title="Archive"
                            >
                              <Archive size={16} />
                            </button>
                          )}
                          <button
                            onClick={(e) => { e.stopPropagation(); setSelectedExam(exam) }}
                            className="p-1.5 text-gray-500 hover:text-purple-600 hover:bg-purple-50 rounded"
                            title="View Results"
                          >
                            <BarChart3 size={16} />
                          </button>
                        </div>
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

      {/* Selected Exam Results Panel */}
      {selectedExam && (
        <div className="mt-8">
          <div className="bg-white rounded-xl border border-gray-200 shadow-sm">
            <div className="px-6 py-4 border-b border-gray-200 flex items-center justify-between">
              <div>
                <h3 className="text-lg font-semibold text-gray-900">Results Analysis: {selectedExam.title}</h3>
                <p className="text-sm text-gray-500">{selectedExam.subject}</p>
              </div>
              <button
                onClick={() => setSelectedExam(null)}
                className="p-1.5 text-gray-400 hover:text-gray-600 hover:bg-gray-100 rounded-lg"
              >
                <X size={18} />
              </button>
            </div>

            <div className="p-6">
              {resultsLoading ? (
                <div className="flex justify-center py-8">
                  <Loader />
                </div>
              ) : (
                <>
                  {/* Summary Metrics */}
                  <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-6">
                    <div className="bg-blue-50 rounded-lg p-4">
                      <div className="flex items-center justify-between">
                        <div>
                          <p className="text-sm font-medium text-gray-500">Success Rate</p>
                          <p className="text-2xl font-bold text-blue-600">
                            {examResults?.success_rate?.toFixed(1) || 0}%
                          </p>
                        </div>
                        <div className="w-10 h-10 bg-blue-100 rounded-lg flex items-center justify-center">
                          <CheckCircle className="w-5 h-5 text-blue-600" />
                        </div>
                      </div>
                    </div>

                    <div className="bg-green-50 rounded-lg p-4">
                      <div className="flex items-center justify-between">
                        <div>
                          <p className="text-sm font-medium text-gray-500">Average Score</p>
                          <p className="text-2xl font-bold text-green-600">
                            {examResults?.average_score?.toFixed(1) || 0}
                          </p>
                        </div>
                        <div className="w-10 h-10 bg-green-100 rounded-lg flex items-center justify-center">
                          <BarChart3 className="w-5 h-5 text-green-600" />
                        </div>
                      </div>
                    </div>

                    <div className="bg-purple-50 rounded-lg p-4">
                      <div className="flex items-center justify-between">
                        <div>
                          <p className="text-sm font-medium text-gray-500">Total Attempts</p>
                          <p className="text-2xl font-bold text-purple-600">
                            {examResults?.total_attempts || 0}
                          </p>
                        </div>
                        <div className="w-10 h-10 bg-purple-100 rounded-lg flex items-center justify-center">
                          <Users className="w-5 h-5 text-purple-600" />
                        </div>
                      </div>
                    </div>
                  </div>

                  {/* Percentile Distribution */}
                  {examResults?.percentile_distribution?.length > 0 && (
                    <div className="mt-6">
                      <h4 className="text-md font-semibold text-gray-900 mb-4">Percentile Distribution</h4>
                      <div className="bg-gray-50 rounded-lg p-4">
                        <div className="h-40 relative">
                          <div className="absolute inset-0 pointer-events-none">
                            {[0, 25, 50, 75, 100].map((p, i) => (
                              <div key={i} className="absolute left-0 right-0 h-0.5 bg-gray-200"
                                style={{ bottom: `${p}%` }} />
                            ))}
                          </div>
                          <div className="absolute inset-0 flex items-end justify-around px-4">
                            {examResults.percentile_distribution.map((p, index) => {
                              const height = Math.max(p.score || 0, 5)
                              return (
                                <div key={index} className="flex flex-col items-center group relative">
                                  <div
                                    className="w-8 bg-gradient-to-t from-blue-600 to-blue-400 rounded-t transition-all hover:from-blue-700 hover:to-blue-500"
                                    style={{ height: `${height}%` }}
                                  />
                                  <span className="mt-2 text-xs text-gray-500">{p.percentile}th</span>
                                  <div className="absolute bottom-full mb-2 hidden group-hover:block bg-gray-900 text-white text-xs px-2 py-1 rounded whitespace-nowrap z-10">
                                    {p.score?.toFixed(1) || 0}%
                                  </div>
                                </div>
                              )
                            })}
                          </div>
                        </div>
                      </div>
                    </div>
                  )}

                  {/* Top Performing Colleges */}
                  <div className="mt-6">
                    <div className="flex items-center justify-between mb-4">
                      <h4 className="text-md font-semibold text-gray-900">Top Performing Colleges</h4>
                      <p className="text-sm text-gray-500">Ranked by success rate</p>
                    </div>
                    {examResults?.top_colleges?.length > 0 ? (
                      <div className="space-y-3">
                        {examResults.top_colleges.map((college, index) => (
                          <div key={college.id} className="bg-gray-50 rounded-lg p-4">
                            <div className="flex items-center justify-between">
                              <div className="flex-1">
                                <div className="flex items-center mb-2">
                                  <div className="w-8 h-8 rounded-lg bg-blue-100 flex items-center justify-center">
                                    <span className="text-blue-600 font-bold">{index + 1}</span>
                                  </div>
                                  <div className="ml-3">
                                    <p className="font-medium text-gray-900">{college.name}</p>
                                    <p className="text-sm text-gray-500">
                                      {college.city}{college.state ? `, ${college.state}` : ''}
                                    </p>
                                  </div>
                                </div>
                                <p className="text-sm text-gray-500">
                                  {college.success_rate?.toFixed(1) || 0}% Success Rate
                                </p>
                              </div>
                              <div className="text-right">
                                <span className="px-2.5 py-0.5 text-xs font-medium rounded-full bg-green-100 text-green-700">
                                  {college.passed_count}/{college.total_attempts} Passed
                                </span>
                              </div>
                            </div>
                          </div>
                        ))}
                      </div>
                    ) : (
                      <div className="text-center py-8 text-gray-500">
                        No college performance data available
                      </div>
                    )}
                  </div>
                </>
              )}
            </div>
          </div>
        </div>
      )}
    </div>
  )
}