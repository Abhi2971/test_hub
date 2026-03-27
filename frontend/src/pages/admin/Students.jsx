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
import Pagination from '../../components/ui/Pagination'
import Loader from '../../components/ui/Loader'
import { Plus, Upload, Download, Search, Edit, Trash2, RefreshCw, ToggleLeft, ToggleRight } from 'lucide-react'

export default function Students() {
  const navigate = useNavigate()
  const { user } = useAuth()
  const { showToast } = useToast()
  const [students, setStudents] = useState([])
  const [loading, setLoading] = useState(true)
  const [pagination, setPagination] = useState({ page: 1, limit: 20, total: 0 })
  const [search, setSearch] = useState('')
  const [showUploadModal, setShowUploadModal] = useState(false)
  const [selectedStudents, setSelectedStudents] = useState([])

  useEffect(() => {
    if (!['admin_college', 'admin_public', 'super_admin'].includes(user?.role)) {
      navigate('/dashboard')
      return
    }
    fetchStudents()
  }, [user, pagination.page, pagination.limit, search])

  const fetchStudents = async () => {
    try {
      setLoading(true)
      const params = {
        page: pagination.page,
        limit: pagination.limit,
        ...(search && { search })
      }
      const response = await api.get('/students', { params })
      setStudents(response.data.data?.items || [])
      setPagination(prev => ({
        ...prev,
        total: response.data.data?.total || 0
      }))
    } catch (error) {
      showToast('Failed to load students', 'error')
    } finally {
      setLoading(false)
    }
  }

  const handleToggleActive = async (studentId, currentStatus) => {
    try {
      await api.put(`/users/${studentId}/toggle-active`, { is_active: !currentStatus })
      showToast(`Student ${currentStatus ? 'deactivated' : 'activated'}`, 'success')
      fetchStudents()
    } catch (error) {
      showToast('Failed to update status', 'error')
    }
  }

  const handleResetCredentials = async (studentId) => {
    if (!confirm('Are you sure you want to reset this student\'s credentials?')) return
    try {
      await api.post(`/users/${studentId}/reset-credentials`)
      showToast('Credentials reset successfully', 'success')
    } catch (error) {
      showToast('Failed to reset credentials', 'error')
    }
  }

  const handleBulkUpload = async (file) => {
    try {
      const formData = new FormData()
      formData.append('file', file)
      const response = await api.post('/students/bulk-upload', formData, {
        headers: { 'Content-Type': 'multipart/form-data' }
      })
      showToast(`${response.data.data?.success || 0} students uploaded`, 'success')
      setShowUploadModal(false)
      fetchStudents()
    } catch (error) {
      showToast(error.response?.data?.message || 'Failed to upload students', 'error')
    }
  }

  const handleDownloadTemplate = async () => {
    try {
      const response = await api.get('/students/template', { responseType: 'blob' })
      const url = window.URL.createObjectURL(new Blob([response.data]))
      const link = document.createElement('a')
      link.href = url
      link.setAttribute('download', 'student_template.xlsx')
      document.body.appendChild(link)
      link.click()
      link.remove()
    } catch (error) {
      showToast('Failed to download template', 'error')
    }
  }

  const toggleSelect = (studentId) => {
    setSelectedStudents(prev =>
      prev.includes(studentId)
        ? prev.filter(id => id !== studentId)
        : [...prev, studentId]
    )
  }

  const toggleSelectAll = () => {
    if (selectedStudents.length === students.length) {
      setSelectedStudents([])
    } else {
      setSelectedStudents(students.map(s => s.id))
    }
  }

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">Students</h1>
          <p className="text-gray-500 mt-1">Manage student accounts and enrollments</p>
        </div>
        <div className="flex gap-2">
          <Button variant="secondary" leftIcon={<Download size={18} />} onClick={handleDownloadTemplate}>
            Download Template
          </Button>
          <Button variant="secondary" leftIcon={<Upload size={18} />} onClick={() => setShowUploadModal(true)}>
            Bulk Upload
          </Button>
          <Button leftIcon={<Plus size={18} />} onClick={() => navigate('/dashboard/admin/students/create')}>
            Add Student
          </Button>
        </div>
      </div>

      <Card>
        <div className="p-4 border-b border-gray-200">
          <div className="relative max-w-md">
            <Search className="absolute left-3 top-1/2 -translate-y-1/2 text-gray-400" size={18} />
            <input
              type="text"
              placeholder="Search by name or email..."
              value={search}
              onChange={(e) => setSearch(e.target.value)}
              onKeyDown={(e) => e.key === 'Enter' && fetchStudents()}
              className="w-full pl-10 pr-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-200"
            />
          </div>
        </div>

        {selectedStudents.length > 0 && (
          <div className="p-3 bg-blue-50 border-b border-blue-100 flex items-center justify-between">
            <span className="text-sm text-blue-700">{selectedStudents.length} students selected</span>
            <Button size="sm" variant="danger" leftIcon={<Trash2 size={14} />}>
              Deactivate Selected
            </Button>
          </div>
        )}

        {loading ? (
          <div className="p-8 flex justify-center">
            <Loader />
          </div>
        ) : (
          <div className="overflow-x-auto">
            <table className="w-full">
              <thead className="bg-gray-50 border-b border-gray-200">
                <tr>
                  <th className="px-4 py-3 text-left">
                    <input
                      type="checkbox"
                      checked={selectedStudents.length === students.length && students.length > 0}
                      onChange={toggleSelectAll}
                      className="rounded border-gray-300"
                    />
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Name</th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Email</th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Batch</th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Section</th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Year</th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Status</th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Attempts</th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Actions</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-gray-100">
                {students.length === 0 ? (
                  <tr>
                    <td colSpan={9} className="px-6 py-8 text-center text-gray-500">
                      No students found
                    </td>
                  </tr>
                ) : (
                  students.map((student) => (
                    <tr key={student.id} className="hover:bg-gray-50">
                      <td className="px-4 py-4">
                        <input
                          type="checkbox"
                          checked={selectedStudents.includes(student.id)}
                          onChange={() => toggleSelect(student.id)}
                          className="rounded border-gray-300"
                        />
                      </td>
                      <td className="px-6 py-4">
                        <div className="font-medium text-gray-900">{student.first_name} {student.last_name}</div>
                      </td>
                      <td className="px-6 py-4 text-gray-600">{student.email}</td>
                      <td className="px-6 py-4 text-gray-600">{student.batch || '-'}</td>
                      <td className="px-6 py-4 text-gray-600">{student.section || '-'}</td>
                      <td className="px-6 py-4 text-gray-600">{student.year || '-'}</td>
                      <td className="px-6 py-4">
                        <Badge variant={student.is_active ? 'success' : 'danger'}>
                          {student.is_active ? 'Active' : 'Inactive'}
                        </Badge>
                      </td>
                      <td className="px-6 py-4 text-gray-600">{student.attempts_count || 0}</td>
                      <td className="px-6 py-4">
                        <div className="flex items-center gap-1">
                          <button
                            onClick={() => navigate(`/dashboard/admin/students/${student.id}`)}
                            className="p-1.5 text-gray-500 hover:text-blue-600 hover:bg-blue-50 rounded"
                            title="Edit"
                          >
                            <Edit size={16} />
                          </button>
                          <button
                            onClick={() => handleResetCredentials(student.id)}
                            className="p-1.5 text-gray-500 hover:text-amber-600 hover:bg-amber-50 rounded"
                            title="Reset credentials"
                          >
                            <RefreshCw size={16} />
                          </button>
                          <button
                            onClick={() => handleToggleActive(student.id, student.is_active)}
                            className={`p-1.5 rounded ${student.is_active ? 'text-gray-500 hover:text-red-600 hover:bg-red-50' : 'text-green-600 hover:bg-green-50'}`}
                            title={student.is_active ? 'Deactivate' : 'Activate'}
                          >
                            {student.is_active ? <ToggleLeft size={16} /> : <ToggleRight size={16} />}
                          </button>
                        </div>
                      </td>
                    </tr>
                  ))
                )}
              </tbody>
            </table>
          </div>
        )}

        <div className="p-4 border-t border-gray-200">
          <Pagination
            page={pagination.page}
            totalPages={Math.ceil(pagination.total / pagination.limit)}
            onPageChange={(page) => setPagination(prev => ({ ...prev, page }))}
            perPage={pagination.limit}
            onPerPageChange={(limit) => setPagination(prev => ({ ...prev, limit, page: 1 }))}
            total={pagination.total}
          />
        </div>
      </Card>

      <BulkUploadModal
        isOpen={showUploadModal}
        onClose={() => setShowUploadModal(false)}
        onUpload={handleBulkUpload}
      />
    </div>
  )
}

