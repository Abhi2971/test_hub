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
import Pagination from '../../components/ui/Pagination'
import Loader from '../../components/ui/Loader'
import { Plus, Edit, Trash2, Eye, Mail, Book } from 'lucide-react'

export default function Teachers() {
  const navigate = useNavigate()
  const { user } = useAuth()
  const { showToast } = useToast()
  const [teachers, setTeachers] = useState([])
  const [loading, setLoading] = useState(true)
  const [pagination, setPagination] = useState({ page: 1, limit: 20, total: 0 })
  const [showCreateModal, setShowCreateModal] = useState(false)
  const [editingTeacher, setEditingTeacher] = useState(null)

  useEffect(() => {
    if (!['admin_college', 'admin_public', 'super_admin'].includes(user?.role)) {
      navigate('/dashboard')
      return
    }
    fetchTeachers()
  }, [user, pagination.page, pagination.limit])

  const fetchTeachers = async () => {
    try {
      setLoading(true)
      const params = { page: pagination.page, limit: pagination.limit }
      const response = await api.get('/teachers', { params })
      setTeachers(response.data.data?.items || [])
      setPagination(prev => ({
        ...prev,
        total: response.data.data?.total || 0
      }))
    } catch (error) {
      showToast('Failed to load teachers', 'error')
    } finally {
      setLoading(false)
    }
  }

  const handleCreateTeacher = async (formData) => {
    try {
      await api.post('/teachers', formData)
      showToast('Teacher added successfully', 'success')
      setShowCreateModal(false)
      fetchTeachers()
    } catch (error) {
      showToast(error.response?.data?.message || 'Failed to add teacher', 'error')
    }
  }

  const handleUpdateTeacher = async (formData) => {
    try {
      await api.patch(`/teachers/${editingTeacher.id}`, formData)
      showToast('Teacher updated successfully', 'success')
      setEditingTeacher(null)
      fetchTeachers()
    } catch (error) {
      showToast('Failed to update teacher', 'error')
    }
  }

  const handleDeactivate = async (teacherId, currentStatus) => {
    try {
      await api.put(`/users/${teacherId}/toggle-active`, { is_active: !currentStatus })
      showToast(`Teacher ${currentStatus ? 'deactivated' : 'activated'}`, 'success')
      fetchTeachers()
    } catch (error) {
      showToast('Failed to update status', 'error')
    }
  }

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">Teachers</h1>
          <p className="text-gray-500 mt-1">Manage teacher accounts and permissions</p>
        </div>
        <Button leftIcon={<Plus size={18} />} onClick={() => setShowCreateModal(true)}>
          Add Teacher
        </Button>
      </div>

      {loading ? (
        <div className="flex justify-center py-12">
          <Loader />
        </div>
      ) : (
        <Card>
          <div className="overflow-x-auto">
            <table className="w-full">
              <thead className="bg-gray-50 border-b border-gray-200">
                <tr>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Name</th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Email</th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Department</th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Designation</th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Exams Created</th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Students</th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Status</th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Actions</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-gray-100">
                {teachers.length === 0 ? (
                  <tr>
                    <td colSpan={8} className="px-6 py-8 text-center text-gray-500">
                      No teachers found
                    </td>
                  </tr>
                ) : (
                  teachers.map((teacher) => (
                    <tr key={teacher.id} className="hover:bg-gray-50">
                      <td className="px-6 py-4">
                        <div className="flex items-center gap-3">
                          <div className="w-10 h-10 rounded-full bg-blue-100 flex items-center justify-center">
                            <span className="text-blue-600 font-medium">
                              {teacher.first_name?.[0]}{teacher.last_name?.[0]}
                            </span>
                          </div>
                          <div>
                            <div className="font-medium text-gray-900">
                              {teacher.first_name} {teacher.last_name}
                            </div>
                          </div>
                        </div>
                      </td>
                      <td className="px-6 py-4 text-gray-600">{teacher.email}</td>
                      <td className="px-6 py-4 text-gray-600">{teacher.department || '-'}</td>
                      <td className="px-6 py-4 text-gray-600">{teacher.designation || '-'}</td>
                      <td className="px-6 py-4 text-gray-600">
                        <div className="flex items-center gap-1">
                          <Book size={14} className="text-gray-400" />
                          {teacher.exams_count || 0}
                        </div>
                      </td>
                      <td className="px-6 py-4 text-gray-600">{teacher.students_count || 0}</td>
                      <td className="px-6 py-4">
                        <Badge variant={teacher.is_active ? 'success' : 'danger'}>
                          {teacher.is_active ? 'Active' : 'Inactive'}
                        </Badge>
                      </td>
                      <td className="px-6 py-4">
                        <div className="flex items-center gap-1">
                          <button
                            onClick={() => setEditingTeacher(teacher)}
                            className="p-1.5 text-gray-500 hover:text-blue-600 hover:bg-blue-50 rounded"
                            title="Edit"
                          >
                            <Edit size={16} />
                          </button>
                          <button
                            onClick={() => navigate(`/dashboard/admin/teachers/${teacher.id}`)}
                            className="p-1.5 text-gray-500 hover:text-purple-600 hover:bg-purple-50 rounded"
                            title="View"
                          >
                            <Eye size={16} />
                          </button>
                          <button
                            onClick={() => handleDeactivate(teacher.id, teacher.is_active)}
                            className={`p-1.5 rounded ${teacher.is_active ? 'text-gray-500 hover:text-red-600 hover:bg-red-50' : 'text-green-600 hover:bg-green-50'}`}
                            title={teacher.is_active ? 'Deactivate' : 'Activate'}
                          >
                            {teacher.is_active ? 'Deactivate' : 'Activate'}
                          </button>
                        </div>
                      </td>
                    </tr>
                  ))
                )}
              </tbody>
            </table>
          </div>

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
      )}

      <CreateTeacherModal
        isOpen={showCreateModal}
        onClose={() => setShowCreateModal(false)}
        onSubmit={handleCreateTeacher}
      />

      <EditTeacherModal
        teacher={editingTeacher}
        onClose={() => setEditingTeacher(null)}
        onSubmit={handleUpdateTeacher}
      />
    </div>
  )
}

