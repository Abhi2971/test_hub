import { useState, useEffect } from 'react'
import { useNavigate } from 'react-router-dom'
import { useAuth } from '../../contexts/AuthContext'
import { useToast } from '../../contexts/ToastContext'
import { examService } from '../../services/examService'
import api from '../../services/api'
import Button from '../../components/ui/Button'
import Card from '../../components/ui/Card'
import Badge from '../../components/ui/Badge'
import Input from '../../components/ui/Input'
import Select from '../../components/ui/Select'
import Loader from '../../components/ui/Loader'
import { ArrowRight, ArrowLeft, Plus, Save, Upload, Brain, X, GripVertical, Check, Eye, BarChart3 } from 'lucide-react'

const steps = ['Details', 'Questions', 'Security', 'Preview']

export default function CreateExam() {
  const navigate = useNavigate()
  const { user } = useAuth()
  const { showToast } = useToast()
  const [currentStep, setCurrentStep] = useState(0)
  const [loading, setLoading] = useState(false)
  const [saving, setSaving] = useState(false)
  const [examId, setExamId] = useState(null)

  const [formData, setFormData] = useState({
    title: '',
    subject: '',
    topic: '',
    duration: 60,
    total_marks: 100,
    passing_marks: 35,
    result_mode: 'auto',
    show_result: true,
    generate_certificate: false,
    questions: [],
    schedule_start: '',
    schedule_end: '',
    camera_required: false,
    tab_switch_limit: 5,
    fullscreen_required: false,
    access_mode: 'assigned',
    passcode: ''
  })

  const [questionBank, setQuestionBank] = useState([])
  const [questionSearch, setQuestionSearch] = useState('')
  const [selectedQuestions, setSelectedQuestions] = useState([])
  const [showNewQuestion, setShowNewQuestion] = useState(false)
  const [newQuestion, setNewQuestion] = useState({
    text: '',
    options: ['', '', '', ''],
    correct_answer: 0,
    difficulty: 'medium',
    topic: ''
  })
  const [aiLoading, setAiLoading] = useState(false)

  useEffect(() => {
    if (user?.role !== 'teacher') {
      navigate('/dashboard')
      return
    }
    fetchQuestionBank()
  }, [user])

  const fetchQuestionBank = async () => {
    try {
      const response = await api.get('/questions', { params: { limit: 100 } })
      setQuestionBank(response.data.data?.items || [])
    } catch (error) {
      console.error('Failed to fetch question bank', error)
    }
  }

  const filteredQuestions = questionBank.filter(q =>
    q.text?.toLowerCase().includes(questionSearch.toLowerCase())
  )

  const addQuestion = (question) => {
    if (!selectedQuestions.find(q => q.id === question.id)) {
      setSelectedQuestions([...selectedQuestions, question])
    }
  }

  const removeQuestion = (questionId) => {
    setSelectedQuestions(selectedQuestions.filter(q => q.id !== questionId))
  }

  const handleCreateNewQuestion = async () => {
    if (!newQuestion.text || !newQuestion.options[0]) {
      showToast('Please fill in the question', 'error')
      return
    }
    try {
      const response = await api.post('/questions', newQuestion)
      const createdQuestion = response.data.data
      setQuestionBank([createdQuestion, ...questionBank])
      addQuestion(createdQuestion)
      setShowNewQuestion(false)
      setNewQuestion({
        text: '',
        options: ['', '', '', ''],
        correct_answer: 0,
        difficulty: 'medium',
        topic: ''
      })
      showToast('Question created', 'success')
    } catch (error) {
      showToast('Failed to create question', 'error')
    }
  }

  const handleGenerateAI = async () => {
    setAiLoading(true)
    try {
      const response = await api.post('/questions/generate-ai', {
        topic: formData.topic || formData.subject,
        count: 5,
        difficulty: 'medium'
      })
      const generatedQuestions = response.data.data.questions
      setQuestionBank([...generatedQuestions, ...questionBank])
      showToast(`${generatedQuestions.length} AI questions generated`, 'success')
    } catch (error) {
      showToast('Failed to generate AI questions', 'error')
    } finally {
      setAiLoading(false)
    }
  }

  const handleSaveDraft = async () => {
    try {
      setSaving(true)
      const data = { ...formData, questions: selectedQuestions.map(q => q.id), status: 'draft' }
      if (examId) {
        await examService.updateExam(examId, data)
      } else {
        const response = await examService.createExam(data)
        setExamId(response.data.data.id)
      }
      showToast('Exam saved as draft', 'success')
    } catch (error) {
      showToast('Failed to save exam', 'error')
    } finally {
      setSaving(false)
    }
  }

  const handlePublish = async () => {
    try {
      setSaving(true)
      const data = { ...formData, questions: selectedQuestions.map(q => q.id), status: 'published' }
      if (examId) {
        await examService.updateExam(examId, data)
      } else {
        const response = await examService.createExam(data)
        await examService.publishExam(response.data.data.id)
      }
      showToast('Exam published successfully', 'success')
      navigate('/dashboard/teacher/exams')
    } catch (error) {
      showToast('Failed to publish exam', 'error')
    } finally {
      setSaving(false)
    }
  }

  const canProceed = () => {
    if (currentStep === 0) return formData.title && formData.subject
    if (currentStep === 1) return selectedQuestions.length > 0
    if (currentStep === 2) return true
    return true
  }

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">Create Exam</h1>
          <p className="text-gray-500 mt-1">Set up a new exam for your students</p>
        </div>
        <Button variant="secondary" onClick={handleSaveDraft} loading={saving} leftIcon={<Save size={18} />}>
          Save Draft
        </Button>
      </div>

      <div className="flex items-center justify-center gap-4">
        {steps.map((step, idx) => (
          <div key={step} className="flex items-center">
            <div className={`flex items-center gap-2 px-4 py-2 rounded-full ${
              currentStep === idx ? 'bg-blue-600 text-white' :
              currentStep > idx ? 'bg-green-100 text-green-700' :
              'bg-gray-100 text-gray-500'
            }`}>
              {currentStep > idx ? <Check size={16} /> : null}
              <span className="text-sm font-medium">{step}</span>
            </div>
            {idx < steps.length - 1 && <ArrowRight size={16} className="mx-2 text-gray-400" />}
          </div>
        ))}
      </div>

      {currentStep === 0 && (
        <Card>
          <div className="p-6 space-y-6">
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              <Input
                label="Exam Title *"
                value={formData.title}
                onChange={(e) => setFormData(prev => ({ ...prev, title: e.target.value }))}
                placeholder="e.g., Mid-Term Examination"
              />
              <Input
                label="Subject *"
                value={formData.subject}
                onChange={(e) => setFormData(prev => ({ ...prev, subject: e.target.value }))}
                placeholder="e.g., Mathematics"
              />
            </div>
            <Input
              label="Topic"
              value={formData.topic}
              onChange={(e) => setFormData(prev => ({ ...prev, topic: e.target.value }))}
              placeholder="e.g., Algebra, Calculus"
            />
            <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">Duration (minutes)</label>
                <input
                  type="range"
                  min="10"
                  max="180"
                  value={formData.duration}
                  onChange={(e) => setFormData(prev => ({ ...prev, duration: parseInt(e.target.value) }))}
                  className="w-full"
                />
                <div className="text-center mt-1 text-gray-600">{formData.duration} min</div>
              </div>
              <Input
                label="Total Marks"
                type="number"
                value={formData.total_marks}
                onChange={(e) => setFormData(prev => ({ ...prev, total_marks: parseInt(e.target.value) }))}
              />
              <Input
                label="Passing Marks"
                type="number"
                value={formData.passing_marks}
                onChange={(e) => setFormData(prev => ({ ...prev, passing_marks: parseInt(e.target.value) }))}
              />
            </div>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              <Select
                label="Result Mode"
                options={[
                  { value: 'auto', label: 'Automatic' },
                  { value: 'manual', label: 'Manual Review' }
                ]}
                value={formData.result_mode}
                onChange={(value) => setFormData(prev => ({ ...prev, result_mode: value }))}
              />
              <Select
                label="Access Mode"
                options={[
                  { value: 'assigned', label: 'Assigned Students' },
                  { value: 'open', label: 'Open to All' },
                  { value: 'passcode', label: 'Passcode Protected' }
                ]}
                value={formData.access_mode}
                onChange={(value) => setFormData(prev => ({ ...prev, access_mode: value }))}
              />
            </div>
            <div className="space-y-3">
              <label className="flex items-center gap-2">
                <input
                  type="checkbox"
                  checked={formData.show_result}
                  onChange={(e) => setFormData(prev => ({ ...prev, show_result: e.target.checked }))}
                  className="rounded border-gray-300"
                />
                <span className="text-sm text-gray-700">Show result to students after submission</span>
              </label>
              <label className="flex items-center gap-2">
                <input
                  type="checkbox"
                  checked={formData.generate_certificate}
                  onChange={(e) => setFormData(prev => ({ ...prev, generate_certificate: e.target.checked }))}
                  className="rounded border-gray-300"
                />
                <span className="text-sm text-gray-700">Generate certificate on pass</span>
              </label>
            </div>
          </div>
        </Card>
      )}

      {currentStep === 1 && (
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          <Card header="Question Bank">
            <div className="p-4 border-b border-gray-200">
              <div className="flex gap-2">
                <Input
                  placeholder="Search questions..."
                  value={questionSearch}
                  onChange={(e) => setQuestionSearch(e.target.value)}
                  className="flex-1"
                />
                <Button variant="secondary" onClick={() => setShowNewQuestion(true)} leftIcon={<Plus size={16} />}>
                  New
                </Button>
                <Button variant="secondary" onClick={handleGenerateAI} loading={aiLoading} leftIcon={<Brain size={16} />}>
                  AI
                </Button>
              </div>
            </div>
            <div className="max-h-96 overflow-y-auto">
              {filteredQuestions.map((question) => (
                <div
                  key={question.id}
                  className={`p-4 border-b border-gray-100 hover:bg-gray-50 cursor-pointer ${
                    selectedQuestions.find(q => q.id === question.id) ? 'bg-blue-50' : ''
                  }`}
                  onClick={() => addQuestion(question)}
                >
                  <p className="text-sm text-gray-900 line-clamp-2">{question.text}</p>
                  <div className="flex items-center gap-2 mt-2">
                    <Badge variant="neutral" size="sm">{question.difficulty}</Badge>
                    {question.ai_generated && <Badge variant="info" size="sm">AI</Badge>}
                  </div>
                </div>
              ))}
            </div>
          </Card>

          <Card header={`Selected Questions (${selectedQuestions.length})`}>
            {selectedQuestions.length === 0 ? (
              <div className="p-8 text-center text-gray-500">
                No questions selected. Click questions from the bank to add them.
              </div>
            ) : (
              <div className="space-y-2 p-4">
                {selectedQuestions.map((question, idx) => (
                  <div key={question.id} className="flex items-center gap-3 p-3 bg-gray-50 rounded-lg">
                    <GripVertical className="text-gray-400" size={16} />
                    <span className="text-sm text-gray-600">{idx + 1}.</span>
                    <p className="flex-1 text-sm text-gray-900 line-clamp-1">{question.text}</p>
                    <button
                      onClick={() => removeQuestion(question.id)}
                      className="p-1 text-gray-400 hover:text-red-500"
                    >
                      <X size={16} />
                    </button>
                  </div>
                ))}
              </div>
            )}
          </Card>
        </div>
      )}

      {currentStep === 2 && (
        <Card>
          <div className="p-6 space-y-6">
            <h3 className="font-semibold text-gray-900">Schedule</h3>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              <Input
                label="Start Date & Time"
                type="datetime-local"
                value={formData.schedule_start}
                onChange={(e) => setFormData(prev => ({ ...prev, schedule_start: e.target.value }))}
              />
              <Input
                label="End Date & Time"
                type="datetime-local"
                value={formData.schedule_end}
                onChange={(e) => setFormData(prev => ({ ...prev, schedule_end: e.target.value }))}
              />
            </div>

            <h3 className="font-semibold text-gray-900 pt-4">Security Settings</h3>
            <div className="space-y-4">
              <label className="flex items-center gap-2">
                <input
                  type="checkbox"
                  checked={formData.camera_required}
                  onChange={(e) => setFormData(prev => ({ ...prev, camera_required: e.target.checked }))}
                  className="rounded border-gray-300"
                />
                <span className="text-sm text-gray-700">Require camera during exam</span>
              </label>
              <label className="flex items-center gap-2">
                <input
                  type="checkbox"
                  checked={formData.fullscreen_required}
                  onChange={(e) => setFormData(prev => ({ ...prev, fullscreen_required: e.target.checked }))}
                  className="rounded border-gray-300"
                />
                <span className="text-sm text-gray-700">Require fullscreen mode</span>
              </label>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Tab Switch Limit: {formData.tab_switch_limit}
                </label>
                <input
                  type="range"
                  min="0"
                  max="20"
                  value={formData.tab_switch_limit}
                  onChange={(e) => setFormData(prev => ({ ...prev, tab_switch_limit: parseInt(e.target.value) }))}
                  className="w-full"
                />
                <p className="text-xs text-gray-500 mt-1">Auto-submit after exceeding this limit (0 = disabled)</p>
              </div>
              {formData.access_mode === 'passcode' && (
                <Input
                  label="Passcode"
                  value={formData.passcode}
                  onChange={(e) => setFormData(prev => ({ ...prev, passcode: e.target.value }))}
                  placeholder="Enter exam passcode"
                />
              )}
            </div>
          </div>
        </Card>
      )}

      {currentStep === 3 && (
        <Card>
          <div className="p-6 space-y-4">
            <h3 className="font-semibold text-gray-900 text-lg">Exam Summary</h3>
            <div className="grid grid-cols-2 gap-4 text-sm">
              <div><span className="text-gray-500">Title:</span> <span className="font-medium">{formData.title}</span></div>
              <div><span className="text-gray-500">Subject:</span> <span className="font-medium">{formData.subject}</span></div>
              <div><span className="text-gray-500">Duration:</span> <span className="font-medium">{formData.duration} minutes</span></div>
              <div><span className="text-gray-500">Total Marks:</span> <span className="font-medium">{formData.total_marks}</span></div>
              <div><span className="text-gray-500">Passing Marks:</span> <span className="font-medium">{formData.passing_marks}</span></div>
              <div><span className="text-gray-500">Questions:</span> <span className="font-medium">{selectedQuestions.length}</span></div>
              <div><span className="text-gray-500">Result Mode:</span> <span className="font-medium capitalize">{formData.result_mode}</span></div>
              <div><span className="text-gray-500">Access:</span> <span className="font-medium capitalize">{formData.access_mode}</span></div>
            </div>

            <div className="border-t border-gray-200 pt-4">
              <h4 className="font-medium text-gray-900 mb-2">Security Settings</h4>
              <div className="flex flex-wrap gap-2">
                {formData.camera_required && <Badge variant="info">Camera Required</Badge>}
                {formData.fullscreen_required && <Badge variant="info">Fullscreen</Badge>}
                <Badge variant="neutral">Tab limit: {formData.tab_switch_limit}</Badge>
              </div>
            </div>

            <div className="flex gap-3 pt-4">
              <Button variant="secondary" onClick={handleSaveDraft} loading={saving} leftIcon={<Save size={18} />}>
                Save as Draft
              </Button>
              <Button onClick={handlePublish} loading={saving}>
                Publish Exam
              </Button>
            </div>
          </div>
        </Card>
      )}

      {showNewQuestion && (
        <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50 p-4">
          <Card className="w-full max-w-lg max-h-[90vh] overflow-y-auto">
            <div className="p-6 space-y-4">
              <div className="flex items-center justify-between">
                <h3 className="font-semibold text-gray-900">Add New Question</h3>
                <button onClick={() => setShowNewQuestion(false)} className="text-gray-400 hover:text-gray-600">
                  <X size={20} />
                </button>
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Question Text *</label>
                <textarea
                  value={newQuestion.text}
                  onChange={(e) => setNewQuestion(prev => ({ ...prev, text: e.target.value }))}
                  rows={3}
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-200"
                  placeholder="Enter question..."
                />
              </div>
              <div className="space-y-2">
                {newQuestion.options.map((opt, idx) => (
                  <div key={idx} className="flex items-center gap-2">
                    <input
                      type="radio"
                      name="correct"
                      checked={newQuestion.correct_answer === idx}
                      onChange={() => setNewQuestion(prev => ({ ...prev, correct_answer: idx }))}
                      className="rounded border-gray-300"
                    />
                    <Input
                      value={opt}
                      onChange={(e) => {
                        const newOpts = [...newQuestion.options]
                        newOpts[idx] = e.target.value
                        setNewQuestion(prev => ({ ...prev, options: newOpts }))
                      }}
                      placeholder={`Option ${idx + 1}`}
                    />
                  </div>
                ))}
              </div>
              <Select
                label="Difficulty"
                options={[
                  { value: 'easy', label: 'Easy' },
                  { value: 'medium', label: 'Medium' },
                  { value: 'hard', label: 'Hard' }
                ]}
                value={newQuestion.difficulty}
                onChange={(value) => setNewQuestion(prev => ({ ...prev, difficulty: value }))}
              />
              <Button onClick={handleCreateNewQuestion} className="w-full">Add Question</Button>
            </div>
          </Card>
        </div>
      )}

      <div className="flex justify-between">
        <Button
          variant="secondary"
          onClick={() => setCurrentStep(prev => prev - 1)}
          disabled={currentStep === 0}
          leftIcon={<ArrowLeft size={18} />}
        >
          Previous
        </Button>
        <Button
          onClick={() => setCurrentStep(prev => prev + 1)}
          disabled={currentStep === steps.length - 1 || !canProceed()}
          rightIcon={<ArrowRight size={18} />}
        >
          Next
        </Button>
      </div>
    </div>
  )
}