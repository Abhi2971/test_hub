import { useState, useEffect } from 'react'
import { useNavigate } from 'react-router-dom'
import { useAuth } from '../../contexts/AuthContext'
import { useToast } from '../../contexts/ToastContext'
import api from '../../services/api'
import Button from '../../components/ui/Button'
import Card from '../../components/ui/Card'
import Badge from '../../components/ui/Badge'
import Select from '../../components/ui/Select'
import Loader from '../../components/ui/Loader'
import { BookOpen, Search, Eye, Download } from 'lucide-react'

export default function EbookLibrary() {
  const navigate = useNavigate()
  const { user } = useAuth()
  const { showToast } = useToast()
  const [ebooks, setEbooks] = useState([])
  const [loading, setLoading] = useState(true)
  const [subjectFilter, setSubjectFilter] = useState('')

  useEffect(() => {
    if (user?.role !== 'student_registered' && user?.role !== 'student_assigned') {
      navigate('/dashboard')
      return
    }
    fetchEbooks()
  }, [user, subjectFilter])

  const fetchEbooks = async () => {
    try {
      setLoading(true)
      const params = subjectFilter ? { subject: subjectFilter } : {}
      const response = await api.get('/ebooks', { params })
      setEbooks(response.data.data || [])
    } catch (error) {
      showToast('Failed to load ebooks', 'error')
    } finally {
      setLoading(false)
    }
  }

  const handleRead = async (ebook) => {
    try {
      const response = await api.get(`/ebooks/${ebook.id}/read`)
      if (response.data.data.url) {
        window.open(response.data.data.url, '_blank')
      }
    } catch (error) {
      showToast('Failed to open ebook', 'error')
    }
  }

  const subjectOptions = [
    { value: '', label: 'All Subjects' },
    { value: 'math', label: 'Mathematics' },
    { value: 'science', label: 'Science' },
    { value: 'english', label: 'English' },
    { value: 'history', label: 'History' }
  ]

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">Ebook Library</h1>
          <p className="text-gray-500 mt-1">Access your learning materials</p>
        </div>
        <Select
          options={subjectOptions}
          value={subjectFilter}
          onChange={setSubjectFilter}
          className="w-40"
        />
      </div>

      {loading ? (
        <div className="flex justify-center py-12">
          <Loader />
        </div>
      ) : ebooks.length === 0 ? (
        <Card>
          <div className="p-12 text-center">
            <BookOpen className="mx-auto text-gray-300 mb-4" size={48} />
            <p className="text-gray-500">No ebooks available</p>
          </div>
        </Card>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
          {ebooks.map((ebook) => (
            <Card key={ebook.id} className="overflow-hidden hover:shadow-lg transition-shadow">
              <div className="h-40 bg-gradient-to-br from-indigo-50 to-blue-100 flex items-center justify-center">
                <BookOpen className="text-indigo-300" size={48} />
              </div>
              <div className="p-4">
                <h3 className="font-semibold text-gray-900 truncate">{ebook.title}</h3>
                <p className="text-sm text-gray-500 mt-1">{ebook.subject}</p>
                <div className="flex items-center gap-2 mt-2">
                  <Badge variant="info">{ebook.access_level}</Badge>
                </div>
                <div className="mt-4 flex gap-2">
                  <Button className="flex-1" size="sm" leftIcon={<Eye size={14} />} onClick={() => handleRead(ebook)}>
                    Read
                  </Button>
                  <Button variant="secondary" size="sm" leftIcon={<Download size={14} />}>
                    PDF
                  </Button>
                </div>
              </div>
            </Card>
          ))}
        </div>
      )}
    </div>
  )
}