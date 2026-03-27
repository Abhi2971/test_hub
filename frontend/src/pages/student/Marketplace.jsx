import { useState, useEffect } from 'react'
import { useNavigate } from 'react-router-dom'
import { useAuth } from '../../contexts/AuthContext'
import { useToast } from '../../contexts/ToastContext'
import { examService } from '../../services/examService'
import { paymentService } from '../../services/paymentService'
import api from '../../services/api'
import Button from '../../components/ui/Button'
import Card from '../../components/ui/Card'
import Badge from '../../components/ui/Badge'
import Select from '../../components/ui/Select'
import Loader from '../../components/ui/Loader'
import { Search, Clock, FileText, DollarSign, Play } from 'lucide-react'

export default function Marketplace() {
  const navigate = useNavigate()
  const { user } = useAuth()
  const { showToast } = useToast()
  const [exams, setExams] = useState([])
  const [loading, setLoading] = useState(true)
  const [filters, setFilters] = useState({ subject: '', price: '', difficulty: '' })
  const [searchQuery, setSearchQuery] = useState('')

  useEffect(() => {
    if (user?.role !== 'student_registered' && user?.role !== 'student_assigned') {
      navigate('/dashboard')
      return
    }
    fetchMarketplace()
  }, [user, filters])

  const fetchMarketplace = async () => {
    try {
      setLoading(true)
      const params = {
        ...(filters.subject && { subject: filters.subject }),
        ...(filters.price && { price_type: filters.price }),
        ...(filters.difficulty && { difficulty: filters.difficulty }),
        ...(searchQuery && { search: searchQuery })
      }
      const response = await examService.getMarketplace(params)
      setExams(response.data?.items || [])
    } catch (error) {
      showToast('Failed to load marketplace', 'error')
    } finally {
      setLoading(false)
    }
  }

  const handlePurchase = async (exam) => {
    if (exam.price === 0 || exam.price === null) {
      const response = await examService.generateMagicLink(exam.id)
      navigate(`/exam/${exam.id}/start?token=${response.data.data.token}`)
      return
    }

    try {
      const walletResponse = await paymentService.getWallet()
      const walletBalance = walletResponse.data.data.balance

      if (walletBalance < exam.price) {
        showToast('Insufficient wallet balance. Please top up.', 'error')
        navigate('/dashboard/student/wallet')
        return
      }

      if (!confirm(`Purchase this exam for ₹${exam.price}?`)) return

      const response = await api.post('/payments/purchase-exam', { exam_id: exam.id })
      
      if (response.data.data.access_url) {
        navigate(response.data.data.access_url)
      } else {
        showToast('Exam purchased successfully!', 'success')
        fetchMarketplace()
      }
    } catch (error) {
      showToast(error.response?.data?.message || 'Failed to purchase exam', 'error')
    }
  }

  const subjectOptions = [
    { value: '', label: 'All Subjects' },
    { value: 'math', label: 'Mathematics' },
    { value: 'science', label: 'Science' },
    { value: 'english', label: 'English' },
    { value: 'history', label: 'History' },
    { value: 'geography', label: 'Geography' }
  ]

  const priceOptions = [
    { value: '', label: 'All Prices' },
    { value: 'free', label: 'Free' },
    { value: 'paid', label: 'Paid' }
  ]

  const difficultyOptions = [
    { value: '', label: 'All Difficulties' },
    { value: 'easy', label: 'Easy' },
    { value: 'medium', label: 'Medium' },
    { value: 'hard', label: 'Hard' }
  ]

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold text-gray-900">Exam Marketplace</h1>
        <p className="text-gray-500 mt-1">Browse and purchase public exams</p>
      </div>

      <Card>
        <div className="p-4 border-b border-gray-200">
          <div className="flex flex-col md:flex-row gap-4">
            <div className="flex-1 relative">
              <Search className="absolute left-3 top-1/2 -translate-y-1/2 text-gray-400" size={18} />
              <input
                type="text"
                placeholder="Search exams..."
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                onKeyDown={(e) => e.key === 'Enter' && fetchMarketplace()}
                className="w-full pl-10 pr-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-200"
              />
            </div>
            <div className="flex gap-2">
              <Select options={subjectOptions} value={filters.subject} onChange={(v) => setFilters(f => ({ ...f, subject: v }))} className="w-36" />
              <Select options={priceOptions} value={filters.price} onChange={(v) => setFilters(f => ({ ...f, price: v }))} className="w-32" />
              <Select options={difficultyOptions} value={filters.difficulty} onChange={(v) => setFilters(f => ({ ...f, difficulty: v }))} className="w-36" />
            </div>
          </div>
        </div>

        {loading ? (
          <div className="p-8 flex justify-center">
            <Loader />
          </div>
        ) : exams.length === 0 ? (
          <div className="p-12 text-center text-gray-500">
            No exams found in marketplace
          </div>
        ) : (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6 p-6">
            {exams.map((exam) => {
              const isOwned = exam.is_purchased || exam.price === 0
              return (
                <div key={exam.id} className="border border-gray-200 rounded-xl p-5 hover:shadow-lg transition-shadow">
                  <div className="flex items-start justify-between">
                    <div>
                      <h3 className="font-semibold text-gray-900">{exam.title}</h3>
                      <p className="text-sm text-gray-500 mt-1">{exam.subject}</p>
                    </div>
                    {isOwned ? (
                      <Badge variant="success">Owned</Badge>
                    ) : (
                      <div className="flex items-center gap-1 text-lg font-bold text-gray-900">
                        <DollarSign size={16} />
                        {exam.price || 'FREE'}
                      </div>
                    )}
                  </div>

                  <div className="mt-4 flex items-center gap-4 text-sm text-gray-600">
                    <div className="flex items-center gap-1">
                      <Clock size={14} />
                      {exam.duration} min
                    </div>
                    <div className="flex items-center gap-1">
                      <FileText size={14} />
                      {exam.question_count} Q
                    </div>
                    {exam.difficulty && (
                      <Badge variant={exam.difficulty === 'easy' ? 'success' : exam.difficulty === 'medium' ? 'warning' : 'danger'}>
                        {exam.difficulty}
                      </Badge>
                    )}
                  </div>

                  <div className="mt-4">
                    {isOwned ? (
                      <Button className="w-full" leftIcon={<Play size={18} />} onClick={() => {
                        const response = examService.generateMagicLink(exam.id)
                        navigate(`/exam/${exam.id}/start?token=${response.data.data.token}`)
                      }}>
                        Attempt Now
                      </Button>
                    ) : (
                      <Button className="w-full" onClick={() => handlePurchase(exam)}>
                        {exam.price ? `Purchase for ₹${exam.price}` : 'Attempt Free'}
                      </Button>
                    )}
                  </div>
                </div>
              )
            })}
          </div>
        )}
      </Card>
    </div>
  )
}