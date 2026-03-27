import { useState, useEffect } from 'react'
import { useNavigate } from 'react-router-dom'
import { useAuth } from '../../contexts/AuthContext'
import { useToast } from '../../contexts/ToastContext'
import api from '../../services/api'
import Button from '../../components/ui/Button'
import Card from '../../components/ui/Card'
import Badge from '../../components/ui/Badge'
import Modal from '../../components/ui/Modal'
import Input from '../../components/ui/Input'
import Select from '../../components/ui/Select'
import Loader from '../../components/ui/Loader'
import { Upload, Edit, Trash2, Eye, Download, BookOpen } from 'lucide-react'

const accessLevelOptions = [
  { value: 'public', label: 'Public' },
  { value: 'students', label: 'Students Only' },
  { value: 'teachers', label: 'Teachers Only' },
  { value: 'all', label: 'All Users' }
]

export default function EbookManagement() {
  const navigate = useNavigate()
  const { user } = useAuth()
  const { showToast } = useToast()
  const [ebooks, setEbooks] = useState([])
  const [loading, setLoading] = useState(true)
  const [showUploadModal, setShowUploadModal] = useState(false)
  const [editingEbook, setEditingEbook] = useState(null)

  useEffect(() => {
    if (!['admin_college', 'admin_public', 'super_admin'].includes(user?.role)) {
      navigate('/dashboard')
      return
    }
    fetchEbooks()
  }, [user])

  const fetchEbooks = async () => {
    try {
      setLoading(true)
      const response = await api.get('/ebooks')
      setEbooks(response.data.data || [])
    } catch (error) {
      showToast('Failed to load ebooks', 'error')
    } finally {
      setLoading(false)
    }
  }

  const handleUpload = async (formData) => {
    try {
      await api.post('/ebooks', formData, {
        headers: { 'Content-Type': 'multipart/form-data' }
      })
      showToast('Ebook uploaded successfully', 'success')
      setShowUploadModal(false)
      fetchEbooks()
    } catch (error) {
      showToast(error.response?.data?.message || 'Failed to upload ebook', 'error')
    }
  }

  const handleUpdate = async (formData) => {
    try {
      await api.patch(`/ebooks/${editingEbook.id}`, formData)
      showToast('Ebook updated successfully', 'success')
      setEditingEbook(null)
      fetchEbooks()
    } catch (error) {
      showToast('Failed to update ebook', 'error')
    }
  }

  const handleDelete = async (ebookId) => {
    if (!confirm('Are you sure you want to delete this ebook?')) return
    try {
      await api.delete(`/ebooks/${ebookId}`)
      showToast('Ebook deleted', 'success')
      fetchEbooks()
    } catch (error) {
      showToast('Failed to delete ebook', 'error')
    }
  }

  const handleToggleAccess = async (ebook) => {
    const levels = ['public', 'students', 'teachers', 'all']
    const currentIndex = levels.indexOf(ebook.access_level)
    const nextLevel = levels[(currentIndex + 1) % levels.length]
    try {
      await api.patch(`/ebooks/${ebook.id}`, { access_level: nextLevel })
      showToast('Access level updated', 'success')
      fetchEbooks()
    } catch (error) {
      showToast('Failed to update access level', 'error')
    }
  }

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">Ebook Management</h1>
          <p className="text-gray-500 mt-1">Manage educational ebooks and materials</p>
        </div>
        <Button leftIcon={<Upload size={18} />} onClick={() => setShowUploadModal(true)}>
          Upload Ebook
        </Button>
      </div>

      {loading ? (
        <div className="flex justify-center py-12">
          <Loader />
        </div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {ebooks.length === 0 ? (
            <div className="col-span-full text-center py-12 text-gray-500">
              No ebooks found. Upload your first ebook to get started.
            </div>
          ) : (
            ebooks.map((ebook) => (
              <Card key={ebook.id} className="overflow-hidden">
                <div className="h-40 bg-gradient-to-br from-blue-50 to-indigo-100 flex items-center justify-center">
                  <BookOpen className="text-blue-300" size={48} />
                </div>
                <div className="p-4">
                  <h3 className="font-semibold text-gray-900 truncate">{ebook.title}</h3>
                  <p className="text-sm text-gray-500 mt-1">{ebook.subject}</p>
                  <div className="flex items-center gap-2 mt-3">
                    <Badge variant="info">{ebook.access_level}</Badge>
                  </div>
                  <div className="flex items-center justify-between mt-4 text-sm text-gray-500">
                    <span>{ebook.views || 0} views</span>
                    <span>{ebook.downloads || 0} downloads</span>
                  </div>
                  <div className="flex gap-2 mt-4">
                    <Button variant="secondary" size="sm" className="flex-1" leftIcon={<Eye size={14} />}>
                      View
                    </Button>
                    <Button variant="secondary" size="sm" className="flex-1" leftIcon={<Download size={14} />}>
                      Download
                    </Button>
                    <button
                      onClick={() => handleToggleAccess(ebook)}
                      className="p-2 text-gray-500 hover:bg-gray-100 rounded"
                      title="Change access"
                    >
                      <Edit size={16} />
                    </button>
                    <button
                      onClick={() => handleDelete(ebook.id)}
                      className="p-2 text-red-500 hover:bg-red-50 rounded"
                      title="Delete"
                    >
                      <Trash2 size={16} />
                    </button>
                  </div>
                </div>
              </Card>
            ))
          )}
        </div>
      )}

      <UploadEbookModal
        isOpen={showUploadModal}
        onClose={() => setShowUploadModal(false)}
        onSubmit={handleUpload}
      />

      <EditEbookModal
        ebook={editingEbook}
        onClose={() => setEditingEbook(null)}
        onSubmit={handleUpdate}
      />
    </div>
  )
}

