import { useState, useEffect } from 'react'
import { useNavigate } from 'react-router-dom'
import { useAuth } from '../../contexts/AuthContext'
import { useToast } from '../../contexts/ToastContext'
import api from '../../services/api'
import { adminService } from '../../services/adminService'
import { paymentService } from '../../services/paymentService'
import Button from '../../components/ui/Button'
import Card from '../../components/ui/Card'
import Badge from '../../components/ui/Badge'
import Input from '../../components/ui/Input'
import Loader from '../../components/ui/Loader'
import { Save, CreditCard, Zap, Calendar } from 'lucide-react'

export default function InstituteSettings() {
  const navigate = useNavigate()
  const { user, updateUser } = useAuth()
  const { showToast } = useToast()
  const [institute, setInstitute] = useState(null)
  const [subscription, setSubscription] = useState(null)
  const [wallet, setWallet] = useState(null)
  const [aiUsage, setAiUsage] = useState(null)
  const [loading, setLoading] = useState(true)
  const [saving, setSaving] = useState(false)
  const [formData, setFormData] = useState({
    name: '',
    address: '',
    city: '',
    state: '',
    country: '',
    contact_phone: '',
    contact_email: ''
  })

  useEffect(() => {
    if (!['admin_college', 'admin_public'].includes(user?.role)) {
      navigate('/dashboard')
      return
    }
    fetchData()
  }, [user])

  const fetchData = async () => {
    try {
      setLoading(true)
      const [instituteRes, subscriptionRes, walletRes, aiRes] = await Promise.all([
        api.get('/institutes/me'),
        adminService.getSubscription(),
        paymentService.getWallet(),
        api.get('/analytics/ai-usage')
      ])
      setInstitute(instituteRes.data.data)
      setSubscription(subscriptionRes.data.data)
      setWallet(walletRes.data.data)
      setAiUsage(aiRes.data.data)

      if (instituteRes.data.data) {
        setFormData({
          name: instituteRes.data.data.name || '',
          address: instituteRes.data.data.address || '',
          city: instituteRes.data.data.city || '',
          state: instituteRes.data.data.state || '',
          country: instituteRes.data.data.country || '',
          contact_phone: instituteRes.data.data.contact_phone || '',
          contact_email: instituteRes.data.data.contact_email || ''
        })
      }
    } catch (error) {
      showToast('Failed to load settings', 'error')
    } finally {
      setLoading(false)
    }
  }

  const handleSave = async () => {
    try {
      setSaving(true)
      await api.patch('/institutes/me', formData)
      showToast('Settings saved successfully', 'success')
      if (formData.name !== user?.institute?.name) {
        updateUser({ ...user, institute: { ...user.institute, name: formData.name } })
      }
    } catch (error) {
      showToast('Failed to save settings', 'error')
    } finally {
      setSaving(false)
    }
  }

  const handleTopUp = async (amount) => {
    try {
      const response = await paymentService.topUp(amount)
      const { order_id } = response.data.data

      await paymentService.initiateRazorpay(
        response.data.data,
        async (razorpayResponse) => {
          await paymentService.verifyPayment(
            order_id,
            razorpayResponse.razorpay_payment_id,
            razorpayResponse.razorpay_signature
          )
          showToast('Wallet topped up successfully', 'success')
          fetchData()
        },
        (error) => {
          showToast('Payment failed: ' + error.description, 'error')
        }
      )
    } catch (error) {
      showToast('Failed to initiate payment', 'error')
    }
  }

  if (loading) {
    return (
      <div className="flex justify-center py-12">
        <Loader text="Loading settings..." />
      </div>
    )
  }

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold text-gray-900">Institute Settings</h1>
        <p className="text-gray-500 mt-1">Manage your institute profile and subscription</p>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        <div className="lg:col-span-2 space-y-6">
          <Card header="Institute Profile">
            <div className="space-y-4">
              <Input
                label="Institute Name"
                value={formData.name}
                onChange={(e) => setFormData(prev => ({ ...prev, name: e.target.value }))}
              />
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Address</label>
                <textarea
                  value={formData.address}
                  onChange={(e) => setFormData(prev => ({ ...prev, address: e.target.value }))}
                  rows={3}
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-200"
                />
              </div>
              <div className="grid grid-cols-2 gap-4">
                <Input
                  label="City"
                  value={formData.city}
                  onChange={(e) => setFormData(prev => ({ ...prev, city: e.target.value }))}
                />
                <Input
                  label="State"
                  value={formData.state}
                  onChange={(e) => setFormData(prev => ({ ...prev, state: e.target.value }))}
                />
              </div>
              <div className="grid grid-cols-2 gap-4">
                <Input
                  label="Country"
                  value={formData.country}
                  onChange={(e) => setFormData(prev => ({ ...prev, country: e.target.value }))}
                />
                <Input
                  label="Phone"
                  value={formData.contact_phone}
                  onChange={(e) => setFormData(prev => ({ ...prev, contact_phone: e.target.value }))}
                />
              </div>
              <Input
                label="Contact Email"
                type="email"
                value={formData.contact_email}
                onChange={(e) => setFormData(prev => ({ ...prev, contact_email: e.target.value }))}
              />
              <div className="flex justify-end pt-2">
                <Button onClick={handleSave} loading={saving} leftIcon={<Save size={18} />}>
                  Save Changes
                </Button>
              </div>
            </div>
          </Card>
        </div>

        <div className="space-y-6">
          <Card>
            <div className="flex items-center gap-3 mb-4">
              <div className="w-10 h-10 bg-blue-100 rounded-lg flex items-center justify-center">
                <CreditCard className="text-blue-600" size={20} />
              </div>
              <div>
                <h3 className="font-semibold text-gray-900">Subscription</h3>
                <p className="text-sm text-gray-500">Current plan</p>
              </div>
            </div>
            {subscription ? (
              <div className="space-y-3">
                <div className="flex items-center justify-between">
                  <span className="text-gray-600">Plan</span>
                  <Badge variant="info">{subscription.plan?.name || 'Free'}</Badge>
                </div>
                <div className="flex items-center justify-between">
                  <span className="text-gray-600">Status</span>
                  <Badge variant={subscription.status === 'active' ? 'success' : 'warning'}>
                    {subscription.status}
                  </Badge>
                </div>
                <div className="flex items-center justify-between">
                  <span className="text-gray-600">Expires</span>
                  <span className="text-sm text-gray-900">
                    {subscription.expires_at ? new Date(subscription.expires_at).toLocaleDateString() : 'Never'}
                  </span>
                </div>
                {subscription.features?.length > 0 && (
                  <div className="pt-2 border-t border-gray-200">
                    <p className="text-sm font-medium text-gray-700 mb-2">Included Features</p>
                    <ul className="text-sm text-gray-600 space-y-1">
                      {subscription.features.slice(0, 5).map((feature, idx) => (
                        <li key={idx} className="flex items-center gap-2">
                          <span className="text-green-500">✓</span>
                          {feature}
                        </li>
                      ))}
                    </ul>
                  </div>
                )}
              </div>
            ) : (
              <p className="text-sm text-gray-500">No active subscription</p>
            )}
          </Card>

          <Card>
            <div className="flex items-center gap-3 mb-4">
              <div className="w-10 h-10 bg-green-100 rounded-lg flex items-center justify-center">
                <CreditCard className="text-green-600" size={20} />
              </div>
              <div>
                <h3 className="font-semibold text-gray-900">Wallet Balance</h3>
                <p className="text-sm text-gray-500">For AI and paid features</p>
              </div>
            </div>
            {wallet && (
              <div className="space-y-4">
                <div className="text-center py-4">
                  <p className="text-4xl font-bold text-gray-900">₹{wallet.balance}</p>
                  <p className="text-sm text-gray-500 mt-1">Available balance</p>
                </div>
                <div className="grid grid-cols-4 gap-2">
                  {[50, 100, 500, 1000].map((amount) => (
                    <Button
                      key={amount}
                      variant="secondary"
                      size="sm"
                      onClick={() => handleTopUp(amount)}
                    >
                      ₹{amount}
                    </Button>
                  ))}
                </div>
              </div>
            )}
          </Card>

          <Card>
            <div className="flex items-center gap-3 mb-4">
              <div className="w-10 h-10 bg-purple-100 rounded-lg flex items-center justify-center">
                <Zap className="text-purple-600" size={20} />
              </div>
              <div>
                <h3 className="font-semibold text-gray-900">AI Usage</h3>
                <p className="text-sm text-gray-500">This month</p>
              </div>
            </div>
            {aiUsage ? (
              <div className="space-y-3">
                <div className="flex items-center justify-between">
                  <span className="text-gray-600">Questions Generated</span>
                  <span className="font-medium text-gray-900">{aiUsage.questions_generated || 0}</span>
                </div>
                <div className="flex items-center justify-between">
                  <span className="text-gray-600">PDFs Processed</span>
                  <span className="font-medium text-gray-900">{aiUsage.pdfs_processed || 0}</span>
                </div>
                <div className="flex items-center justify-between">
                  <span className="text-gray-600">Cost</span>
                  <span className="font-medium text-gray-900">₹{aiUsage.cost || 0}</span>
                </div>
              </div>
            ) : (
              <p className="text-sm text-gray-500">No AI usage data</p>
            )}
          </Card>
        </div>
      </div>
    </div>
  )
}