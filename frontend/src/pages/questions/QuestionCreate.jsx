import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { questionService } from '../../services/questionService'

export default function QuestionCreate() {
  const navigate = useNavigate()
  const [form, setForm] = useState({
    text: '',
    question_type: 'mcq',
    difficulty: 'medium',
    topic: '',
    options: [
      { option_id: 'opt_0', text: '' },
      { option_id: 'opt_1', text: '' },
      { option_id: 'opt_2', text: '' },
      { option_id: 'opt_3', text: '' },
    ],
    correct_option_id: '',
    explanation: '',
    marks: 1,
  })
  const [error, setError] = useState('')
  const [loading, setLoading] = useState(false)
  const [tab, setTab] = useState('single')

  const handleChange = (field, value) => setForm({ ...form, [field]: value })

  const handleOptionChange = (idx, text) => {
    const options = [...form.options]
    options[idx] = { ...options[idx], text }
    setForm({ ...form, options })
  }

  const handleSubmit = async (e) => {
    e.preventDefault()
    if (!form.text.trim()) { setError('Question text is required'); return }
    if (form.question_type === 'mcq') {
      const filledOptions = form.options.filter((o) => o.text.trim())
      if (filledOptions.length < 2) { setError('At least 2 options are required'); return }
      if (!form.correct_option_id) { setError('Select the correct answer'); return }
    }
    setError('')
    setLoading(true)
    try {
      await questionService.createQuestion(form)
      navigate('/questions')
    } catch (err) {
      setError(err.response?.data?.message || 'Failed to create question')
    } finally {
      setLoading(false)
    }
  }

  const difficultyColors = { easy: 'bg-green-500', medium: 'bg-amber-500', hard: 'bg-red-500' }

  return (
    <div className="max-w-3xl">
      <form onSubmit={handleSubmit} className="space-y-5">
        {error && <div className="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded-lg text-sm">{error}</div>}

        <div className="bg-white rounded-xl border border-gray-200 p-6 space-y-4">
          <div className="grid grid-cols-3 gap-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1.5">Question Type</label>
              <select className="w-full px-4 py-2.5 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary outline-none"
                value={form.question_type} onChange={(e) => handleChange('question_type', e.target.value)}>
                <option value="mcq">MCQ</option>
                <option value="true_false">True/False</option>
              </select>
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1.5">Difficulty</label>
              <div className="flex gap-2 pt-1">
                {['easy', 'medium', 'hard'].map((d) => (
                  <button key={d} type="button" onClick={() => handleChange('difficulty', d)}
                    className={`flex-1 py-2 rounded-lg text-sm font-medium transition border-2 ${form.difficulty === d ? `border-transparent text-white ${difficultyColors[d]}` : 'border-gray-200 text-gray-600 hover:bg-gray-50'}`}>
                    {d.charAt(0).toUpperCase() + d.slice(1)}
                  </button>
                ))}
              </div>
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1.5">Topic</label>
              <input type="text" className="w-full px-4 py-2.5 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary outline-none"
                value={form.topic} onChange={(e) => handleChange('topic', e.target.value)} placeholder="e.g., Algebra" />
            </div>
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1.5">Question Text *</label>
            <textarea rows={3} required className="w-full px-4 py-2.5 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary outline-none resize-none"
              value={form.text} onChange={(e) => handleChange('text', e.target.value)}
              placeholder="Enter your question here..." />
          </div>

          {form.question_type === 'mcq' && (
            <>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">Answer Options *</label>
                <div className="space-y-2">
                  {form.options.map((opt, idx) => (
                    <div key={opt.option_id} className="flex items-center gap-3">
                      <input
                        type="radio"
                        name="correct"
                        checked={form.correct_option_id === opt.option_id}
                        onChange={() => handleChange('correct_option_id', opt.option_id)}
                        className="w-4 h-4 text-primary"
                        title="Mark as correct"
                      />
                      <input
                        type="text"
                        className="flex-1 px-4 py-2.5 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary outline-none"
                        value={opt.text}
                        onChange={(e) => handleOptionChange(idx, e.target.value)}
                        placeholder={`Option ${idx + 1}`}
                      />
                    </div>
                  ))}
                </div>
                <p className="text-xs text-gray-400 mt-2">Select the radio button to mark the correct answer</p>
              </div>
            </>
          )}

          {form.question_type === 'true_false' && (
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">Correct Answer *</label>
              <div className="flex gap-4">
                {['True', 'False'].map((val) => (
                  <label key={val} className="flex items-center gap-2">
                    <input type="radio" name="tf" value={val} checked={form.correct_option_id === val.toLowerCase()}
                      onChange={() => handleChange('correct_option_id', val.toLowerCase())}
                      className="w-4 h-4 text-primary" />
                    <span className="text-sm text-gray-700">{val}</span>
                  </label>
                ))}
              </div>
            </div>
          )}

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1.5">Explanation (optional)</label>
            <textarea rows={2} className="w-full px-4 py-2.5 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary outline-none resize-none"
              value={form.explanation} onChange={(e) => handleChange('explanation', e.target.value)}
              placeholder="Explain the correct answer..." />
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1.5">Marks</label>
            <input type="number" min={1} className="w-24 px-4 py-2.5 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary outline-none"
              value={form.marks} onChange={(e) => handleChange('marks', parseFloat(e.target.value))} />
          </div>
        </div>

        <div className="flex items-center gap-3">
          <button type="submit" disabled={loading}
            className="px-6 py-2.5 bg-primary text-white rounded-lg font-medium hover:bg-primary-dark disabled:opacity-50">
            {loading ? 'Creating...' : 'Create Question'}
          </button>
          <button type="button" onClick={() => navigate('/questions')}
            className="px-6 py-2.5 border border-gray-300 text-gray-600 rounded-lg font-medium hover:bg-gray-50">
            Cancel
          </button>
        </div>
      </form>
    </div>
  )
}
