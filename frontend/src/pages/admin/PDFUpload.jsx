import { useState, useEffect } from 'react'
import { useNavigate, useParams } from 'react-router-dom'
import { useAuth } from '../../contexts/AuthContext'
import { useToast } from '../../contexts/ToastContext'
import { examService } from '../../services/examService'
import api from '../../services/api'
import Button from '../../components/ui/Button'
import Card from '../../components/ui/Card'
import Badge from '../../components/ui/Badge'
import Select from '../../components/ui/Select'
import Input from '../../components/ui/Input'
import Loader from '../../components/ui/Loader'
import { Upload, FileText, Check, X, Plus, ArrowRight, Loader as LoaderIcon, Brain } from 'lucide-react'

const stages = ['upload', 'processing', 'review', 'complete']
const stageLabels = {
  upload: 'Upload PDF',
  processing: 'Processing',
  review: 'Review Questions',
  complete: 'Complete'
}

const processingStages = {
  extracting: 'Extracting text from PDF...',
  chunking: 'Chunking content...',
  generating: 'Generating questions...',
  review: 'Preparing for review...'
}

export default function PDFUpload() {
  const navigate = useNavigate()
  const { examId } = useParams()
  const { user } = useAuth()
  const { showToast } = useToast()
  const [currentStage, setCurrentStage] = useState('upload')
  const [file, setFile] = useState(null)
  const [topic, setTopic] = useState('')
  const [processingStatus, setProcessingStatus] = useState(null)
  const [generatedQuestions, setGeneratedQuestions] = useState([])
  const [examOptions, setExamOptions] = useState([])
  const [selectedExam, setSelectedExam] = useState('')
  const [loading, setLoading] = useState(false)
  const [polling, setPolling] = useState(null)

  useEffect(() => {
    if (!['admin_college', 'admin_public', 'super_admin', 'teacher'].includes(user?.role)) {
      navigate('/dashboard')
      return
    }
    fetchExams()
    return () => {
      if (polling) clearInterval(polling)
    }
  }, [user])

  const fetchExams = async () => {
    try {
      const response = await examService.getExams({ status: 'draft', limit: 50 })
      const exams = response.data?.items || []
      setExamOptions(exams.map(e => ({ value: e.id, label: e.title })))
    } catch (error) {
      console.error('Failed to fetch exams', error)
    }
  }

  const handleFileChange = (e) => {
    const selectedFile = e.target.files?.[0]
    if (selectedFile) {
      if (selectedFile.type !== 'application/pdf') {
        showToast('Please upload a PDF file', 'error')
        return
      }
      if (selectedFile.size > 10 * 1024 * 1024) {
        showToast('File size must be less than 10MB', 'error')
        return
      }
      setFile(selectedFile)
    }
  }

  const startProcessing = async () => {
    if (!file) {
      showToast('Please select a file', 'error')
      return
    }
    if (!topic.trim()) {
      showToast('Please enter a topic', 'error')
      return
    }

    setLoading(true)
    try {
      const formData = new FormData()
      formData.append('file', file)
      formData.append('topic', topic)

      const response = await api.post('/questions/generate-from-pdf', formData, {
        headers: { 'Content-Type': 'multipart/form-data' }
      })

      const jobId = response.data.data?.job_id
      if (jobId) {
        setCurrentStage('processing')
        startPolling(jobId)
      } else {
        setGeneratedQuestions(response.data.data?.questions || [])
        setCurrentStage('review')
      }
    } catch (error) {
      showToast(error.response?.data?.message || 'Failed to start processing', 'error')
    } finally {
      setLoading(false)
    }
  }

  const startPolling = (jobId) => {
    const poll = setInterval(async () => {
      try {
        const response = await api.get(`/jobs/${jobId}`)
        const status = response.data.data

        setProcessingStatus(status)

        if (status.status === 'completed') {
          clearInterval(poll)
          setGeneratedQuestions(status.questions || [])
          setCurrentStage('review')
          setPolling(null)
        } else if (status.status === 'failed') {
          clearInterval(poll)
          showToast(status.error || 'Processing failed', 'error')
          setCurrentStage('upload')
          setPolling(null)
        }
      } catch (error) {
        console.error('Polling error', error)
      }
    }, 3000)

    setPolling(poll)
  }

  const handleApproveQuestion = async (questionId) => {
    try {
      await api.patch(`/questions/${questionId}`, { reviewed: true, status: 'approved' })
      setGeneratedQuestions(prev =>
        prev.map(q => q.id === questionId ? { ...q, reviewed: true, status: 'approved' } : q)
      )
    } catch (error) {
      showToast('Failed to approve question', 'error')
    }
  }

  const handleRejectQuestion = async (questionId) => {
    try {
      await api.patch(`/questions/${questionId}`, { reviewed: true, status: 'rejected' })
      setGeneratedQuestions(prev =>
        prev.map(q => q.id === questionId ? { ...q, reviewed: true, status: 'rejected' } : q)
      )
    } catch (error) {
      showToast('Failed to reject question', 'error')
    }
  }

  const handleAddToExam = async (questionId) => {
    if (!selectedExam) {
      showToast('Please select an exam', 'error')
      return
    }
    try {
      await api.post(`/exams/${selectedExam}/questions`, { question_ids: [questionId] })
      showToast('Question added to exam', 'success')
    } catch (error) {
      showToast('Failed to add question to exam', 'error')
    }
  }

  const handleAddAllToExam = async () => {
    if (!selectedExam) {
      showToast('Please select an exam', 'error')
      return
    }
    const approvedIds = generatedQuestions.filter(q => q.status === 'approved').map(q => q.id)
    if (approvedIds.length === 0) {
      showToast('No approved questions to add', 'error')
      return
    }
    try {
      await api.post(`/exams/${selectedExam}/questions`, { question_ids: approvedIds })
      showToast(`${approvedIds.length} questions added to exam`, 'success')
      setCurrentStage('complete')
    } catch (error) {
      showToast('Failed to add questions to exam', 'error')
    }
  }

  const formatFileSize = (bytes) => {
    if (bytes < 1024) return bytes + ' B'
    if (bytes < 1024 * 1024) return (bytes / 1024).toFixed(1) + ' KB'
    return (bytes / (1024 * 1024)).toFixed(1) + ' MB'
  }

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold text-gray-900">PDF to Questions</h1>
        <p className="text-gray-500 mt-1">Generate questions from PDF documents</p>
      </div>

      <div className="flex items-center justify-center gap-4">
        {stages.map((stage, idx) => (
          <div key={stage} className="flex items-center">
            <div className={`flex items-center gap-2 px-4 py-2 rounded-full ${
              currentStage === stage ? 'bg-blue-600 text-white' :
              stages.indexOf(currentStage) > idx ? 'bg-green-100 text-green-700' :
              'bg-gray-100 text-gray-500'
            }`}>
              {stage === 'upload' && <Upload size={16} />}
              {stage === 'processing' && stages.indexOf(currentStage) > stages.indexOf(stage) ? <Check size={16} /> :
               stage === 'processing' ? <LoaderIcon size={16} className="animate-spin" /> : null}
              {stage === 'review' && stages.indexOf(currentStage) > stages.indexOf(stage) ? <Check size={16} /> : null}
              {stage === 'complete' && <Check size={16} />}
              <span className="text-sm font-medium">{stageLabels[stage]}</span>
            </div>
            {idx < stages.length - 1 && (
              <ArrowRight size={16} className="mx-2 text-gray-400" />
            )}
          </div>
        ))}
      </div>

      {currentStage === 'upload' && (
        <Card>
          <div className="p-6 space-y-6">
            <div className="border-2 border-dashed border-gray-300 rounded-xl p-8 text-center hover:border-blue-400 transition-colors">
              <input
                type="file"
                accept=".pdf"
                onChange={handleFileChange}
                className="hidden"
                id="pdf-upload"
              />
              <label htmlFor="pdf-upload" className="cursor-pointer">
                <Upload className="mx-auto text-gray-400 mb-4" size={48} />
                <p className="text-lg font-medium text-gray-700">
                  {file ? file.name : 'Click to upload PDF'}
                </p>
                {file && (
                  <p className="text-sm text-gray-500 mt-1">{formatFileSize(file.size)}</p>
                )}
                <p className="text-sm text-gray-400 mt-2">PDF up to 10MB</p>
              </label>
            </div>

            <Input
              label="Topic / Subject"
              value={topic}
              onChange={(e) => setTopic(e.target.value)}
              placeholder="e.g., Mathematics, Physics, History"
              helpText="Enter the topic or subject this PDF covers"
            />

            <div className="flex justify-end">
              <Button
                onClick={startProcessing}
                loading={loading}
                disabled={!file || !topic.trim()}
                leftIcon={<Brain size={18} />}
              >
                Generate Questions
              </Button>
            </div>
          </div>
        </Card>
      )}

      {currentStage === 'processing' && (
        <Card>
          <div className="p-8 text-center">
            <LoaderIcon className="mx-auto text-blue-600 mb-4" size={48} />
            <h3 className="text-lg font-semibold text-gray-900">Processing your PDF</h3>
            <p className="text-gray-500 mt-2">
              {processingStatus?.stage ? processingStages[processingStatus.stage] : 'Starting...'}
            </p>

            {processingStatus?.progress !== undefined && (
              <div className="mt-6 max-w-md mx-auto">
                <div className="flex justify-between text-sm text-gray-600 mb-2">
                  <span>Progress</span>
                  <span>{processingStatus.progress}%</span>
                </div>
                <div className="w-full bg-gray-200 rounded-full h-2">
                  <div
                    className="bg-blue-600 h-2 rounded-full transition-all duration-300"
                    style={{ width: `${processingStatus.progress}%` }}
                  />
                </div>
              </div>
            )}
          </div>
        </Card>
      )}

      {currentStage === 'review' && (
        <div className="space-y-6">
          <Card>
            <div className="p-4 border-b border-gray-200">
              <div className="flex items-center justify-between">
                <h3 className="font-semibold text-gray-900">Review Generated Questions</h3>
                <div className="flex items-center gap-4">
                  <Select
                    options={[{ value: '', label: 'Select Exam...' }, ...examOptions]}
                    value={selectedExam}
                    onChange={setSelectedExam}
                    className="w-64"
                  />
                  <Button
                    onClick={handleAddAllToExam}
                    disabled={!selectedExam}
                    leftIcon={<Plus size={18} />}
                  >
                    Add All Approved to Exam
                  </Button>
                </div>
              </div>
            </div>
            <div className="p-4 bg-gray-50 text-sm text-gray-600">
              <span className="font-medium">{generatedQuestions.filter(q => q.status === 'approved').length}</span> approved,{' '}
              <span className="font-medium">{generatedQuestions.filter(q => q.status === 'rejected').length}</span> rejected,{' '}
              <span className="font-medium">{generatedQuestions.filter(q => !q.reviewed).length}</span> pending review
            </div>
          </Card>

          <div className="grid gap-4">
            {generatedQuestions.map((question) => (
              <Card key={question.id} className={`p-4 ${question.status === 'rejected' ? 'opacity-60' : ''}`}>
                <div className="flex items-start justify-between">
                  <div className="flex-1">
                    <p className="text-gray-900">{question.text}</p>
                    <div className="flex items-center gap-3 mt-3">
                      <Badge variant={question.difficulty === 'easy' ? 'success' : question.difficulty === 'medium' ? 'warning' : 'danger'}>
                        {question.difficulty}
                      </Badge>
                      {question.ai_generated && (
                        <Badge variant="info"><Brain size={12} className="mr-1" />AI Generated</Badge>
                      )}
                      {question.status === 'approved' && <Badge variant="success">Approved</Badge>}
                      {question.status === 'rejected' && <Badge variant="danger">Rejected</Badge>}
                    </div>
                  </div>
                  <div className="flex items-center gap-2 ml-4">
                    {!question.reviewed ? (
                      <>
                        <button
                          onClick={() => handleApproveQuestion(question.id)}
                          className="p-2 text-green-600 hover:bg-green-50 rounded"
                          title="Approve"
                        >
                          <Check size={20} />
                        </button>
                        <button
                          onClick={() => handleRejectQuestion(question.id)}
                          className="p-2 text-red-600 hover:bg-red-50 rounded"
                          title="Reject"
                        >
                          <X size={20} />
                        </button>
                      </>
                    ) : (
                      <Select
                        options={[{ value: '', label: 'Add to exam...' }, ...examOptions]}
                        value=""
                        onChange={(examId) => handleAddToExam(question.id)}
                        className="w-48"
                      />
                    )}
                  </div>
                </div>
              </Card>
            ))}
          </div>

          {generatedQuestions.length === 0 && (
            <div className="text-center py-12 text-gray-500">
              No questions were generated. Please try again with a different PDF.
            </div>
          )}
        </div>
      )}

      {currentStage === 'complete' && (
        <Card>
          <div className="p-8 text-center">
            <div className="w-16 h-16 bg-green-100 rounded-full flex items-center justify-center mx-auto mb-4">
              <Check className="text-green-600" size={32} />
            </div>
            <h3 className="text-xl font-semibold text-gray-900">Questions Added Successfully!</h3>
            <p className="text-gray-500 mt-2">The questions have been added to the selected exam.</p>
            <div className="flex justify-center gap-3 mt-6">
              <Button variant="secondary" onClick={() => navigate('/dashboard/admin/exams')}>
                Back to Exams
              </Button>
              <Button onClick={() => {
                setCurrentStage('upload')
                setFile(null)
                setTopic('')
                setGeneratedQuestions([])
              }}>
                Upload Another PDF
              </Button>
            </div>
          </div>
        </Card>
      )}
    </div>
  )
}