import { useState } from 'react'
import { useAuth } from '../contexts/AuthContext'
import { authService } from '../services/authService'

export default function Profile() {
  const { user, updateProfile } = useAuth()
  const [form, setForm] = useState({
    first_name: user?.first_name || '',
    last_name: user?.last_name || '',
    email: user?.email || '',
    phone: user?.phone || '',
  })
  const [passwordForm, setPasswordForm] = useState({ current: '', new: '', confirm: '' })
  const [msg, setMsg] = useState({ type: '', text: '' })
  const [loading, setLoading] = useState(false)

  const handleProfileUpdate = async (e) => {
    e.preventDefault()
    setLoading(true)
    setMsg({ type: '', text: '' })
    try {
      await updateProfile(form)
      setMsg({ type: 'success', text: 'Profile updated successfully!' })
    } catch (err) {
      setMsg({ type: 'error', text: err.response?.data?.message || 'Update failed' })
    } finally {
      setLoading(false)
    }
  }

  const handlePasswordChange = async (e) => {
    e.preventDefault()
    if (passwordForm.new !== passwordForm.confirm) {
      setMsg({ type: 'error', text: 'New passwords do not match' }); return
    }
    setLoading(true)
    try {
      await authService.changePassword(passwordForm.current, passwordForm.new)
      setPasswordForm({ current: '', new: '', confirm: '' })
      setMsg({ type: 'success', text: 'Password changed successfully!' })
    } catch (err) {
      setMsg({ type: 'error', text: err.response?.data?.message || 'Failed to change password' })
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="max-w-2xl space-y-6">
      {msg.text && (
        <div className={`px-4 py-3 rounded-lg text-sm ${msg.type === 'success' ? 'bg-green-50 text-green-700 border border-green-200' : 'bg-red-50 text-red-700 border border-red-200'}`}>
          {msg.text}
        </div>
      )}

      <div className="bg-white rounded-xl border border-gray-200 p-6">
        <h2 className="font-semibold text-gray-900 mb-4">Profile Information</h2>
        <form onSubmit={handleProfileUpdate} className="space-y-4">
          <div className="grid grid-cols-2 gap-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1.5">First Name</label>
              <input type="text" className="w-full px-4 py-2.5 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary outline-none"
                value={form.first_name} onChange={(e) => setForm({ ...form, first_name: e.target.value })} />
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1.5">Last Name</label>
              <input type="text" className="w-full px-4 py-2.5 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary outline-none"
                value={form.last_name} onChange={(e) => setForm({ ...form, last_name: e.target.value })} />
            </div>
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1.5">Email</label>
            <input type="email" className="w-full px-4 py-2.5 border border-gray-300 rounded-lg bg-gray-50"
              value={form.email} disabled />
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1.5">Phone</label>
            <input type="tel" className="w-full px-4 py-2.5 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary outline-none"
              value={form.phone} onChange={(e) => setForm({ ...form, phone: e.target.value })} />
          </div>
          <button type="submit" disabled={loading}
            className="px-6 py-2.5 bg-primary text-white rounded-lg font-medium hover:bg-primary-dark disabled:opacity-50">
            {loading ? 'Saving...' : 'Save Changes'}
          </button>
        </form>
      </div>

      <div className="bg-white rounded-xl border border-gray-200 p-6">
        <h2 className="font-semibold text-gray-900 mb-4">Change Password</h2>
        <form onSubmit={handlePasswordChange} className="space-y-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1.5">Current Password</label>
            <input type="password" className="w-full px-4 py-2.5 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary outline-none"
              value={passwordForm.current} onChange={(e) => setPasswordForm({ ...passwordForm, current: e.target.value })} />
          </div>
          <div className="grid grid-cols-2 gap-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1.5">New Password</label>
              <input type="password" className="w-full px-4 py-2.5 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary outline-none"
                value={passwordForm.new} onChange={(e) => setPasswordForm({ ...passwordForm, new: e.target.value })} />
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1.5">Confirm New Password</label>
              <input type="password" className="w-full px-4 py-2.5 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary outline-none"
                value={passwordForm.confirm} onChange={(e) => setPasswordForm({ ...passwordForm, confirm: e.target.value })} />
            </div>
          </div>
          <button type="submit" disabled={loading}
            className="px-6 py-2.5 bg-gray-900 text-white rounded-lg font-medium hover:bg-gray-800 disabled:opacity-50">
            {loading ? 'Changing...' : 'Change Password'}
          </button>
        </form>
      </div>
    </div>
  )
}
