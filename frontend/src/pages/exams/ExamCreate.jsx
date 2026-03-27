import { useState } from 'react'
import { useNavigate, useParams } from 'react-router-dom'
import { examService } from '../../services/examService'

const emptyExam = {
  title: '',
  description: '',
  duration_minutes: 60,
  total_marks: 100,
  passing_marks: 40,
  question_selection_type: 'manual',
  total_questions: 10,
  randomize_questions: false,
  randomize_options: false,
  show_results_immediately: true,
  certificate_enabled: false,
  schedule: {
    start_at: '',
    end_at: '',
    grace_minutes: 5,
  },
  security: {
    prevent_copy_paste: true,
    prevent_right_click: false,
    webcam_required: false,
    allowed_attempts: 1,
  },
}

export default function ExamCreate() {
  const { id } = useParams()
  const isEditing = Boolean(id)
  const navigate = useNavigate()
  const [form, setForm] = useState(emptyExam)
  const [error, setError] = useState('')
  const [loading, setLoading] = useState(false)
  const [activeTab, setActiveTab] = useState('basic')

  const handleChange = (field, value) => {
    if (field.includes('.')) {
      const [parent, child] = field.split('.')
      setForm({ ...form, [parent]: { ...form[parent], [child]: value } })
    } else {
      setForm({ ...form, [field]: value })
    }
  }

  const handleSubmit = async (e) => {
    e.preventDefault()
    if (!form.title.trim()) { setError('Title is required'); return }
    setError('')
    setLoading(true)
    try {
      const payload = { ...form }
      if (payload.schedule.start_at) payload.schedule.start_at = new Date(payload.schedule.start_at).toISOString()
      if (payload.schedule.end_at) payload.schedule.end_at = new Date(payload.schedule.end_at).toISOString()
      if (isEditing) {
        await examService.updateExam(id, payload)
      } else {
        await examService.createExam(payload)
      }
      navigate('/exams')
    } catch (err) {
      setError(err.response?.data?.message || 'Failed to save exam')
    } finally {
      setLoading(false)
    }
  }

  const tabs = [
    { id: 'basic', label: 'Basic Info' },
    { id: 'schedule', label: 'Schedule' },
    { id: 'security', label: 'Security' },
  ]

  return (
    <div className="max-w-3xl">
      <form onSubmit={handleSubmit} className="space-y-5">
        {error && (
          <div className="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded-lg text-sm">{error}</div>
        )}

        <div className="bg-white rounded-xl border border-gray-200">
          <div className="border-b border-gray-200 px-6">
            <div className="flex gap-1">
              {tabs.map((tab) => (
                <button
                  key={tab.id}
                  type="button"
                  onClick={() => setActiveTab(tab.id)}
                  className={`px-4 py-3 text-sm font-medium border-b-2 transition ${
                    activeTab === tab.id
                      ? 'border-primary text-primary'
                      : 'border-transparent text-gray-500 hover:text-gray-700'
                  }`}
                >
                  {tab.label}
                </button>
              ))}
            </div>
          </div>

          <div className="p-6 space-y-4">
            {activeTab === 'basic' && (
              <>
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1.5">Exam Title *</label>
                  <input
                    type="text"
                    required
                    className="w-full px-4 py-2.5 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary focus:border-primary outline-none"
                    value={form.title}
                    onChange={(e) => handleChange('title', e.target.value)}
                    placeholder="e.g., Introduction to Computer Science"
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1.5">Description</label>
                  <textarea
                    rows={3}
                    className="w-full px-4 py-2.5 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary focus:border-primary outline-none resize-none"
                    value={form.description}
                    onChange={(e) => handleChange('description', e.target.value)}
                    placeholder="Brief description of the exam..."
                  />
                </div>
                <div className="grid grid-cols-3 gap-4">
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1.5">Duration (min)</label>
                    <input
                      type="number"
                      min={5}
                      className="w-full px-4 py-2.5 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary focus:border-primary outline-none"
                      value={form.duration_minutes}
                      onChange={(e) => handleChange('duration_minutes', parseInt(e.target.value))}
                    />
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1.5">Total Marks</label>
                    <input
                      type="number"
                      min={1}
                      className="w-full px-4 py-2.5 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary focus:border-primary outline-none"
                      value={form.total_marks}
                      onChange={(e) => handleChange('total_marks', parseFloat(e.target.value))}
                    />
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1.5">Passing Marks</label>
                    <input
                      type="number"
                      min={1}
                      className="w-full px-4 py-2.5 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary focus:border-primary outline-none"
                      value={form.passing_marks}
                      onChange={(e) => handleChange('passing_marks', parseFloat(e.target.value))}
                    />
                  </div>
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1.5">Question Selection</label>
                  <select
                    className="w-full px-4 py-2.5 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary focus:border-primary outline-none"
                    value={form.question_selection_type}
                    onChange={(e) => handleChange('question_selection_type', e.target.value)}
                  >
                    <option value="manual">Manual (assign specific questions)</option>
                    <option value="random">Random from pool</option>
                  </select>
                </div>
                <div className="flex flex-wrap gap-6">
                  {[
                    { field: 'randomize_questions', label: 'Randomize questions' },
                    { field: 'randomize_options', label: 'Randomize options' },
                    { field: 'show_results_immediately', label: 'Show results immediately' },
                    { field: 'certificate_enabled', label: 'Enable certificates' },
                  ].map(({ field, label }) => (
                    <label key={field} className="flex items-center gap-2">
                      <input
                        type="checkbox"
                        className="rounded border-gray-300 text-primary focus:ring-primary"
                        checked={form[field]}
                        onChange={(e) => handleChange(field, e.target.checked)}
                      />
                      <span className="text-sm text-gray-700">{label}</span>
                    </label>
                  ))}
                </div>
              </>
            )}

            {activeTab === 'schedule' && (
              <>
                <div className="grid grid-cols-2 gap-4">
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1.5">Start At</label>
                    <input
                      type="datetime-local"
                      className="w-full px-4 py-2.5 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary focus:border-primary outline-none"
                      value={form.schedule.start_at}
                      onChange={(e) => handleChange('schedule.start_at', e.target.value)}
                    />
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1.5">End At</label>
                    <input
                      type="datetime-local"
                      className="w-full px-4 py-2.5 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary focus:border-primary outline-none"
                      value={form.schedule.end_at}
                      onChange={(e) => handleChange('schedule.end_at', e.target.value)}
                    />
                  </div>
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1.5">Grace Period (minutes)</label>
                  <input
                    type="number"
                    min={0}
                    className="w-32 px-4 py-2.5 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary focus:border-primary outline-none"
                    value={form.schedule.grace_minutes}
                    onChange={(e) => handleChange('schedule.grace_minutes', parseInt(e.target.value))}
                  />
                </div>
              </>
            )}

            {activeTab === 'security' && (
              <>
                <div className="space-y-4">
                  {[
                    { field: 'security.prevent_copy_paste', label: 'Prevent copy/paste' },
                    { field: 'security.prevent_right_click', label: 'Prevent right-click' },
                    { field: 'security.webcam_required', label: 'Require webcam' },
                  ].map(({ field, label }) => (
                    <label key={field} className="flex items-center gap-2">
                      <input
                        type="checkbox"
                        className="rounded border-gray-300 text-primary focus:ring-primary"
                        checked={form.security[field.split('.')[1]]}
                        onChange={(e) => handleChange(field, e.target.checked)}
                      />
                      <span className="text-sm text-gray-700">{label}</span>
                    </label>
                  ))}
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1.5">Max Attempts Allowed</label>
                    <input
                      type="number"
                      min={1}
                      className="w-32 px-4 py-2.5 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary focus:border-primary outline-none"
                      value={form.security.allowed_attempts}
                      onChange={(e) => handleChange('security.allowed_attempts', parseInt(e.target.value))}
                    />
                  </div>
                </div>
              </>
            )}
          </div>
        </div>

        <div className="flex items-center gap-3">
          <button
            type="submit"
            disabled={loading}
            className="px-6 py-2.5 bg-primary text-white rounded-lg font-medium hover:bg-primary-dark disabled:opacity-50 transition"
          >
            {loading ? 'Saving...' : isEditing ? 'Update Exam' : 'Create Exam'}
          </button>
          <button
            type="button"
            onClick={() => navigate('/exams')}
            className="px-6 py-2.5 border border-gray-300 text-gray-600 rounded-lg font-medium hover:bg-gray-50 transition"
          >
            Cancel
          </button>
        </div>
      </form>
    </div>
  )
}
