import { useState, useEffect } from 'react'
import { useNavigate, useParams } from 'react-router-dom'
import { useAuth } from '../../contexts/AuthContext'
import { useToast } from '../../contexts/ToastContext'
import { resultService } from '../../services/resultService'
import { examService } from '../../services/examService'
import Button from '../../components/ui/Button'
import Card from '../../components/ui/Card'
import Badge from '../../components/ui/Badge'
import Select from '../../components/ui/Select'
import Pagination from '../../components/ui/Pagination'
import Loader from '../../components/ui/Loader'
import { Download, Filter, Award, TrendingUp, Users } from 'lucide-react'

const gradeColors = {
  S: 'bg-purple-100 text-purple-700',
  A: 'bg-green-100 text-green-700',
  B: 'bg-blue-100 text-blue-700',
  C: 'bg-yellow-100 text-yellow-700',
  D: 'bg-orange-100 text-orange-700',
  F: 'bg-red-100 text-red-700'
}

export default function ResultsView() {
  const navigate = useNavigate()
  const { examId } = useParams()
  const { user } = useAuth()
  const { showToast } = useToast()
  const [exam, setExam] = useState(null)
  const [results, setResults] = useState([])
  const [stats, setStats] = useState(null)
  const [loading, setLoading] = useState(true)
  const [pagination, setPagination] = useState({ page: 1, limit: 20, total: 0 })
  const [filter, setFilter] = useState('all')
  const [sortBy, setSortBy] = useState('score_desc')

  useEffect(() => {
    if (user?.role !== 'teacher') {
      navigate('/dashboard')
      return
    }
    fetchExam()
    fetchResults()
  }, [user, examId, pagination.page, filter, sortBy])

  const fetchExam = async () => {
    try {
      const response = await examService.getExam(examId)
      setExam(response.data.data)
    } catch (error) {
      showToast('Failed to load exam', 'error')
    }
  }

  const fetchResults = async () => {
    try {
      setLoading(true)
      const [resultsRes, statsRes] = await Promise.all([
        resultService.getExamResults(examId),
        resultService.getLeaderboard(examId)
      ])
      
      let filteredResults = resultsRes.data.data || []
      
      if (filter === 'pass') {
        filteredResults = filteredResults.filter(r => r.percentage >= (exam?.passing_marks || 35))
      } else if (filter === 'fail') {
        filteredResults = filteredResults.filter(r => r.percentage < (exam?.passing_marks || 35))
      }

      if (sortBy === 'score_desc') {
        filteredResults.sort((a, b) => b.score - a.score)
      } else if (sortBy === 'score_asc') {
        filteredResults.sort((a, b) => a.score - b.score)
      } else if (sortBy === 'time') {
        filteredResults.sort((a, b) => a.time_taken - b.time_taken)
      }

      const start = (pagination.page - 1) * pagination.limit
      const paginatedResults = filteredResults.slice(start, start + pagination.limit)

      setResults(paginatedResults)
      setPagination(prev => ({ ...prev, total: filteredResults.length }))
      setStats(statsRes.data.data)
    } catch (error) {
      showToast('Failed to load results', 'error')
    } finally {
      setLoading(false)
    }
  }

  const handleExport = async () => {
    try {
      const response = await resultService.getExamResults(examId)
      const results = response.data.data || []
      
      const csvContent = [
        ['Rank', 'Student Name', 'Email', 'Score', 'Percentage', 'Grade', 'Time Taken (min)'].join(','),
        ...results.map((r, idx) => [
          idx + 1,
          `${r.student?.first_name} ${r.student?.last_name}`,
          r.student?.email,
          r.score,
          r.percentage.toFixed(2),
          r.grade || '-',
          Math.round((r.time_taken || 0) / 60)
        ].join(','))
      ].join('\n')

      const blob = new Blob([csvContent], { type: 'text/csv' })
      const url = window.URL.createObjectURL(blob)
      const link = document.createElement('a')
      link.href = url
      link.setAttribute('download', `${exam?.title}_results.csv`)
      document.body.appendChild(link)
      link.click()
      link.remove()
      showToast('Results exported', 'success')
    } catch (error) {
      showToast('Failed to export results', 'error')
    }
  }

  const filterOptions = [
    { value: 'all', label: 'All Results' },
    { value: 'pass', label: 'Pass Only' },
    { value: 'fail', label: 'Fail Only' }
  ]

  const sortOptions = [
    { value: 'score_desc', label: 'Score (High to Low)' },
    { value: 'score_asc', label: 'Score (Low to High)' },
    { value: 'time', label: 'Time Taken' }
  ]

  const getGrade = (percentage) => {
    if (percentage >= 90) return 'S'
    if (percentage >= 80) return 'A'
    if (percentage >= 70) return 'B'
    if (percentage >= 60) return 'C'
    if (percentage >= 50) return 'D'
    return 'F'
  }

  const passCount = results.filter(r => r.percentage >= (exam?.passing_marks || 35)).length
  const failCount = results.length - passCount
  const passRate = results.length > 0 ? ((passCount / results.length) * 100).toFixed(1) : 0

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">Exam Results</h1>
          <p className="text-gray-500 mt-1">{exam?.title}</p>
        </div>
        <Button variant="secondary" leftIcon={<Download size={18} />} onClick={handleExport}>
          Export to Excel
        </Button>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <Card className="p-4">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 bg-blue-100 rounded-lg flex items-center justify-center">
              <Users className="text-blue-600" size={20} />
            </div>
            <div>
              <p className="text-2xl font-bold text-gray-900">{pagination.total}</p>
              <p className="text-sm text-gray-500">Total Attempts</p>
            </div>
          </div>
        </Card>
        <Card className="p-4">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 bg-green-100 rounded-lg flex items-center justify-center">
              <TrendingUp className="text-green-600" size={20} />
            </div>
            <div>
              <p className="text-2xl font-bold text-gray-900">{passRate}%</p>
              <p className="text-sm text-gray-500">Pass Rate</p>
            </div>
          </div>
        </Card>
        <Card className="p-4">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 bg-purple-100 rounded-lg flex items-center justify-center">
              <Award className="text-purple-600" size={20} />
            </div>
            <div>
              <p className="text-2xl font-bold text-gray-900">{stats?.top_score || '-'}</p>
              <p className="text-sm text-gray-500">Top Score</p>
            </div>
          </div>
        </Card>
        <Card className="p-4">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 bg-amber-100 rounded-lg flex items-center justify-center">
              <TrendingUp className="text-amber-600" size={20} />
            </div>
            <div>
              <p className="text-2xl font-bold text-gray-900">{stats?.avg_score?.toFixed(1) || '-'}</p>
              <p className="text-sm text-gray-500">Average Score</p>
            </div>
          </div>
        </Card>
      </div>

      <Card>
        <div className="p-4 border-b border-gray-200 flex flex-col sm:flex-row gap-4">
          <div className="flex items-center gap-2">
            <Filter size={16} className="text-gray-400" />
            <Select
              options={filterOptions}
              value={filter}
              onChange={setFilter}
              className="w-32"
            />
          </div>
          <Select
            options={sortOptions}
            value={sortBy}
            onChange={setSortBy}
            className="w-48"
          />
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
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Rank</th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Student</th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Score</th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Percentage</th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Grade</th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Time Taken</th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Status</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-gray-100">
                {results.length === 0 ? (
                  <tr>
                    <td colSpan={7} className="px-6 py-8 text-center text-gray-500">
                      No results found
                    </td>
                  </tr>
                ) : (
                  results.map((result, idx) => {
                    const percentage = result.percentage || ((result.score / (exam?.total_marks || 100)) * 100)
                    const passed = percentage >= (exam?.passing_marks || 35)
                    return (
                      <tr key={result.id} className="hover:bg-gray-50">
                        <td className="px-6 py-4">
                          <span className={`inline-flex items-center justify-center w-8 h-8 rounded-full ${
                            idx === 0 ? 'bg-yellow-100 text-yellow-700' :
                            idx === 1 ? 'bg-gray-100 text-gray-700' :
                            idx === 2 ? 'bg-orange-100 text-orange-700' : 'bg-gray-50 text-gray-600'
                          }`}>
                            {idx + 1}
                          </span>
                        </td>
                        <td className="px-6 py-4">
                          <div>
                            <p className="font-medium text-gray-900">
                              {result.student?.first_name} {result.student?.last_name}
                            </p>
                            <p className="text-xs text-gray-500">{result.student?.email}</p>
                          </div>
                        </td>
                        <td className="px-6 py-4 text-gray-900">
                          {result.score} / {exam?.total_marks || 100}
                        </td>
                        <td className="px-6 py-4 text-gray-900">
                          {percentage.toFixed(1)}%
                        </td>
                        <td className="px-6 py-4">
                          <span className={`inline-flex items-center justify-center w-8 h-8 rounded-full font-bold text-sm ${gradeColors[getGrade(percentage)]}`}>
                            {getGrade(percentage)}
                          </span>
                        </td>
                        <td className="px-6 py-4 text-gray-600">
                          {Math.floor((result.time_taken || 0) / 60)} min
                        </td>
                        <td className="px-6 py-4">
                          <Badge variant={passed ? 'success' : 'danger'}>
                            {passed ? 'Passed' : 'Failed'}
                          </Badge>
                        </td>
                      </tr>
                    )
                  })
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