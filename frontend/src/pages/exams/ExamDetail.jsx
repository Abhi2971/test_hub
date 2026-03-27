import { useState, useEffect } from 'react'
import { useParams, Link, useNavigate } from 'react-router-dom'
import { examService } from '../../services/examService'

export default function ExamDetail() {
  const { id } = useParams()
  const navigate = useNavigate()
  const [exam, setExam] = useState(null)
  const [loading, setLoading] = useState(true)
  const [tab, setTab] = useState('overview')

  useEffect(() => {
    examService.getExam(id)
      .then((r) => setExam(r.data))
      .catch(() => navigate('/exams'))
      .finally(() => setLoading(false))
  }, [id])

  if (loading) return <div className="flex justify-center py-12"><div className="animate-spin rounded-full h-10 w-10 border-b-2 border-primary"></div></div>
  if (!exam) return null

  const examData = exam.data

  const handlePublish = async () => {
    await examService.publishExam(id)
    setExam({ ...exam, data: { ...examData, status: 'published' } })
  }

  const handleUnpublish = async () => {
    await examService.unpublishExam(id)
    setExam({ ...exam, data: { ...examData, status: 'draft' } })
  }

  const tabs = [
    { id: 'overview', label: 'Overview' },
    { id: 'questions', label: 'Questions' },
    { id: 'attempts', label: 'Attempts' },
    { id: 'analytics', label: 'Analytics' },
  ]

  return (
    <div className="space-y-5">
      <div className="flex items-start justify-between">
        <div>
          <div className="flex items-center gap-3">
            <h1 className="text-2xl font-bold text-gray-900">{examData.title}</h1>
            <span className={`px-2.5 py-1 rounded-full text-xs font-medium ${
              examData.status === 'active' ? 'bg-green-100 text-green-700' :
              examData.status === 'published' ? 'bg-blue-100 text-blue-700' :
              examData.status === 'draft' ? 'bg-gray-100 text-gray-600' :
              'bg-red-100 text-red-600'
            }`}>{examData.status}</span>
          </div>
          {examData.description && <p className="text-gray-500 mt-1">{examData.description}</p>}
        </div>
        <div className="flex gap-2">
          {examData.status === 'draft' && (
            <button onClick={handlePublish} className="px-4 py-2 bg-green-600 text-white rounded-lg text-sm font-medium hover:bg-green-700">
              Publish
            </button>
          )}
          {examData.status === 'published' && (
            <button onClick={handleUnpublish} className="px-4 py-2 bg-gray-600 text-white rounded-lg text-sm font-medium hover:bg-gray-700">
              Unpublish
            </button>
          )}
          <Link to={`/exams/${id}/edit`} className="px-4 py-2 border border-gray-300 text-gray-600 rounded-lg text-sm font-medium hover:bg-gray-50">
            Edit
          </Link>
        </div>
      </div>

      <div className="grid grid-cols-4 gap-4">
        {[
          { label: 'Duration', value: `${examData.duration_minutes} min` },
          { label: 'Total Marks', value: examData.total_marks },
          { label: 'Passing Marks', value: examData.passing_marks },
          { label: 'Questions', value: examData.question_count || 0 },
        ].map((item, i) => (
          <div key={i} className="bg-white border border-gray-200 rounded-xl p-4 text-center">
            <p className="text-2xl font-bold text-gray-900">{item.value}</p>
            <p className="text-sm text-gray-500 mt-1">{item.label}</p>
          </div>
        ))}
      </div>

      <div className="bg-white rounded-xl border border-gray-200">
        <div className="border-b border-gray-200 px-6">
          <div className="flex gap-1">
            {tabs.map((t) => (
              <button
                key={t.id}
                onClick={() => setTab(t.id)}
                className={`px-4 py-3 text-sm font-medium border-b-2 transition ${
                  tab === t.id ? 'border-primary text-primary' : 'border-transparent text-gray-500 hover:text-gray-700'
                }`}
              >
                {t.label}
              </button>
            ))}
          </div>
        </div>

        <div className="p-6">
          {tab === 'overview' && (
            <div className="space-y-4">
              <div className="grid grid-cols-2 gap-6">
                {[
                  { label: 'Randomize Questions', value: examData.randomize_questions ? 'Yes' : 'No' },
                  { label: 'Randomize Options', value: examData.randomize_options ? 'Yes' : 'No' },
                  { label: 'Show Results Immediately', value: examData.show_results_immediately ? 'Yes' : 'No' },
                  { label: 'Certificates', value: examData.certificate_enabled ? 'Enabled' : 'Disabled' },
                  { label: 'Max Attempts', value: examData.security?.allowed_attempts || 1 },
                  { label: 'Prevent Copy/Paste', value: examData.security?.prevent_copy_paste ? 'Yes' : 'No' },
                ].map((item, i) => (
                  <div key={i} className="flex justify-between py-2 border-b border-gray-100">
                    <span className="text-gray-500">{item.label}</span>
                    <span className="font-medium text-gray-900">{item.value}</span>
                  </div>
                ))}
              </div>
              {examData.schedule?.start_at && (
                <div className="mt-4 p-4 bg-gray-50 rounded-lg">
                  <p className="text-sm text-gray-600">
                    Schedule: {new Date(examData.schedule.start_at).toLocaleString()} → {new Date(examData.schedule.end_at).toLocaleString()}
                  </p>
                </div>
              )}
            </div>
          )}
          {tab === 'questions' && (
            <div className="text-center py-8">
              <p className="text-gray-400 mb-3">{examData.question_count || 0} questions assigned</p>
              <Link to="/questions/create" className="text-primary hover:underline text-sm">Add questions to this exam</Link>
            </div>
          )}
          {tab === 'attempts' && (
            <div className="text-center py-8 text-gray-400">No attempts yet</div>
          )}
          {tab === 'analytics' && (
            <div className="text-center py-8 text-gray-400">Analytics coming soon</div>
          )}
        </div>
      </div>
    </div>
  )
}
