import { useState, useEffect, useRef } from 'react'
import { useParams, useNavigate } from 'react-router-dom'
import { examService } from '../../services/examService'
import { attemptService } from '../../services/attemptService'

export default function TakeExam() {
  const { id } = useParams()
  const navigate = useNavigate()
  const [exam, setExam] = useState(null)
  const [attempt, setAttempt] = useState(null)
  const [questions, setQuestions] = useState([])
  const [answers, setAnswers] = useState({})
  const [currentIndex, setCurrentIndex] = useState(0)
  const [timeLeft, setTimeLeft] = useState(null)
  const [loading, setLoading] = useState(true)
  const [submitting, setSubmitting] = useState(false)
  const [error, setError] = useState('')
  const timerRef = useRef(null)

  useEffect(() => {
    const init = async () => {
      try {
        const examRes = await examService.getExam(id)
        setExam(examRes.data)
        setQuestions(examRes.data.questions || [])

        const attemptRes = await attemptService.startExam(id)
        setAttempt(attemptRes.data)
        setTimeLeft(attemptRes.data.remaining_seconds)
      } catch (err) {
        setError('Failed to start exam. ' + (err.response?.data?.message || ''))
      } finally {
        setLoading(false)
      }
    }
    init()
  }, [id])

  useEffect(() => {
    if (timeLeft === null || timeLeft <= 0) return
    timerRef.current = setInterval(() => {
      setTimeLeft((t) => {
        if (t <= 1) {
          clearInterval(timerRef.current)
          handleAutoSubmit()
          return 0
        }
        return t - 1
      })
    }, 1000)
    return () => clearInterval(timerRef.current)
  }, [timeLeft])

  const handleAutoSubmit = async () => {
    try {
      await attemptService.submitExam(attempt.id)
      navigate(`/results/${attempt.result_id}`)
    } catch {}
  }

  const handleSaveAnswer = async (questionId, optionId) => {
    setAnswers((prev) => ({ ...prev, [questionId]: optionId }))
    try {
      await attemptService.saveAnswer(attempt.id, { [questionId]: optionId })
    } catch {}
  }

  const handleSubmit = async () => {
    if (!confirm('Submit your exam? You cannot change answers after submission.')) return
    setSubmitting(true)
    try {
      clearInterval(timerRef.current)
      await attemptService.submitExam(attempt.id)
      navigate(`/results/${attempt.result_id}`)
    } catch (err) {
      setError('Submission failed: ' + (err.response?.data?.message || ''))
      setSubmitting(false)
    }
  }

  const formatTime = (seconds) => {
    const m = Math.floor(seconds / 60)
    const s = seconds % 60
    return `${m}:${s.toString().padStart(2, '0')}`
  }

  if (loading) return (
    <div className="min-h-screen bg-gray-50 flex items-center justify-center">
      <div className="text-center">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary mx-auto mb-4"></div>
        <p className="text-gray-500">Loading exam...</p>
      </div>
    </div>
  )

  if (error) return (
    <div className="min-h-screen bg-gray-50 flex items-center justify-center">
      <div className="bg-white rounded-xl border border-gray-200 p-8 text-center max-w-md">
        <p className="text-red-600 mb-4">{error}</p>
        <button onClick={() => navigate('/exams')} className="text-primary hover:underline">Back to Exams</button>
      </div>
    </div>
  )

  if (!exam || questions.length === 0) return (
    <div className="min-h-screen bg-gray-50 flex items-center justify-center">
      <div className="text-center">
        <p className="text-gray-500">No questions available for this exam.</p>
        <button onClick={() => navigate('/exams')} className="text-primary hover:underline mt-2">Back</button>
      </div>
    </div>
  )

  const currentQ = questions[currentIndex]

  return (
    <div className="min-h-screen bg-gray-50">
      <header className="bg-white border-b border-gray-200 px-6 py-3 flex items-center justify-between sticky top-0 z-10">
        <h1 className="font-semibold text-gray-900">{exam.title}</h1>
        <div className="flex items-center gap-6">
          <div className="text-sm text-gray-500">
            Question {currentIndex + 1} of {questions.length}
          </div>
          <div className={`px-4 py-1.5 rounded-lg font-mono font-bold text-lg ${
            timeLeft < 300 ? 'bg-red-100 text-red-700' : 'bg-gray-100 text-gray-700'
          }`}>
            {formatTime(timeLeft)}
          </div>
          <button
            onClick={handleSubmit}
            disabled={submitting}
            className="px-4 py-1.5 bg-green-600 text-white rounded-lg text-sm font-medium hover:bg-green-700 disabled:opacity-50"
          >
            {submitting ? 'Submitting...' : 'Submit Exam'}
          </button>
        </div>
      </header>

      <div className="max-w-2xl mx-auto p-6">
        <div className="bg-white rounded-xl border border-gray-200 p-8">
          <p className="text-sm text-gray-500 mb-2">
            Topic: <span className="font-medium">{currentQ.topic || 'General'}</span>
            <span className="ml-2 px-2 py-0.5 bg-gray-100 rounded text-xs">{currentQ.difficulty}</span>
          </p>
          <p className="text-lg font-medium text-gray-900 mb-6">{currentQ.text}</p>

          <div className="space-y-3">
            {currentQ.options?.map((opt) => (
              <button
                key={opt.option_id}
                onClick={() => handleSaveAnswer(currentQ.id, opt.option_id)}
                className={`w-full text-left px-5 py-4 rounded-lg border-2 transition ${
                  answers[currentQ.id] === opt.option_id
                    ? 'border-primary bg-blue-50'
                    : 'border-gray-200 hover:border-gray-300'
                }`}
              >
                <span className={`inline-block w-7 h-7 rounded-full text-center leading-7 mr-3 text-sm font-semibold ${
                  answers[currentQ.id] === opt.option_id
                    ? 'bg-primary text-white'
                    : 'bg-gray-100 text-gray-600'
                }`}>
                  {opt.option_id.replace('opt_', '')}
                </span>
                {opt.text}
              </button>
            ))}
          </div>
        </div>

        <div className="mt-6 flex items-center justify-between">
          <button
            disabled={currentIndex === 0}
            onClick={() => setCurrentIndex((i) => i - 1)}
            className="px-4 py-2 border border-gray-300 rounded-lg text-sm disabled:opacity-50 hover:bg-gray-50"
          >
            Previous
          </button>

          <div className="flex gap-1.5 flex-wrap justify-center">
            {questions.map((q, i) => (
              <button
                key={q.id}
                onClick={() => setCurrentIndex(i)}
                className={`w-8 h-8 rounded text-xs font-medium transition ${
                  i === currentIndex
                    ? 'bg-primary text-white'
                    : answers[q.id]
                    ? 'bg-green-100 text-green-700'
                    : 'bg-gray-100 text-gray-600 hover:bg-gray-200'
                }`}
              >
                {i + 1}
              </button>
            ))}
          </div>

          <button
            disabled={currentIndex === questions.length - 1}
            onClick={() => setCurrentIndex((i) => i + 1)}
            className="px-4 py-2 border border-gray-300 rounded-lg text-sm disabled:opacity-50 hover:bg-gray-50"
          >
            Next
          </button>
        </div>
      </div>
    </div>
  )
}
