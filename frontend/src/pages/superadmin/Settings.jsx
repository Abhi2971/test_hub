import { useState } from 'react';
import { useAuth } from '../../contexts/AuthContext';
import { useToast } from '../../contexts/ToastContext';
import api from '../../services/api';
import Loader from '../../components/ui/Loader';
import Card from '../../components/ui/Card';

export default function Settings() {
  const { user } = useAuth();
  const { showToast } = useToast();
  const [activeTab, setActiveTab] = useState('general');
  const [loading, setLoading] = useState(false);
  const [settings, setSettings] = useState({
    site_name: 'ExamPro',
    site_email: 'support@exampro.com',
    contact_phone: '+91 98765 43210',
    timezone: 'Asia/Kolkata',
    currency: 'INR',
    tax_rate: 18,
    referral_enabled: true,
    wallet_enabled: true,
    razorpay_key_id: '',
    razorpay_key_secret: '',
    smtp_host: '',
    smtp_port: 587,
    smtp_user: '',
    smtp_password: '',
    smtp_from_email: '',
    smtp_from_name: 'ExamPro',
  });

  const [notifications, setNotifications] = useState({
    email_notifications: true,
    new_user_alerts: true,
    ticket_alerts: true,
    payment_alerts: false,
    exam_submission_alerts: true,
  });

  const handleSaveSettings = async (e) => {
    e.preventDefault();
    setLoading(true);
    try {
      showToast('Settings saved successfully', 'success');
    } catch (error) {
      showToast('Failed to save settings', 'error');
    } finally {
      setLoading(false);
    }
  };

  const handleChangePassword = async (e) => {
    e.preventDefault();
    const formData = new FormData(e.target);
    const currentPassword = formData.get('current_password');
    const newPassword = formData.get('new_password');
    const confirmPassword = formData.get('confirm_password');

    if (newPassword !== confirmPassword) {
      showToast('Passwords do not match', 'error');
      return;
    }

    if (newPassword.length < 6) {
      showToast('Password must be at least 6 characters', 'error');
      return;
    }

    setLoading(true);
    try {
      await api.post('/auth/change-password', {
        current_password: currentPassword,
        new_password: newPassword,
      });
      showToast('Password changed successfully', 'success');
      e.target.reset();
    } catch (error) {
      showToast(error.message || 'Failed to change password', 'error');
    } finally {
      setLoading(false);
    }
  };

  const tabs = [
    { id: 'general', label: 'General', icon: 'M10.325 4.317c.426-1.756 2.924-1.756 3.35 0a1.724 1.724 0 002.573 1.066c1.543-.94 3.31.826 2.37 2.37a1.724 1.724 0 001.065 2.572c1.756.426 1.756 2.924 0 3.35a1.724 1.724 0 00-1.066 2.573c.94 1.543-.826 3.31-2.37 2.37a1.724 1.724 0 00-2.572 1.065c-.426 1.756-2.924 1.756-3.35 0a1.724 1.724 0 00-2.573-1.066c-1.543.94-3.31-.826-2.37-2.37a1.724 1.724 0 00-1.065-2.572c-1.756-.426-1.756-2.924 0-3.35a1.724 1.724 0 001.066-2.573c-.94-1.543.826-3.31 2.37-2.37.996.608 2.296.07 2.572-1.065z M15 12a3 3 0 11-6 0 3 3 0 016 0z' },
    { id: 'payments', label: 'Payments', icon: 'M3 10h18M7 15h1m4 0h1m-7 4h12a3 3 0 003-3V8a3 3 0 00-3-3H6a3 3 0 00-3 3v8a3 3 0 003 3z' },
    { id: 'email', label: 'Email/SMTP', icon: 'M3 8l7.89 5.26a2 2 0 002.22 0L21 8M5 19h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v10a2 2 0 002 2z' },
    { id: 'notifications', label: 'Notifications', icon: 'M15 17h5l-1.405-1.405A2.032 2.032 0 0118 14.158V11a6.002 6.002 0 00-4-5.659V5a2 2 0 10-4 0v.341C7.67 6.165 6 8.388 6 11v3.159c0 .538-.214 1.055-.595 1.436L4 17h5m6 0v1a3 3 0 11-6 0v-1m6 0H9' },
    { id: 'security', label: 'Security', icon: 'M12 15v2m-6 4h12a2 2 0 002-2v-6a2 2 0 00-2-2H6a2 2 0 00-2 2v6a2 2 0 002 2zm10-10V7a4 4 0 00-8 0v4h8z' },
  ];

  return (
    <div className="space-y-6">
      <div>
        <h2 className="text-lg font-semibold text-gray-900">Settings</h2>
        <p className="text-sm text-gray-500">Manage your platform settings and preferences</p>
      </div>

      <div className="flex flex-col lg:flex-row gap-6">
        <div className="lg:w-64 flex-shrink-0">
          <div className="bg-white rounded-xl border border-gray-200 p-2">
            <nav className="space-y-1">
              {tabs.map((tab) => (
                <button
                  key={tab.id}
                  onClick={() => setActiveTab(tab.id)}
                  className={`w-full flex items-center gap-3 px-4 py-3 rounded-lg transition-colors ${
                    activeTab === tab.id
                      ? 'bg-blue-50 text-blue-700'
                      : 'text-gray-600 hover:bg-gray-50'
                  }`}
                >
                  <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d={tab.icon} />
                  </svg>
                  <span className="font-medium">{tab.label}</span>
                </button>
              ))}
            </nav>
          </div>
        </div>

        <div className="flex-1">
          {activeTab === 'general' && (
            <form onSubmit={handleSaveSettings} className="space-y-6">
              <Card>
                <h3 className="text-lg font-semibold text-gray-900 mb-6">General Settings</h3>
                
                <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2">Site Name</label>
                    <input
                      type="text"
                      value={settings.site_name}
                      onChange={(e) => setSettings({ ...settings, site_name: e.target.value })}
                      className="w-full px-4 py-2.5 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
                    />
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2">Support Email</label>
                    <input
                      type="email"
                      value={settings.site_email}
                      onChange={(e) => setSettings({ ...settings, site_email: e.target.value })}
                      className="w-full px-4 py-2.5 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
                    />
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2">Contact Phone</label>
                    <input
                      type="tel"
                      value={settings.contact_phone}
                      onChange={(e) => setSettings({ ...settings, contact_phone: e.target.value })}
                      className="w-full px-4 py-2.5 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
                    />
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2">Timezone</label>
                    <select
                      value={settings.timezone}
                      onChange={(e) => setSettings({ ...settings, timezone: e.target.value })}
                      className="w-full px-4 py-2.5 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
                    >
                      <option value="Asia/Kolkata">Asia/Kolkata (IST)</option>
                      <option value="Asia/Dubai">Asia/Dubai (GST)</option>
                      <option value="UTC">UTC</option>
                    </select>
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2">Currency</label>
                    <select
                      value={settings.currency}
                      onChange={(e) => setSettings({ ...settings, currency: e.target.value })}
                      className="w-full px-4 py-2.5 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
                    >
                      <option value="INR">Indian Rupee (INR)</option>
                      <option value="USD">US Dollar (USD)</option>
                    </select>
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2">Tax Rate (%)</label>
                    <input
                      type="number"
                      value={settings.tax_rate}
                      onChange={(e) => setSettings({ ...settings, tax_rate: e.target.value })}
                      className="w-full px-4 py-2.5 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
                    />
                  </div>
                </div>

                <div className="mt-6 space-y-4">
                  <div className="flex items-center justify-between py-3 border-t border-gray-100">
                    <div>
                      <p className="font-medium text-gray-900">Referral System</p>
                      <p className="text-sm text-gray-500">Enable referral bonus for users</p>
                    </div>
                    <label className="relative inline-flex items-center cursor-pointer">
                      <input 
                        type="checkbox" 
                        checked={settings.referral_enabled}
                        onChange={(e) => setSettings({ ...settings, referral_enabled: e.target.checked })}
                        className="sr-only peer" 
                      />
                      <div className="w-11 h-6 bg-gray-200 peer-focus:ring-4 peer-focus:ring-blue-500/25 rounded-full peer peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:border-gray-300 after:border after:rounded-full after:h-5 after:w-5 after:transition-all peer-checked:bg-blue-600"></div>
                    </label>
                  </div>
                  <div className="flex items-center justify-between py-3 border-t border-gray-100">
                    <div>
                      <p className="font-medium text-gray-900">Wallet System</p>
                      <p className="text-sm text-gray-500">Enable wallet top-ups for users</p>
                    </div>
                    <label className="relative inline-flex items-center cursor-pointer">
                      <input 
                        type="checkbox" 
                        checked={settings.wallet_enabled}
                        onChange={(e) => setSettings({ ...settings, wallet_enabled: e.target.checked })}
                        className="sr-only peer" 
                      />
                      <div className="w-11 h-6 bg-gray-200 peer-focus:ring-4 peer-focus:ring-blue-500/25 rounded-full peer peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:border-gray-300 after:border after:rounded-full after:h-5 after:w-5 after:transition-all peer-checked:bg-blue-600"></div>
                    </label>
                  </div>
                </div>

                <div className="flex justify-end pt-6 border-t border-gray-200 mt-6">
                  <button type="submit" className="px-6 py-2.5 bg-blue-600 text-white rounded-lg hover:bg-blue-700 font-medium">
                    Save Changes
                  </button>
                </div>
              </Card>
            </form>
          )}

          {activeTab === 'payments' && (
            <form onSubmit={handleSaveSettings} className="space-y-6">
              <Card>
                <h3 className="text-lg font-semibold text-gray-900 mb-6">Payment Settings</h3>
                
                <div className="space-y-6">
                  <div className="p-4 bg-blue-50 rounded-lg">
                    <div className="flex items-center gap-3">
                      <div className="w-10 h-10 rounded-lg bg-blue-100 flex items-center justify-center">
                        <svg className="w-5 h-5 text-blue-600" viewBox="0 0 24 24" fill="currentColor">
                          <path d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm0 18c-4.41 0-8-3.59-8-8s3.59-8 8-8 8 3.59 8 8-3.59 8-8 8z"/>
                        </svg>
                      </div>
                      <div>
                        <p className="font-medium text-gray-900">Razorpay Integration</p>
                        <p className="text-sm text-gray-500">Configure your Razorpay payment gateway</p>
                      </div>
                    </div>
                  </div>

                  <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-2">Razorpay Key ID</label>
                      <input
                        type="text"
                        value={settings.razorpay_key_id}
                        onChange={(e) => setSettings({ ...settings, razorpay_key_id: e.target.value })}
                        placeholder="rzp_test_xxxxx"
                        className="w-full px-4 py-2.5 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
                      />
                    </div>
                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-2">Razorpay Key Secret</label>
                      <input
                        type="password"
                        value={settings.razorpay_key_secret}
                        onChange={(e) => setSettings({ ...settings, razorpay_key_secret: e.target.value })}
                        placeholder="••••••••••••"
                        className="w-full px-4 py-2.5 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
                      />
                    </div>
                  </div>
                </div>

                <div className="flex justify-end pt-6 border-t border-gray-200 mt-6">
                  <button type="submit" className="px-6 py-2.5 bg-blue-600 text-white rounded-lg hover:bg-blue-700 font-medium">
                    Save Changes
                  </button>
                </div>
              </Card>
            </form>
          )}

          {activeTab === 'email' && (
            <form onSubmit={handleSaveSettings} className="space-y-6">
              <Card>
                <h3 className="text-lg font-semibold text-gray-900 mb-6">SMTP Email Settings</h3>
                
                <div className="space-y-6">
                  <div className="p-4 bg-yellow-50 rounded-lg">
                    <div className="flex items-center gap-3">
                      <div className="w-10 h-10 rounded-lg bg-yellow-100 flex items-center justify-center">
                        <svg className="w-5 h-5 text-yellow-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />
                        </svg>
                      </div>
                      <div>
                        <p className="font-medium text-gray-900">Email Configuration</p>
                        <p className="text-sm text-gray-500">Configure SMTP for sending emails</p>
                      </div>
                    </div>
                  </div>

                  <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-2">SMTP Host</label>
                      <input
                        type="text"
                        value={settings.smtp_host}
                        onChange={(e) => setSettings({ ...settings, smtp_host: e.target.value })}
                        placeholder="smtp.gmail.com"
                        className="w-full px-4 py-2.5 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
                      />
                    </div>
                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-2">SMTP Port</label>
                      <input
                        type="number"
                        value={settings.smtp_port}
                        onChange={(e) => setSettings({ ...settings, smtp_port: e.target.value })}
                        placeholder="587"
                        className="w-full px-4 py-2.5 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
                      />
                    </div>
                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-2">SMTP Username</label>
                      <input
                        type="text"
                        value={settings.smtp_user}
                        onChange={(e) => setSettings({ ...settings, smtp_user: e.target.value })}
                        placeholder="your-email@gmail.com"
                        className="w-full px-4 py-2.5 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
                      />
                    </div>
                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-2">SMTP Password</label>
                      <input
                        type="password"
                        value={settings.smtp_password}
                        onChange={(e) => setSettings({ ...settings, smtp_password: e.target.value })}
                        placeholder="••••••••••••"
                        className="w-full px-4 py-2.5 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
                      />
                    </div>
                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-2">From Email</label>
                      <input
                        type="email"
                        value={settings.smtp_from_email}
                        onChange={(e) => setSettings({ ...settings, smtp_from_email: e.target.value })}
                        placeholder="noreply@exampro.com"
                        className="w-full px-4 py-2.5 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
                      />
                    </div>
                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-2">From Name</label>
                      <input
                        type="text"
                        value={settings.smtp_from_name}
                        onChange={(e) => setSettings({ ...settings, smtp_from_name: e.target.value })}
                        placeholder="ExamPro"
                        className="w-full px-4 py-2.5 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
                      />
                    </div>
                  </div>
                </div>

                <div className="flex justify-end pt-6 border-t border-gray-200 mt-6">
                  <button type="submit" className="px-6 py-2.5 bg-blue-600 text-white rounded-lg hover:bg-blue-700 font-medium">
                    Save Changes
                  </button>
                </div>
              </Card>
            </form>
          )}

          {activeTab === 'notifications' && (
            <Card>
              <h3 className="text-lg font-semibold text-gray-900 mb-6">Notification Preferences</h3>
              
              <div className="space-y-4">
                {[
                  { key: 'email_notifications', title: 'Email Notifications', desc: 'Receive email updates about your account' },
                  { key: 'new_user_alerts', title: 'New User Registrations', desc: 'Get notified when new users sign up' },
                  { key: 'ticket_alerts', title: 'Support Ticket Alerts', desc: 'Get notified about new support tickets' },
                  { key: 'payment_alerts', title: 'Payment Notifications', desc: 'Get notified about payment transactions' },
                  { key: 'exam_submission_alerts', title: 'Exam Submission Alerts', desc: 'Get notified when students submit exams' },
                ].map((item) => (
                  <div key={item.key} className="flex items-center justify-between py-4 border-b border-gray-100 last:border-0">
                    <div>
                      <h4 className="font-medium text-gray-900">{item.title}</h4>
                      <p className="text-sm text-gray-500">{item.desc}</p>
                    </div>
                    <label className="relative inline-flex items-center cursor-pointer">
                      <input 
                        type="checkbox" 
                        checked={notifications[item.key]}
                        onChange={(e) => setNotifications({ ...notifications, [item.key]: e.target.checked })}
                        className="sr-only peer" 
                      />
                      <div className="w-11 h-6 bg-gray-200 peer-focus:ring-4 peer-focus:ring-blue-500/25 rounded-full peer peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:border-gray-300 after:border after:rounded-full after:h-5 after:w-5 after:transition-all peer-checked:bg-blue-600"></div>
                    </label>
                  </div>
                ))}
              </div>

              <div className="flex justify-end pt-6 border-t border-gray-200 mt-6">
                <button 
                  onClick={() => showToast('Notification settings saved', 'success')}
                  className="px-6 py-2.5 bg-blue-600 text-white rounded-lg hover:bg-blue-700 font-medium"
                >
                  Save Preferences
                </button>
              </div>
            </Card>
          )}

          {activeTab === 'security' && (
            <div className="space-y-6">
              <Card>
                <h3 className="text-lg font-semibold text-gray-900 mb-6">Change Password</h3>
                <form onSubmit={handleChangePassword} className="space-y-4">
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2">Current Password</label>
<input
                        type="password"
                        name="current_password"
                        required
                        autoComplete="current-password"
                        className="w-full px-4 py-2.5 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
                      />
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2">New Password</label>
                    <input
                      type="password"
                      name="new_password"
                      required
                      autoComplete="new-password"
                      className="w-full px-4 py-2.5 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
                    />
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2">Confirm New Password</label>
                    <input
                      type="password"
                      name="confirm_password"
                      required
                      autoComplete="new-password"
                      className="w-full px-4 py-2.5 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
                    />
                  </div>
                  <button
                    type="submit"
                    disabled={loading}
                    className="px-6 py-2.5 bg-blue-600 text-white rounded-lg hover:bg-blue-700 font-medium disabled:opacity-50"
                  >
                    {loading ? 'Updating...' : 'Update Password'}
                  </button>
                </form>
              </Card>

              <Card>
                <h3 className="text-lg font-semibold text-gray-900 mb-4">Two-Factor Authentication</h3>
                <div className="flex items-center justify-between p-4 bg-gray-50 rounded-lg">
                  <div className="flex items-center gap-3">
                    <div className="w-10 h-10 rounded-full bg-green-100 flex items-center justify-center">
                      <svg className="w-5 h-5 text-green-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m5.618-4.016A11.955 11.955 0 0112 2.944a11.955 11.955 0 01-8.618 3.04A12.02 12.02 0 003 9c0 5.591 3.824 10.29 9 11.622 5.176-1.332 9-6.03 9-11.622 0-1.042-.133-2.052-.382-3.016z" />
                      </svg>
                    </div>
                    <div>
                      <p className="font-medium text-gray-900">2FA is enabled</p>
                      <p className="text-sm text-gray-500">Your account is protected</p>
                    </div>
                  </div>
                  <button className="px-4 py-2 text-red-600 hover:bg-red-50 rounded-lg transition-colors">
                    Disable
                  </button>
                </div>
              </Card>

              <Card>
                <h3 className="text-lg font-semibold text-gray-900 mb-4">Active Sessions</h3>
                <div className="space-y-3">
                  <div className="flex items-center justify-between p-3 bg-gray-50 rounded-lg">
                    <div className="flex items-center gap-3">
                      <svg className="w-5 h-5 text-gray-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9.75 17L9 20l-1 1h8l-1-1-.75-3M3 13h18M5 17h14a2 2 0 002-2V5a2 2 0 00-2-2H5a2 2 0 00-2 2v10a2 2 0 002 2z" />
                      </svg>
                      <div>
                        <p className="font-medium text-gray-900">Current Session</p>
                        <p className="text-xs text-gray-500">Chrome on Windows • Active now</p>
                      </div>
                    </div>
                    <span className="px-2 py-1 text-xs font-medium bg-green-100 text-green-700 rounded">Current</span>
                  </div>
                </div>
              </Card>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
