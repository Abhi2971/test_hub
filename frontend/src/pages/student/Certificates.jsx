import { useState, useEffect } from 'react'
import { useNavigate } from 'react-router-dom'
import { useAuth } from '../../contexts/AuthContext'
import { useToast } from '../../contexts/ToastContext'
import { resultService } from '../../services/resultService'
import api from '../../services/api'
import Button from '../../components/ui/Button'
import Card from '../../components/ui/Card'
import Badge from '../../components/ui/Badge'
import Loader from '../../components/ui/Loader'
import { Award, Download, CheckCircle, Calendar } from 'lucide-react'

export default function Certificates() {
  const navigate = useNavigate()
  const { user } = useAuth()
  const { showToast } = useToast()
  const [certificates, setCertificates] = useState([])
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    if (user?.role !== 'student_registered' && user?.role !== 'student_assigned') {
      navigate('/dashboard')
      return
    }
    fetchCertificates()
  }, [user])

  const fetchCertificates = async () => {
    try {
      setLoading(true)
      const response = await api.get('/certificates')
      setCertificates(response.data.data || [])
    } catch (error) {
      showToast('Failed to load certificates', 'error')
    } finally {
      setLoading(false)
    }
  }

  const handleDownload = async (certificateId) => {
    try {
      const response = await resultService.downloadCertificate(certificateId)
      if (response.data.data?.download_url) {
        window.open(response.data.data.download_url, '_blank')
      }
    } catch (error) {
      showToast('Failed to download certificate', 'error')
    }
  }

  const getGradeColor = (grade) => {
    switch (grade) {
      case 'S': return 'text-purple-600'
      case 'A': return 'text-green-600'
      case 'B': return 'text-blue-600'
      case 'C': return 'text-yellow-600'
      default: return 'text-gray-600'
    }
  }

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold text-gray-900">Certificates</h1>
        <p className="text-gray-500 mt-1">Your earned certificates</p>
      </div>

      {loading ? (
        <div className="flex justify-center py-12">
          <Loader />
        </div>
      ) : certificates.length === 0 ? (
        <Card>
          <div className="p-12 text-center">
            <Award className="mx-auto text-gray-300 mb-4" size={48} />
            <p className="text-gray-500 mb-4">No certificates earned yet</p>
            <p className="text-sm text-gray-400">Complete exams with certificates to earn them here</p>
          </div>
        </Card>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {certificates.map((cert) => (
            <Card key={cert.id} className="overflow-hidden hover:shadow-lg transition-shadow">
              <div className="h-32 bg-gradient-to-br from-yellow-50 to-amber-100 flex items-center justify-center">
                <Award className="text-amber-400" size={48} />
              </div>
              <div className="p-5">
                <div className="flex items-center justify-between mb-2">
                  <h3 className="font-semibold text-gray-900">{cert.exam_name || 'Exam'}</h3>
                  <Badge variant="success">Verified</Badge>
                </div>
                <div className="flex items-center justify-between text-sm text-gray-600 mb-4">
                  <span>Score: <span className={`font-bold ${getGradeColor(cert.grade)}`}>{cert.score}%</span></span>
                  <span>Grade: <span className={`font-bold ${getGradeColor(cert.grade)}`}>{cert.grade}</span></span>
                </div>
                <div className="flex items-center gap-2 text-sm text-gray-500 mb-4">
                  <Calendar size={14} />
                  <span>Issued: {new Date(cert.issued_at).toLocaleDateString()}</span>
                </div>
                <Button className="w-full" leftIcon={<Download size={18} />} onClick={() => handleDownload(cert.id)}>
                  Download Certificate
                </Button>
              </div>
            </Card>
          ))}
        </div>
      )}
    </div>
  )
}