function UploadEbookModal({ isOpen, onClose, onSubmit }) {
  const { showToast } = useToast()
  const [formData, setFormData] = useState({
    title: '',
    subject: '',
    access_level: 'students',
    file: null
  })
  const [loading, setLoading] = useState(false)

  const handleSubmit = async (e) => {
    e.preventDefault()
    if (!formData.title || !formData.subject || !formData.file) {
      showToast('Please fill in all required fields', 'error')
      return
    }
    setLoading(true)
    try {
      const data = new FormData()
      data.append('title', formData.title)
      data.append('subject', formData.subject)
      data.append('access_level', formData.access_level)
      data.append('file', formData.file)
      await onSubmit(data)
      setFormData({ title: '', subject: '', access_level: 'students', file: null })
    } finally {
      setLoading(false)
    }
  }

  return (
    <Modal isOpen={isOpen} onClose={onClose} title="Upload Ebook" size="lg">
      <form onSubmit={handleSubmit} className="space-y-4">
        <Input
          label="Title *"
          value={formData.title}
          onChange={(e) => setFormData(prev => ({ ...prev, title: e.target.value }))}
          placeholder="Ebook title"
        />
        <Input
          label="Subject *"
          value={formData.subject}
          onChange={(e) => setFormData(prev => ({ ...prev, subject: e.target.value }))}
          placeholder="e.g., Mathematics, Physics"
        />
        <Select
          label="Access Level"
          options={accessLevelOptions}
          value={formData.access_level}
          onChange={(value) => setFormData(prev => ({ ...prev, access_level: value }))}
        />
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">File * (PDF, EPUB)</label>
          <input
            type="file"
            accept=".pdf,.epub"
            onChange={(e) => setFormData(prev => ({ ...prev, file: e.target.files?.[0] }))}
            className="w-full border border-gray-300 rounded-lg p-2"
          />
        </div>
        <div className="flex justify-end gap-3 pt-4">
          <Button variant="secondary" onClick={onClose}>Cancel</Button>
          <Button type="submit" loading={loading}>Upload</Button>
        </div>
      </form>
    </Modal>
  )
}

function EditEbookModal({ ebook, onClose, onSubmit }) {
  const { showToast } = useToast()
  const [formData, setFormData] = useState({
    title: '',
    subject: '',
    access_level: 'students'
  })
  const [loading, setLoading] = useState(false)

  useEffect(() => {
    if (ebook) {
      setFormData({
        title: ebook.title || '',
        subject: ebook.subject || '',
        access_level: ebook.access_level || 'students'
      })
    }
  }, [ebook])

  const handleSubmit = async (e) => {
    e.preventDefault()
    if (!formData.title || !formData.subject) {
      showToast('Please fill in all required fields', 'error')
      return
    }
    setLoading(true)
    try {
      await onSubmit(formData)
    } finally {
      setLoading(false)
    }
  }

  if (!ebook) return null

  return (
    <Modal isOpen={!!ebook} onClose={onClose} title="Edit Ebook" size="lg">
      <form onSubmit={handleSubmit} className="space-y-4">
        <Input
          label="Title *"
          value={formData.title}
          onChange={(e) => setFormData(prev => ({ ...prev, title: e.target.value }))}
        />
        <Input
          label="Subject *"
          value={formData.subject}
          onChange={(e) => setFormData(prev => ({ ...prev, subject: e.target.value }))}
        />
        <Select
          label="Access Level"
          options={accessLevelOptions}
          value={formData.access_level}
          onChange={(value) => setFormData(prev => ({ ...prev, access_level: value }))}
        />
        <div className="flex justify-end gap-3 pt-4">
          <Button variant="secondary" onClick={onClose}>Cancel</Button>
          <Button type="submit" loading={loading}>Save Changes</Button>
        </div>
      </form>
    </Modal>
  )
}