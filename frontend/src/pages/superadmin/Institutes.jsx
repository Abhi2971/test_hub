import { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { superadminService } from '../../services/superadminService';
import { useToast } from '../../contexts/ToastContext';
import Loader from '../../components/ui/Loader';

export default function Institutes() {
  const { showToast } = useToast();
  const [institutes, setInstitutes] = useState([]);
  const [loading, setLoading] = useState(true);
  const [pagination, setPagination] = useState({ page: 1, limit: 10, total: 0 });
  const [search, setSearch] = useState('');
  const [statusFilter, setStatusFilter] = useState('all');
  const [showCreateModal, setShowCreateModal] = useState(false);
  const [selectedInstitute, setSelectedInstitute] = useState(null);

  useEffect(() => {
    fetchInstitutes();
  }, [pagination.page, pagination.limit, search, statusFilter]);

  const fetchInstitutes = async () => {
    try {
      setLoading(true);
      const params = {
        page: pagination.page,
        per_page: pagination.limit,
        search: search || undefined,
      };
      const response = await superadminService.getInstitutes(params);
      const items = response?.data?.items || response?.items || [];
      setInstitutes(items);
      setPagination(prev => ({
        ...prev,
        total: response?.data?.total || response?.total || 0,
      }));
    } catch (error) {
      showToast(error?.response?.data?.message || error?.message || 'Failed to load institutes', 'error');
    } finally {
      setLoading(false);
    }
  };

  const handleCreateInstitute = async (formData) => {
    try {
      const payload = {
        name: formData.name,
        slug: formData.slug,
        city: formData.city,
        state: formData.state,
        country: formData.country,
        admin: {
          email: formData.admin_email,
          password: formData.admin_password,
          first_name: formData.admin_email?.split('@')[0] || 'Admin',
          last_name: '',
        },
      };
      await superadminService.createInstitute(payload);
      showToast('Institute created successfully', 'success');
      setShowCreateModal(false);
      fetchInstitutes();
    } catch (error) {
      const errorMessage = error?.response?.data?.message || error?.data?.message || error?.message || 'Failed to create institute';
      showToast(errorMessage, 'error');
    }
  };

  const handleToggleStatus = async (institute) => {
    try {
      if (institute.is_suspended) {
        await superadminService.restoreInstitute(institute.id);
        showToast('Institute restored', 'success');
      } else {
        await superadminService.suspendInstitute(institute.id);
        showToast('Institute suspended', 'success');
      }
      fetchInstitutes();
    } catch (error) {
      showToast('Failed to update status', 'error');
    }
  };

  const getStatusBadge = (inst) => {
    if (inst.is_suspended) {
      return <span className="px-2.5 py-1 text-xs font-semibold rounded-full bg-red-100 text-red-700">Suspended</span>;
    }
    if (inst.is_active) {
      return <span className="px-2.5 py-1 text-xs font-semibold rounded-full bg-green-100 text-green-700">Active</span>;
    }
    return <span className="px-2.5 py-1 text-xs font-semibold rounded-full bg-gray-100 text-gray-600">Inactive</span>;
  };

  const getPlanBadge = (plan) => {
    const colors = {
      'enterprise': 'bg-purple-100 text-purple-700',
      'growth': 'bg-blue-100 text-blue-700',
      'starter': 'bg-green-100 text-green-700',
      'free': 'bg-gray-100 text-gray-600',
    };
    return <span className={`px-2.5 py-1 text-xs font-semibold rounded-full ${colors[plan?.toLowerCase()] || colors.free}`}>{plan || 'Free'}</span>;
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <h2 className="text-lg font-semibold text-gray-900">All Institutes</h2>
          <p className="text-sm text-gray-500">Manage and monitor all registered institutes</p>
        </div>
        <button
          onClick={() => setShowCreateModal(true)}
          className="inline-flex items-center gap-2 px-4 py-2.5 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors font-medium text-sm shadow-sm"
        >
          <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 6v6m0 0v6m0-6h6m-6 0H6" />
          </svg>
          Add Institute
        </button>
      </div>

      {/* Stats Cards */}
      <div className="grid grid-cols-2 lg:grid-cols-4 gap-4">
        <div className="bg-white rounded-xl border border-gray-200 p-4">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 rounded-lg bg-blue-100 flex items-center justify-center">
              <svg className="w-5 h-5 text-blue-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 21V5a2 2 0 00-2-2H7a2 2 0 00-2 2v16m14 0h2m-2 0h-5m-9 0H3m2 0h5M9 7h1m-1 4h1m4-4h1m-1 4h1m-5 10v-5a1 1 0 011-1h2a1 1 0 011 1v5m-4 0h4" />
              </svg>
            </div>
            <div>
              <p className="text-2xl font-bold text-gray-900">{pagination.total}</p>
              <p className="text-xs text-gray-500">Total Institutes</p>
            </div>
          </div>
        </div>
        <div className="bg-white rounded-xl border border-gray-200 p-4">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 rounded-lg bg-green-100 flex items-center justify-center">
              <svg className="w-5 h-5 text-green-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
              </svg>
            </div>
            <div>
              <p className="text-2xl font-bold text-gray-900">{institutes.filter(i => i.is_active && !i.is_suspended).length}</p>
              <p className="text-xs text-gray-500">Active</p>
            </div>
          </div>
        </div>
        <div className="bg-white rounded-xl border border-gray-200 p-4">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 rounded-lg bg-purple-100 flex items-center justify-center">
              <svg className="w-5 h-5 text-purple-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8c-1.657 0-3 .895-3 2s1.343 2 3 2 3 .895 3 2-1.343 2-3 2m0-8c1.11 0 2.08.402 2.599 1M12 8V7m0 1v8m0 0v1m0-1c-1.11 0-2.08-.402-2.599-1M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
              </svg>
            </div>
            <div>
              <p className="text-2xl font-bold text-gray-900">{institutes.filter(i => i.plan && i.plan !== 'Free').length}</p>
              <p className="text-xs text-gray-500">Paid Plans</p>
            </div>
          </div>
        </div>
        <div className="bg-white rounded-xl border border-gray-200 p-4">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 rounded-lg bg-red-100 flex items-center justify-center">
              <svg className="w-5 h-5 text-red-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M18.364 18.364A9 9 0 005.636 5.636m12.728 12.728A9 9 0 015.636 5.636m12.728 12.728L5.636 5.636" />
              </svg>
            </div>
            <div>
              <p className="text-2xl font-bold text-gray-900">{institutes.filter(i => i.is_suspended).length}</p>
              <p className="text-xs text-gray-500">Suspended</p>
            </div>
          </div>
        </div>
      </div>

      {/* Filters */}
      <div className="bg-white rounded-xl border border-gray-200">
        <div className="p-4 border-b border-gray-200">
          <div className="flex flex-col sm:flex-row gap-4">
            <div className="flex-1 relative">
              <svg className="absolute left-3 top-1/2 -translate-y-1/2 w-5 h-5 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
              </svg>
              <input
                type="text"
                placeholder="Search institutes by name or slug..."
                value={search}
                onChange={(e) => { setSearch(e.target.value); setPagination(p => ({ ...p, page: 1 })); }}
                className="w-full pl-10 pr-4 py-2.5 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 text-sm"
              />
            </div>
            <select
              value={statusFilter}
              onChange={(e) => setStatusFilter(e.target.value)}
              className="px-4 py-2.5 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 text-sm"
            >
              <option value="all">All Status</option>
              <option value="active">Active</option>
              <option value="suspended">Suspended</option>
            </select>
          </div>
        </div>

        {loading ? (
          <div className="p-12 flex justify-center">
            <Loader />
          </div>
        ) : (
          <>
            <div className="overflow-x-auto">
              <table className="w-full">
                <thead className="bg-gray-50">
                  <tr>
                    <th className="px-6 py-3 text-left text-xs font-semibold text-gray-500 uppercase tracking-wide">Institute</th>
                    <th className="px-6 py-3 text-left text-xs font-semibold text-gray-500 uppercase tracking-wide">Location</th>
                    <th className="px-6 py-3 text-left text-xs font-semibold text-gray-500 uppercase tracking-wide">Plan</th>
                    <th className="px-6 py-3 text-left text-xs font-semibold text-gray-500 uppercase tracking-wide">Status</th>
                    <th className="px-6 py-3 text-left text-xs font-semibold text-gray-500 uppercase tracking-wide">Created</th>
                    <th className="px-6 py-3 text-right text-xs font-semibold text-gray-500 uppercase tracking-wide">Actions</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-gray-100">
                  {institutes.length === 0 ? (
                    <tr>
                      <td colSpan={6} className="px-6 py-12 text-center">
                        <div className="flex flex-col items-center">
                          <svg className="w-12 h-12 text-gray-300 mb-3" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M19 21V5a2 2 0 00-2-2H7a2 2 0 00-2 2v16m14 0h2m-2 0h-5m-9 0H3m2 0h5M9 7h1m-1 4h1m4-4h1m-1 4h1m-5 10v-5a1 1 0 011-1h2a1 1 0 011 1v5m-4 0h4" />
                          </svg>
                          <p className="text-gray-500 font-medium">No institutes found</p>
                          <p className="text-sm text-gray-400 mt-1">Create your first institute to get started</p>
                        </div>
                      </td>
                    </tr>
                  ) : (
                    institutes.map((inst) => (
                      <tr key={inst.id} className="hover:bg-gray-50 transition-colors">
                        <td className="px-6 py-4">
                          <div>
                            <p className="font-semibold text-gray-900">{inst.name}</p>
                            <p className="text-sm text-gray-500">{inst.slug}</p>
                          </div>
                        </td>
                        <td className="px-6 py-4">
                          <p className="text-sm text-gray-900">{inst.city}{inst.city && inst.state ? ', ' : ''}{inst.state}</p>
                          <p className="text-xs text-gray-500">{inst.country}</p>
                        </td>
                        <td className="px-6 py-4">
                          {getPlanBadge(inst.plan)}
                        </td>
                        <td className="px-6 py-4">
                          {getStatusBadge(inst)}
                        </td>
                        <td className="px-6 py-4">
                          <p className="text-sm text-gray-600">
                            {inst.created_at ? new Date(inst.created_at).toLocaleDateString('en-IN', { day: 'numeric', month: 'short', year: 'numeric' }) : '-'}
                          </p>
                        </td>
                        <td className="px-6 py-4">
                          <div className="flex items-center justify-end gap-2">
                            <button
                              onClick={() => setSelectedInstitute(inst)}
                              className="p-2 text-gray-500 hover:text-blue-600 hover:bg-blue-50 rounded-lg transition-colors"
                              title="View"
                            >
                              <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" />
                                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M2.458 12C3.732 7.943 7.523 5 12 5c4.478 0 8.268 2.943 9.542 7-1.274 4.057-5.064 7-9.542 7-4.477 0-8.268-2.943-9.542-7z" />
                              </svg>
                            </button>
                            <button
                              onClick={() => handleToggleStatus(inst)}
                              className={`p-2 rounded-lg transition-colors ${
                                inst.is_suspended
                                  ? 'text-green-600 hover:bg-green-50'
                                  : 'text-red-600 hover:bg-red-50'
                              }`}
                              title={inst.is_suspended ? 'Restore' : 'Suspend'}
                            >
                              {inst.is_suspended ? (
                                <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" />
                                </svg>
                              ) : (
                                <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M18.364 18.364A9 9 0 005.636 5.636m12.728 12.728A9 9 0 015.636 5.636m12.728 12.728L5.636 5.636" />
                                </svg>
                              )}
                            </button>
                          </div>
                        </td>
                      </tr>
                    ))
                  )}
                </tbody>
              </table>
            </div>

            {/* Pagination */}
            {pagination.total_pages > 1 && (
              <div className="px-6 py-4 border-t border-gray-200 flex items-center justify-between">
                <p className="text-sm text-gray-500">
                  Showing {((pagination.page - 1) * pagination.limit) + 1} to {Math.min(pagination.page * pagination.limit, pagination.total)} of {pagination.total} institutes
                </p>
                <div className="flex items-center gap-2">
                  <button
                    onClick={() => setPagination(p => ({ ...p, page: p.page - 1 }))}
                    disabled={pagination.page === 1}
                    className="px-3 py-1.5 text-sm border border-gray-300 rounded-lg hover:bg-gray-50 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
                  >
                    Previous
                  </button>
                  <span className="px-3 py-1.5 text-sm font-medium">
                    Page {pagination.page} of {pagination.total_pages}
                  </span>
                  <button
                    onClick={() => setPagination(p => ({ ...p, page: p.page + 1 }))}
                    disabled={pagination.page >= pagination.total_pages}
                    className="px-3 py-1.5 text-sm border border-gray-300 rounded-lg hover:bg-gray-50 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
                  >
                    Next
                  </button>
                </div>
              </div>
            )}
          </>
        )}
      </div>

      {/* Create Modal */}
      {showCreateModal && (
        <CreateInstituteModal
          onClose={() => setShowCreateModal(false)}
          onSubmit={handleCreateInstitute}
        />
      )}

      {/* Detail Modal */}
      {selectedInstitute && (
        <InstituteDetailModal
          institute={selectedInstitute}
          onClose={() => setSelectedInstitute(null)}
        />
      )}
    </div>
  );
}

function CreateInstituteModal({ onClose, onSubmit }) {
  const [formData, setFormData] = useState({
    name: '',
    slug: '',
    city: '',
    state: '',
    country: 'India',
    admin_email: '',
    admin_password: ''
  });
  const [loading, setLoading] = useState(false);

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!formData.name || !formData.slug || !formData.admin_email || !formData.admin_password) {
      return;
    }
    setLoading(true);
    try {
      await onSubmit(formData);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/50">
      <div className="bg-white rounded-xl shadow-xl w-full max-w-lg mx-4">
        <div className="px-6 py-4 border-b border-gray-200">
          <h3 className="text-lg font-semibold text-gray-900">Create New Institute</h3>
        </div>
        <form onSubmit={handleSubmit} className="p-6 space-y-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">Institute Name *</label>
            <input
              type="text"
              value={formData.name}
              onChange={(e) => setFormData({ ...formData, name: e.target.value })}
              className="w-full px-4 py-2.5 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
              placeholder="Enter institute name"
            />
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">Slug *</label>
            <input
              type="text"
              value={formData.slug}
              onChange={(e) => setFormData({ ...formData, slug: e.target.value.toLowerCase().replace(/[^a-z0-9-]/g, '-') })}
              className="w-full px-4 py-2.5 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
              placeholder="institute-slug"
            />
          </div>
          <div className="grid grid-cols-2 gap-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">City</label>
              <input
                type="text"
                value={formData.city}
                onChange={(e) => setFormData({ ...formData, city: e.target.value })}
                className="w-full px-4 py-2.5 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
              />
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">State</label>
              <input
                type="text"
                value={formData.state}
                onChange={(e) => setFormData({ ...formData, state: e.target.value })}
                className="w-full px-4 py-2.5 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
              />
            </div>
          </div>
          <div className="border-t border-gray-200 pt-4">
            <h4 className="font-medium text-gray-900 mb-3">Admin Account</h4>
            <div className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Admin Email *</label>
                <input
                  type="email"
                  value={formData.admin_email}
                  onChange={(e) => setFormData({ ...formData, admin_email: e.target.value })}
                  className="w-full px-4 py-2.5 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                  placeholder="admin@institute.com"
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Admin Password *</label>
                <input
                  type="password"
                  value={formData.admin_password}
                  onChange={(e) => setFormData({ ...formData, admin_password: e.target.value })}
                  className="w-full px-4 py-2.5 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                  placeholder="Create password"
                />
              </div>
            </div>
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
              {loading ? 'Creating...' : 'Create Institute'}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}

function InstituteDetailModal({ institute, onClose }) {
  if (!institute) return null;

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/50">
      <div className="bg-white rounded-xl shadow-xl w-full max-w-lg mx-4">
        <div className="px-6 py-4 border-b border-gray-200 flex items-center justify-between">
          <h3 className="text-lg font-semibold text-gray-900">Institute Details</h3>
          <button onClick={onClose} className="text-gray-400 hover:text-gray-600">
            <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
            </svg>
          </button>
        </div>
        <div className="p-6">
          <div className="space-y-4">
            <div className="grid grid-cols-2 gap-4">
              <div>
                <p className="text-xs text-gray-500 uppercase tracking-wide">Name</p>
                <p className="font-medium text-gray-900">{institute.name}</p>
              </div>
              <div>
                <p className="text-xs text-gray-500 uppercase tracking-wide">Slug</p>
                <p className="font-medium text-gray-900">{institute.slug}</p>
              </div>
              <div>
                <p className="text-xs text-gray-500 uppercase tracking-wide">City</p>
                <p className="text-gray-700">{institute.city || '-'}</p>
              </div>
              <div>
                <p className="text-xs text-gray-500 uppercase tracking-wide">State</p>
                <p className="text-gray-700">{institute.state || '-'}</p>
              </div>
              <div>
                <p className="text-xs text-gray-500 uppercase tracking-wide">Country</p>
                <p className="text-gray-700">{institute.country || '-'}</p>
              </div>
              <div>
                <p className="text-xs text-gray-500 uppercase tracking-wide">Plan</p>
                <p className="text-gray-700">{institute.plan || 'Free'}</p>
              </div>
              <div>
                <p className="text-xs text-gray-500 uppercase tracking-wide">Status</p>
                <p className="text-gray-700">{institute.is_suspended ? 'Suspended' : institute.is_active ? 'Active' : 'Inactive'}</p>
              </div>
              <div>
                <p className="text-xs text-gray-500 uppercase tracking-wide">Created</p>
                <p className="text-gray-700">
                  {institute.created_at ? new Date(institute.created_at).toLocaleDateString('en-IN', { day: 'numeric', month: 'short', year: 'numeric' }) : '-'}
                </p>
              </div>
            </div>
          </div>
          <div className="flex justify-end mt-6">
            <button
              onClick={onClose}
              className="px-4 py-2.5 border border-gray-300 rounded-lg text-gray-700 hover:bg-gray-50 transition-colors"
            >
              Close
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}
