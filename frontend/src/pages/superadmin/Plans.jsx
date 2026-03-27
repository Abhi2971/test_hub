import { useState, useEffect } from 'react';
import { superadminService } from '../../services/superadminService';
import { useToast } from '../../contexts/ToastContext';
import Loader from '../../components/ui/Loader';

export default function Plans() {
  const { showToast } = useToast();
  const [allPlans, setAllPlans] = useState([]);
  const [loading, setLoading] = useState(true);
  const [showCreateModal, setShowCreateModal] = useState(false);
  const [editingPlan, setEditingPlan] = useState(null);
  const [activeTab, setActiveTab] = useState('institute');

  const plans = allPlans.filter(p => p.is_for === activeTab);

  useEffect(() => {
    fetchPlans();
  }, []);

  const fetchPlans = async () => {
    try {
      setLoading(true);
      const response = await superadminService.getPlans({ is_for: 'all' });
      setAllPlans(response?.data?.items || []);
    } catch (error) {
      showToast('Failed to load plans', 'error');
    } finally {
      setLoading(false);
    }
  };

  const handleCreatePlan = async (formData) => {
    try {
      await superadminService.createPlan({ ...formData, is_for: activeTab });
      showToast('Plan created successfully', 'success');
      setShowCreateModal(false);
      fetchPlans();
    } catch (error) {
      showToast(error.message || 'Failed to create plan', 'error');
    }
  };

  const handleUpdatePlan = async (formData) => {
    try {
      await superadminService.updatePlan(editingPlan.id, formData);
      showToast('Plan updated successfully', 'success');
      setEditingPlan(null);
      fetchPlans();
    } catch (error) {
      showToast(error.message || 'Failed to update plan', 'error');
    }
  };

  const handleDeletePlan = async (planId) => {
    if (!confirm('Are you sure you want to delete this plan?')) return;
    try {
      await superadminService.deletePlan(planId);
      showToast('Plan deleted successfully', 'success');
      fetchPlans();
    } catch (error) {
      showToast('Failed to delete plan', 'error');
    }
  };

  const handleToggleActive = async (plan) => {
    try {
      await superadminService.updatePlan(plan.id, { is_active: !plan.is_active });
      showToast(`Plan ${plan.is_active ? 'deactivated' : 'activated'}`, 'success');
      fetchPlans();
    } catch (error) {
      showToast('Failed to update plan status', 'error');
    }
  };

  const formatPrice = (price) => {
    if (price === 0) return 'Free';
    return new Intl.NumberFormat('en-IN', {
      style: 'currency',
      currency: 'INR',
      maximumFractionDigits: 0
    }).format(price / 100);
  };

  const getFeatureList = (featureFlags) => {
    if (!featureFlags) return [];
    const labels = {
      ebook_access: 'Ebook Access',
      ai_recommendations: 'AI Recommendations',
      pdf_exam_generation: 'PDF Exam Generation',
      certificate_generation: 'Certificate Generation',
      live_monitoring: 'Live Monitoring',
      excel_export: 'Excel Export',
      marketplace_access: 'Marketplace Access',
    };
    return Object.entries(featureFlags)
      .filter(([, enabled]) => enabled)
      .map(([key]) => labels[key] || key);
  };

  const institutePlans = allPlans.filter(p => p.is_for === 'institute');
  const studentPlans = allPlans.filter(p => p.is_for === 'student');

  return (
    <div className="space-y-6">
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <h2 className="text-lg font-semibold text-gray-900">Subscription Plans</h2>
          <p className="text-sm text-gray-500">Manage pricing and features for your platform</p>
        </div>
        <button
          onClick={() => setShowCreateModal(true)}
          className="inline-flex items-center gap-2 px-4 py-2.5 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors font-medium text-sm shadow-sm"
        >
          <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 6v6m0 0v6m0-6h6m-6 0H6" />
          </svg>
          Create {activeTab === 'institute' ? 'Institute' : 'Student'} Plan
        </button>
      </div>

      <div className="bg-white rounded-xl border border-gray-200">
        <div className="border-b border-gray-200">
          <nav className="flex">
            <button
              onClick={() => setActiveTab('institute')}
              className={`px-6 py-3 text-sm font-medium border-b-2 transition-colors ${
                activeTab === 'institute'
                  ? 'border-blue-500 text-blue-600'
                  : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
              }`}
            >
              Institute Plans
              <span className="ml-2 px-2 py-0.5 text-xs rounded-full bg-gray-100">{institutePlans.length}</span>
            </button>
            <button
              onClick={() => setActiveTab('student')}
              className={`px-6 py-3 text-sm font-medium border-b-2 transition-colors ${
                activeTab === 'student'
                  ? 'border-blue-500 text-blue-600'
                  : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
              }`}
            >
              Student Plans
              <span className="ml-2 px-2 py-0.5 text-xs rounded-full bg-gray-100">{studentPlans.length}</span>
            </button>
          </nav>
        </div>

        <div className="grid grid-cols-2 lg:grid-cols-4 gap-4 p-4">
          <div className="bg-gray-50 rounded-lg p-4">
            <p className="text-2xl font-bold text-gray-900">{plans.length}</p>
            <p className="text-xs text-gray-500">{activeTab === 'institute' ? 'Institute' : 'Student'} Plans</p>
          </div>
          <div className="bg-gray-50 rounded-lg p-4">
            <p className="text-2xl font-bold text-green-600">{plans.filter(p => p.is_active).length}</p>
            <p className="text-xs text-gray-500">Active</p>
          </div>
          <div className="bg-gray-50 rounded-lg p-4">
            <p className="text-2xl font-bold text-purple-600">{formatPrice(plans.reduce((sum, p) => sum + (p.price || 0), 0))}</p>
            <p className="text-xs text-gray-500">Total Value</p>
          </div>
          <div className="bg-gray-50 rounded-lg p-4">
            <p className="text-2xl font-bold text-orange-600">
              {activeTab === 'institute' 
                ? plans.reduce((sum, p) => sum + (p.max_students || 0), 0)
                : plans.reduce((sum, p) => sum + (p.ai_usage_limit || 0), 0)}
            </p>
            <p className="text-xs text-gray-500">{activeTab === 'institute' ? 'Max Students' : 'AI Usage'}</p>
          </div>
        </div>
      </div>

      {loading ? (
        <div className="p-12 flex justify-center">
          <Loader />
        </div>
      ) : plans.length === 0 ? (
        <div className="bg-white rounded-xl border border-gray-200 p-12 text-center">
          <svg className="w-12 h-12 text-gray-300 mx-auto mb-3" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M9 7h6m0 10v-3m-3 3h.01M9 17h.01M9 14h.01M12 14h.01M15 11h.01M12 11h.01M9 11h.01M7 21h10a2 2 0 002-2V5a2 2 0 00-2-2H7a2 2 0 00-2 2v14a2 2 0 002 2z" />
          </svg>
          <p className="text-gray-500 font-medium">No plans found</p>
          <p className="text-sm text-gray-400 mt-1">Create your first plan to get started</p>
        </div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {plans.map((plan) => (
            <div key={plan.id} className="bg-white rounded-xl border border-gray-200 overflow-hidden hover:shadow-lg transition-shadow">
              <div className="p-6">
                <div className="flex items-start justify-between mb-4">
                  <div>
                    <h3 className="text-lg font-bold text-gray-900">{plan.name}</h3>
                    <div className="mt-1">
                      <span className="text-3xl font-bold text-gray-900">{formatPrice(plan.price)}</span>
                      <span className="text-gray-500 text-sm">/month</span>
                    </div>
                  </div>
                  <span className={`px-2.5 py-1 text-xs font-semibold rounded-full ${
                    plan.is_active ? 'bg-green-100 text-green-700' : 'bg-gray-100 text-gray-600'
                  }`}>
                    {plan.is_active ? 'Active' : 'Inactive'}
                  </span>
                </div>

                <div className="mb-4 flex items-center gap-2">
                  <span className={`px-2 py-0.5 text-xs font-medium rounded ${
                    plan.is_for === 'student' ? 'bg-purple-100 text-purple-700' : 'bg-blue-100 text-blue-700'
                  }`}>
                    {plan.is_for === 'student' ? 'Student' : 'Institute'}
                  </span>
                  <span className="text-sm text-gray-600">
                    {plan.is_for === 'student' ? (
                      <><span className="font-semibold text-gray-900">{plan.ai_usage_limit || 0}</span> AI uses/mo</>
                    ) : (
                      <><span className="font-semibold text-gray-900">{plan.max_students || 'Unlimited'}</span> students</>
                    )}
                  </span>
                </div>

                <div className="space-y-2 mb-6">
                  <h4 className="text-xs font-semibold text-gray-500 uppercase tracking-wide">Features:</h4>
                  <ul className="space-y-2">
                    {getFeatureList(plan.feature_flags).slice(0, 5).map((feature, idx) => (
                      <li key={idx} className="flex items-center gap-2 text-sm text-gray-600">
                        <svg className="w-4 h-4 text-green-500 flex-shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
                        </svg>
                        {feature}
                      </li>
                    ))}
                    {getFeatureList(plan.feature_flags).length === 0 && (
                      <li className="text-sm text-gray-400">No features listed</li>
                    )}
                  </ul>
                </div>

                <div className="flex gap-2">
                  <button
                    onClick={() => setEditingPlan(plan)}
                    className="flex-1 px-3 py-2 text-sm border border-gray-300 rounded-lg text-gray-700 hover:bg-gray-50 transition-colors"
                  >
                    Edit
                  </button>
                  <button
                    onClick={() => handleToggleActive(plan)}
                    className={`flex-1 px-3 py-2 text-sm rounded-lg transition-colors ${
                      plan.is_active
                        ? 'bg-yellow-50 text-yellow-700 hover:bg-yellow-100'
                        : 'bg-green-50 text-green-700 hover:bg-green-100'
                    }`}
                  >
                    {plan.is_active ? 'Deactivate' : 'Activate'}
                  </button>
                  <button
                    onClick={() => handleDeletePlan(plan.id)}
                    className="px-3 py-2 text-sm text-red-600 hover:bg-red-50 rounded-lg transition-colors"
                  >
                    <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" />
                    </svg>
                  </button>
                </div>
              </div>
            </div>
          ))}
        </div>
      )}

      {showCreateModal && (
        <PlanModal
          isFor={activeTab}
          onClose={() => setShowCreateModal(false)}
          onSubmit={handleCreatePlan}
        />
      )}

      {editingPlan && (
        <PlanModal
          plan={editingPlan}
          isFor={editingPlan.is_for || 'institute'}
          onClose={() => setEditingPlan(null)}
          onSubmit={handleUpdatePlan}
        />
      )}
    </div>
  );
}

