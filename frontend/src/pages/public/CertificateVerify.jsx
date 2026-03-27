import { useState, useEffect } from 'react'
import { useSearchParams, useNavigate } from 'react-router-dom'
import { resultService } from '../../services/resultService'
import Card from '../../components/ui/Card'
import Input from '../../components/ui/Input'
import Button from '../../components/ui/Button'
import Loader from '../../components/ui/Loader'
import { Search, Award, CheckCircle, XCircle, Download, Calendar, User, BookOpen } from 'lucide-react'

export default function CertificateVerify() {
  const [searchParams] = useSearchParams()
  const navigate = useNavigate()
  const [certificateId, setCertificateId] = useState(searchParams.get('id') || '')
  const [certificate, setCertificate] = useState(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState(null)
  const [searched, setSearched] = useState(false)

  const verifyCertificate = async (e) => {
    e.preventDefault()
    if (!certificateId.trim()) return

    try {
      setLoading(true)
      setError(null)
      setSearched(true)
      const response = await resultService.verifyCertificate(certificateId)
      setCertificate(response.data.data)
    } catch (err) {
      setError('Certificate not found or invalid')
      setCertificate(null)
    } finally {
      setLoading(false)
    }
  }

  const getGradeColor = (grade) => {
    const colors = {
      'S': 'text-green-600',
      'A': 'text-blue-600',
      'B': 'text-indigo-600',
      'C': 'text-yellow-600',
      'D': 'text-orange-600',
      'F': 'text-red-600'
    }
    return colors[grade] || 'text-gray-600'
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-indigo-50 to-white py-12 px-4">
      <div className="max-w-2xl mx-auto">
        <div className="text-center mb-8">
          <div className="inline-flex items-center justify-center w-16 h-16 bg-indigo-100 rounded-full mb-4">
            <Award className="text-indigo-600" size={32} />
          </div>
          <h1 className="text-3xl font-bold text-gray-900">Certificate Verification</h1>
          <p className="text-gray-500 mt-2">Verify the authenticity of exam certificates</p>
        </div>

        <Card className="p-6">
          <form onSubmit={verifyCertificate} className="flex gap-3">
            <div className="flex-1">
              <Input
                placeholder="Enter Certificate ID"
                value={certificateId}
                onChange={(e) => setCertificateId(e.target.value)}
              />
            </div>
            <Button type="submit" disabled={loading} leftIcon={<Search size={16} />}>
              Verify
            </Button>
          </form>
        </Card>

        {loading && (
          <div className="flex justify-center py-12">
            <Loader />
          </div>
        )}

        {error && searched && !loading && (
          <Card className="mt-6 p-8">
            <div className="text-center">
              <XCircle className="mx-auto text-red-500 mb-4" size={48} />
              <h3 className="text-lg font-semibold text-gray-900 mb-2">Invalid Certificate</h3>
              <p className="text-gray-500">{error}</p>
            </div>
          </Card>
        )}

        {certificate && (
          <Card className="mt-6 overflow-hidden">
            <div className="bg-gradient-to-r from-indigo-600 to-purple-600 p-6 text-white">
              <div className="flex items-center justify-between">
                <div>
                  <h2 className="text-2xl font-bold">Certificate of Completion</h2>
                  <p className="opacity-90 mt-1">This certifies that</p>
                </div>
                <Award size={48} className="opacity-50" />
              </div>
            </div>

            <div className="p-6">
              <div className="text-center mb-6">
                <h3 className="text-2xl font-bold text-gray-900">{certificate.student_name}</h3>
                <p className="text-gray-500">has successfully completed</p>
                <h4 className="text-xl font-semibold text-indigo-600 mt-2">{certificate.exam_title}</h4>
              </div>

              <div className="grid grid-cols-2 gap-4 mb-6">
                <div className="bg-gray-50 rounded-lg p-4">
                  <div className="flex items-center gap-2 text-gray-500 mb-1">
                    <BookOpen size={16} />
                    <span className="text-sm">Subject</span>
                  </div>
                  <p className="font-medium text-gray-900">{certificate.subject}</p>
                </div>
                <div className="bg-gray-50 rounded-lg p-4">
                  <div className="flex items-center gap-2 text-gray-500 mb-1">
                    <Calendar size={16} />
                    <span className="text-sm">Date</span>
                  </div>
                  <p className="font-medium text-gray-900">{new Date(certificate.issued_at).toLocaleDateString()}</p>
                </div>
              </div>

              <div className="grid grid-cols-3 gap-4 mb-6">
                <div className="text-center p-4 bg-gray-50 rounded-lg">
                  <p className="text-sm text-gray-500 mb-1">Score</p>
                  <p className="text-2xl font-bold text-gray-900">{certificate.score}%</p>
                </div>
                <div className="text-center p-4 bg-gray-50 rounded-lg">
                  <p className="text-sm text-gray-500 mb-1">Grade</p>
                  <p className={`text-2xl font-bold ${getGradeColor(certificate.grade)}`}>{certificate.grade}</p>
                </div>
                <div className="text-center p-4 bg-gray-50 rounded-lg">
                  <p className="text-sm text-gray-500 mb-1">Status</p>
                  <div className="flex items-center justify-center gap-1">
                    <CheckCircle size={16} className="text-green-500" />
                    <span className="font-medium text-green-600">Verified</span>
                  </div>
                </div>
              </div>

              <div className="border-t border-gray-200 pt-4">
                <div className="flex justify-between items-center text-sm text-gray-500">
                  <span>Certificate ID: {certificate.id}</span>
                  <span>Issued by: {certificate.institute_name}</span>
                </div>
              </div>

              <div className="mt-6 flex gap-3 justify-center">
                <Button leftIcon={<Download size={16} />}>
                  Download PDF
                </Button>
                <Button variant="secondary" onClick={() => { setCertificateId(''); setCertificate(null); setSearched(false); }}>
                  Verify Another
                </Button>
              </div>
            </div>
          </Card>
        )}

        {!searched && !loading && (
          <Card className="mt-6 p-8">
            <div className="text-center text-gray-500">
              <p>Enter a certificate ID above to verify its authenticity</p>
            </div>
          </Card>
        )}
      </div>
    </div>
  )
}