function CreateTeacherModal({ isOpen, onClose, onSubmit }) {
  const { showToast } = useToast()
  const [formData, setFormData] = useState({
    first_name: '',
    last_name: '',
    email: '',
    department: '',
    designation: '',
    password: ''
  })
  const [loading, setLoading] = useState(false)

  const handleSubmit = async (e) => {
    e.preventDefault()
    if (!formData.first_name || !formData.email || !formData.password) {
      showToast('Please fill in required fields', 'error')
      return
    }
    setLoading(true)
    try {
      await onSubmit(formData)
      setFormData({ first_name: '', last_name: '', email: '', department: '', designation: '', password: '' })
    } finally {
      setLoading(false)
    }
  }

  return (
    <Modal isOpen={isOpen} onClose={onClose} title="Add Teacher" size="lg">
      <form onSubmit={handleSubmit} className="space-y-4">
        <div className="grid grid-cols-2 gap-4">
          <Input
            label="First Name *"
            value={formData.first_name}
            onChange={(e) => setFormData(prev => ({ ...prev, first_name: e.target.value }))}
            placeholder="First name"
          />
          <Input
            label="Last Name"
            value={formData.last_name}
            onChange={(e) => setFormData(prev => ({ ...prev, last_name: e.target.value }))}
            placeholder="Last name"
          />
        </div>
        <Input
          label="Email *"
          type="email"
          value={formData.email}
          onChange={(e) => setFormData(prev => ({ ...prev, email: e.target.value }))}
          placeholder="teacher@institute.com"
        />
        <Input
          label="Department"
          value={formData.department}
          onChange={(e) => setFormData(prev => ({ ...prev, department: e.target.value }))}
          placeholder="e.g., Computer Science"
        />
        <Input
          label="Designation"
          value={formData.designation}
          onChange={(e) => setFormData(prev => ({ ...prev, designation: e.target.value }))}
          placeholder="e.g., Professor, Lecturer"
        />
        <Input
          label="Password *"
          type="password"
          value={formData.password}
          onChange={(e) => setFormData(prev => ({ ...prev, password: e.target.value }))}
          placeholder="Create password"
        />
        <div className="flex justify-end gap-3 pt-4">
          <Button variant="secondary" onClick={onClose}>Cancel</Button>
          <Button type="submit" loading={loading}>Add Teacher</Button>
        </div>
      </form>
    </Modal>
  )
}

function EditTeacherModal({ teacher, onClose, onSubmit }) {
  const { showToast } = useToast()
  const [formData, setFormData] = useState({
    first_name: '',
    last_name: '',
    email: '',
    department: '',
    designation: ''
  })
  const [loading, setLoading] = useState(false)

  useEffect(() => {
    if (teacher) {
      setFormData({
        first_name: teacher.first_name || '',
        last_name: teacher.last_name || '',
        email: teacher.email || '',
        department: teacher.department || '',
        designation: teacher.designation || ''
      })
    }
  }, [teacher])

  const handleSubmit = async (e) => {
    e.preventDefault()
    if (!formData.first_name || !formData.email) {
      showToast('Please fill in required fields', 'error')
      return
    }
    setLoading(true)
    try {
      await onSubmit(formData)
    } finally {
      setLoading(false)
    }
  }

  if (!teacher) return null

  return (
    <Modal isOpen={!!teacher} onClose={onClose} title="Edit Teacher" size="lg">
      <form onSubmit={handleSubmit} className="space-y-4">
        <div className="grid grid-cols-2 gap-4">
          <Input
            label="First Name *"
            value={formData.first_name}
            onChange={(e) => setFormData(prev => ({ ...prev, first_name: e.target.value }))}
          />
          <Input
            label="Last Name"
            value={formData.last_name}
            onChange={(e) => setFormData(prev => ({ ...prev, last_name: e.target.value }))}
          />
        </div>
        <Input
          label="Email *"
          type="email"
          value={formData.email}
          onChange={(e) => setFormData(prev => ({ ...prev, email: e.target.value }))}
        />
        <Input
          label="Department"
          value={formData.department}
          onChange={(e) => setFormData(prev => ({ ...prev, department: e.target.value }))}
        />
        <Input
          label="Designation"
          value={formData.designation}
          onChange={(e) => setFormData(prev => ({ ...prev, designation: e.target.value }))}
        />
        <div className="flex justify-end gap-3 pt-4">
          <Button variant="secondary" onClick={onClose}>Cancel</Button>
          <Button type="submit" loading={loading}>Save Changes</Button>
        </div>
      </form>
    </Modal>
  )
}