function PlanModal({ plan, isFor = 'institute', onClose, onSubmit }) {
  const [formData, setFormData] = useState({
    name: plan?.name || '',
    slug: plan?.slug || '',
    price: plan?.price ? (plan.price / 100).toString() : '',
    duration_days: plan?.duration_days?.toString() || '30',
    max_students: plan?.max_students?.toString() || '100',
    max_teachers: plan?.max_teachers?.toString() || '5',
    exam_limit: plan?.exam_limit?.toString() || '10',
    ai_usage_limit: plan?.ai_usage_limit?.toString() || '50',
    is_active: plan?.is_active ?? true,
  });

  const [featureFlags, setFeatureFlags] = useState({
    ebook_access: plan?.feature_flags?.ebook_access || false,
    ai_recommendations: plan?.feature_flags?.ai_recommendations || false,
    pdf_exam_generation: plan?.feature_flags?.pdf_exam_generation || false,
    certificate_generation: plan?.feature_flags?.certificate_generation || false,
    live_monitoring: plan?.feature_flags?.live_monitoring || false,
    excel_export: plan?.feature_flags?.excel_export || false,
    marketplace_access: plan?.feature_flags?.marketplace_access || false,
  });

  const [loading, setLoading] = useState(false);

  const instituteFeatures = [
    { key: 'ebook_access', label: 'Ebook Access' },
    { key: 'ai_recommendations', label: 'AI Recommendations' },
    { key: 'pdf_exam_generation', label: 'PDF Exam Generation' },
    { key: 'certificate_generation', label: 'Certificate Generation' },
    { key: 'live_monitoring', label: 'Live Monitoring' },
    { key: 'excel_export', label: 'Excel Export' },
    { key: 'marketplace_access', label: 'Marketplace Access' },
  ];

  const studentFeatures = [
    { key: 'ai_recommendations', label: 'AI Recommendations' },
    { key: 'certificate_generation', label: 'Certificate Generation' },
    { key: 'ebook_access', label: 'Ebook Access' },
    { key: 'marketplace_access', label: 'Marketplace Access' },
  ];

  const activeFeatures = isFor === 'student' ? studentFeatures : instituteFeatures;

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!formData.name || !formData.price) return;
    setLoading(true);
    try {
      await onSubmit({
        name: formData.name,
        slug: formData.slug || formData.name.toLowerCase().replace(/[^a-z0-9]+/g, '-'),
        price: Math.round(parseFloat(formData.price) * 100),
        duration_days: parseInt(formData.duration_days) || 30,
        max_students: formData.max_students ? parseInt(formData.max_students) : (isFor === 'student' ? 0 : -1),
        max_teachers: formData.max_teachers ? parseInt(formData.max_teachers) : 5,
        exam_limit: formData.exam_limit ? parseInt(formData.exam_limit) : 10,
        ai_usage_limit: formData.ai_usage_limit ? parseInt(formData.ai_usage_limit) : 50,
        is_active: formData.is_active,
        feature_flags: featureFlags,
        is_for: isFor,
      });
    } finally {
      setLoading(false);
    }
  };

  const toggleFeature = (key) => {
    setFeatureFlags(prev => ({ ...prev, [key]: !prev[key] }));
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/50">
      <div className="bg-white rounded-xl shadow-xl w-full max-w-lg mx-4 max-h-[90vh] overflow-y-auto">
        <div className="px-6 py-4 border-b border-gray-200 sticky top-0 bg-white">
          <h3 className="text-lg font-semibold text-gray-900">
            {plan ? 'Edit Plan' : `Create ${isFor === 'student' ? 'Student' : 'Institute'} Plan`}
          </h3>
        </div>
        <form onSubmit={handleSubmit} className="p-6 space-y-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">Plan Name *</label>
            <input
              type="text"
              value={formData.name}
              onChange={(e) => setFormData({ ...formData, name: e.target.value })}
              className="w-full px-4 py-2.5 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
              placeholder="e.g., Professional"
              required
            />
          </div>
          <div className="grid grid-cols-2 gap-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">Price (₹) *</label>
              <input
                type="number"
                value={formData.price}
                onChange={(e) => setFormData({ ...formData, price: e.target.value })}
                className="w-full px-4 py-2.5 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                placeholder="0"
                required
              />
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">Duration (days)</label>
              <input
                type="number"
                value={formData.duration_days}
                onChange={(e) => setFormData({ ...formData, duration_days: e.target.value })}
                className="w-full px-4 py-2.5 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                placeholder="30"
              />
            </div>
          </div>
          {isFor === 'institute' ? (
            <div className="grid grid-cols-3 gap-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Max Students</label>
                <input
                  type="number"
                  value={formData.max_students}
                  onChange={(e) => setFormData({ ...formData, max_students: e.target.value })}
                  className="w-full px-4 py-2.5 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                  placeholder="-1"
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Max Teachers</label>
                <input
                  type="number"
                  value={formData.max_teachers}
                  onChange={(e) => setFormData({ ...formData, max_teachers: e.target.value })}
                  className="w-full px-4 py-2.5 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                  placeholder="5"
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Exam Limit</label>
                <input
                  type="number"
                  value={formData.exam_limit}
                  onChange={(e) => setFormData({ ...formData, exam_limit: e.target.value })}
                  className="w-full px-4 py-2.5 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                  placeholder="10"
                />
              </div>
            </div>
          ) : (
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">AI Usage Limit</label>
              <input
                type="number"
                value={formData.ai_usage_limit}
                onChange={(e) => setFormData({ ...formData, ai_usage_limit: e.target.value })}
                className="w-full px-4 py-2.5 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                placeholder="50"
              />
            </div>
          )}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">Features</label>
            <div className="grid grid-cols-2 gap-2">
              {activeFeatures.map(({ key, label }) => (
                <label key={key} className="flex items-center gap-2 text-sm cursor-pointer">
                  <input
                    type="checkbox"
                    checked={featureFlags[key]}
                    onChange={() => toggleFeature(key)}
                    className="w-4 h-4 text-blue-600 border-gray-300 rounded focus:ring-blue-500"
                  />
                  <span className="text-gray-700">{label}</span>
                </label>
              ))}
            </div>
          </div>
          <div className="flex items-center gap-2">
            <input
              type="checkbox"
              id="is_active"
              checked={formData.is_active}
              onChange={(e) => setFormData({ ...formData, is_active: e.target.checked })}
              className="w-4 h-4 text-blue-600 border-gray-300 rounded focus:ring-blue-500"
            />
            <label htmlFor="is_active" className="text-sm text-gray-700">Active</label>
          </div>
          <div className="flex justify-end gap-3 pt-4">
            <button
              type="button"
              onClick={onClose}
              className="px-4 py-2.5 border border-gray-300 rounded-lg text-gray-700 hover:bg-gray-50 transition-colors"
            >
              Cancel
            </button>
            <button
              type="submit"
              disabled={loading}
              className="px-4 py-2.5 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors disabled:opacity-50"
            >
              {loading ? 'Saving...' : (plan ? 'Save Changes' : 'Create Plan')}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}