function BulkUploadModal({ isOpen, onClose, onUpload }) {
  const { showToast } = useToast()
  const [file, setFile] = useState(null)
  const [preview, setPreview] = useState([])
  const [loading, setLoading] = useState(false)

  const handleFileChange = (e) => {
    const selectedFile = e.target.files?.[0]
    if (selectedFile) {
      setFile(selectedFile)
    }
  }

  const handleUpload = async () => {
    if (!file) {
      showToast('Please select a file', 'error')
      return
    }
    setLoading(true)
    try {
      await onUpload(file)
    } finally {
      setLoading(false)
    }
  }

  return (
    <Modal isOpen={isOpen} onClose={onClose} title="Bulk Upload Students" size="lg">
      <div className="space-y-4">
        <div className="border-2 border-dashed border-gray-300 rounded-xl p-6 text-center hover:border-blue-400 transition-colors">
          <input
            type="file"
            accept=".xlsx,.xls"
            onChange={handleFileChange}
            className="hidden"
            id="student-upload"
          />
          <label htmlFor="student-upload" className="cursor-pointer">
            <Upload className="mx-auto text-gray-400 mb-2" size={32} />
            <p className="text-gray-700">
              {file ? file.name : 'Click to upload Excel file'}
            </p>
            <p className="text-sm text-gray-400 mt-1">.xlsx or .xls files</p>
          </label>
        </div>

        {file && (
          <div className="text-sm text-gray-600">
            <p className="font-medium">File ready: {file.name}</p>
            <p className="text-xs text-gray-500 mt-1">Make sure the Excel file follows the template format</p>
          </div>
        )}

        <div className="flex justify-end gap-3 pt-4">
          <Button variant="secondary" onClick={onClose}>Cancel</Button>
          <Button onClick={handleUpload} loading={loading} disabled={!file}>
            Upload Students
          </Button>
        </div>
      </div>
    </Modal>
  )
}