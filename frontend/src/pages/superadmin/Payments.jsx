import { useState, useEffect } from 'react';
import { superadminService } from '../../services/superadminService';
import Loader from '../../components/ui/Loader';

export default function Payments() {
  const [activeTab, setActiveTab] = useState('payments');
  const [payments, setPayments] = useState([]);
  const [subscriptions, setSubscriptions] = useState([]);
  const [loading, setLoading] = useState(true);
  const [pagination, setPagination] = useState({ page: 1, limit: 20, total: 0, total_pages: 0 });
  const [filters, setFilters] = useState({ status: '', purpose: '', entity_type: '' });

  useEffect(() => {
    if (activeTab === 'payments') {
      loadPayments();
    } else {
      loadSubscriptions();
    }
  }, [pagination.page, filters, activeTab]);

  const loadPayments = async () => {
    setLoading(true);
    try {
      const params = {
        page: pagination.page,
        limit: pagination.limit,
        ...(filters.status && { status: filters.status }),
        ...(filters.purpose && { purpose: filters.purpose }),
      };
      const response = await superadminService.getPayments(params);
      setPayments(response?.data?.items || []);
      setPagination(prev => ({
        ...prev,
        total: response?.data?.total || 0,
        total_pages: response?.data?.total_pages || 0,
      }));
    } catch (error) {
      console.error('Failed to load payments:', error);
    } finally {
      setLoading(false);
    }
  };

  const loadSubscriptions = async () => {
    setLoading(true);
    try {
      const params = {
        page: pagination.page,
        limit: pagination.limit,
        ...(filters.status && { status: filters.status }),
        ...(filters.entity_type && { entity_type: filters.entity_type }),
      };
      const response = await superadminService.getSubscriptions(params);
      setSubscriptions(response?.data?.items || []);
      setPagination(prev => ({
        ...prev,
        total: response?.data?.total || 0,
        total_pages: response?.data?.total_pages || 0,
      }));
    } catch (error) {
      console.error('Failed to load subscriptions:', error);
    } finally {
      setLoading(false);
    }
  };

  const getStatusBadge = (status) => {
    const styles = {
      completed: 'bg-green-100 text-green-700',
      pending: 'bg-yellow-100 text-yellow-700',
      failed: 'bg-red-100 text-red-700',
      refunded: 'bg-gray-100 text-gray-700',
      active: 'bg-green-100 text-green-700',
      expired: 'bg-red-100 text-red-700',
      cancelled: 'bg-gray-100 text-gray-700',
    };
    return <span className={`px-2.5 py-1 text-xs font-semibold rounded-full ${styles[status] || 'bg-gray-100 text-gray-700'}`}>{status?.charAt(0).toUpperCase() + status?.slice(1) || 'Unknown'}</span>;
  };

  const getPurposeLabel = (purpose) => {
    const labels = {
      subscription: 'Subscription',
      wallet_topup: 'Wallet Topup',
      exam_purchase: 'Exam Purchase',
      ebook_purchase: 'Ebook Purchase',
    };
    return labels[purpose] || purpose;
  };

  const formatCurrency = (amount) => {
    return new Intl.NumberFormat('en-IN', {
      style: 'currency',
      currency: 'INR',
      maximumFractionDigits: 0,
    }).format((amount || 0) / 100);
  };

  const formatDate = (date) => {
    if (!date) return '-';
    return new Date(date).toLocaleDateString('en-IN', {
      day: 'numeric',
      month: 'short',
      year: 'numeric',
      hour: '2-digit',
      minute: '2-digit',
    });
  };

  const totalAmount = payments.reduce((sum, p) => sum + (p.amount || 0), 0);
  const completedPayments = payments.filter(p => p.status === 'completed');
  const completedAmount = completedPayments.reduce((sum, p) => sum + (p.amount || 0), 0);

  const activeSubscriptions = subscriptions.filter(s => s.status === 'active');
  const expiredSubscriptions = subscriptions.filter(s => s.status === 'expired');

  return (
    <div className="space-y-6">
      {/* Header */}
      <div>
        <h2 className="text-lg font-semibold text-gray-900">Payments & Subscriptions</h2>
        <p className="text-sm text-gray-500">View and manage all platform transactions</p>
      </div>

      {/* Tabs */}
      <div className="border-b border-gray-200">
        <nav className="flex gap-8">
          <button
            onClick={() => { setActiveTab('payments'); setPagination(p => ({ ...p, page: 1 })); }}
            className={`pb-3 text-sm font-medium border-b-2 transition-colors ${
              activeTab === 'payments'
                ? 'border-blue-500 text-blue-600'
                : 'border-transparent text-gray-500 hover:text-gray-700'
            }`}
          >
            Payments
          </button>
          <button
            onClick={() => { setActiveTab('subscriptions'); setPagination(p => ({ ...p, page: 1 })); }}
            className={`pb-3 text-sm font-medium border-b-2 transition-colors ${
              activeTab === 'subscriptions'
                ? 'border-blue-500 text-blue-600'
                : 'border-transparent text-gray-500 hover:text-gray-700'
            }`}
          >
            Subscriptions
          </button>
        </nav>
      </div>

      {/* Stats */}
      <div className="grid grid-cols-2 lg:grid-cols-4 gap-4">
        {activeTab === 'payments' ? (
          <>
            <div className="bg-white rounded-xl border border-gray-200 p-4">
              <div className="flex items-center gap-3">
                <div className="w-10 h-10 rounded-lg bg-blue-100 flex items-center justify-center">
                  <svg className="w-5 h-5 text-blue-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M3 10h18M7 15h1m4 0h1m-7 4h12a3 3 0 003-3V8a3 3 0 00-3-3H6a3 3 0 00-3 3v8a3 3 0 003 3z" />
                  </svg>
                </div>
                <div>
                  <p className="text-2xl font-bold text-gray-900">{pagination.total}</p>
                  <p className="text-xs text-gray-500">Total Payments</p>
                </div>
              </div>
            </div>
            <div className="bg-white rounded-xl border border-gray-200 p-4">
              <div className="flex items-center gap-3">
                <div className="w-10 h-10 rounded-lg bg-green-100 flex items-center justify-center">
                  <svg className="w-5 h-5 text-green-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8c-1.657 0-3 .895-3 2s1.343 2 3 2 3 .895 3 2-1.343 2-3 2m0-8c1.11 0 2.08.402 2.599 1M12 8V7m0 1v8m0 0v1m0-1c-1.11 0-2.08-.402-2.599-1M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
                  </svg>
                </div>
                <div>
                  <p className="text-2xl font-bold text-gray-900">{formatCurrency(totalAmount)}</p>
                  <p className="text-xs text-gray-500">Total Amount</p>
                </div>
              </div>
            </div>
            <div className="bg-white rounded-xl border border-gray-200 p-4">
              <div className="flex items-center gap-3">
                <div className="w-10 h-10 rounded-lg bg-purple-100 flex items-center justify-center">
                  <svg className="w-5 h-5 text-purple-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
                  </svg>
                </div>
                <div>
                  <p className="text-2xl font-bold text-gray-900">{completedPayments.length}</p>
                  <p className="text-xs text-gray-500">Completed</p>
                </div>
              </div>
            </div>
            <div className="bg-white rounded-xl border border-gray-200 p-4">
              <div className="flex items-center gap-3">
                <div className="w-10 h-10 rounded-lg bg-green-100 flex items-center justify-center">
                  <svg className="w-5 h-5 text-green-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8c-1.657 0-3 .895-3 2s1.343 2 3 2 3 .895 3 2-1.343 2-3 2m0-8c1.11 0 2.08.402 2.599 1M12 8V7m0 1v8m0 0v1m0-1c-1.11 0-2.08-.402-2.599-1M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
                  </svg>
                </div>
                <div>
                  <p className="text-2xl font-bold text-gray-900">{formatCurrency(completedAmount)}</p>
                  <p className="text-xs text-gray-500">Collected</p>
                </div>
              </div>
            </div>
          </>
        ) : (
          <>
            <div className="bg-white rounded-xl border border-gray-200 p-4">
              <div className="flex items-center gap-3">
                <div className="w-10 h-10 rounded-lg bg-blue-100 flex items-center justify-center">
                  <svg className="w-5 h-5 text-blue-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m5.618-4.016A11.955 11.955 0 0112 2.944a11.955 11.955 0 01-8.618 3.04A12.02 12.02 0 003 9c0 5.591 3.824 10.29 9 11.622 5.176-1.332 9-6.03 9-11.622 0-1.042-.133-2.052-.382-3.016z" />
                  </svg>
                </div>
                <div>
                  <p className="text-2xl font-bold text-gray-900">{pagination.total}</p>
                  <p className="text-xs text-gray-500">Total Subscriptions</p>
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
                  <p className="text-2xl font-bold text-gray-900">{activeSubscriptions.length}</p>
                  <p className="text-xs text-gray-500">Active</p>
                </div>
              </div>
            </div>
            <div className="bg-white rounded-xl border border-gray-200 p-4">
              <div className="flex items-center gap-3">
                <div className="w-10 h-10 rounded-lg bg-red-100 flex items-center justify-center">
                  <svg className="w-5 h-5 text-red-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
                  </svg>
                </div>
                <div>
                  <p className="text-2xl font-bold text-gray-900">{expiredSubscriptions.length}</p>
                  <p className="text-xs text-gray-500">Expired</p>
                </div>
              </div>
            </div>
            <div className="bg-white rounded-xl border border-gray-200 p-4">
              <div className="flex items-center gap-3">
                <div className="w-10 h-10 rounded-lg bg-purple-100 flex items-center justify-center">
                  <svg className="w-5 h-5 text-purple-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M17 20h5v-2a3 3 0 00-5.356-1.857M17 20H7m10 0v-2c0-.656-.126-1.283-.356-1.857M7 20H2v-2a3 3 0 015.356-1.857M7 20v-2c0-.656.126-1.283.356-1.857m0 0a5.002 5.002 0 019.288 0M15 7a3 3 0 11-6 0 3 3 0 016 0zm6 3a2 2 0 11-4 0 2 2 0 014 0zM7 10a2 2 0 11-4 0 2 2 0 014 0z" />
                  </svg>
                </div>
                <div>
                  <p className="text-2xl font-bold text-gray-900">{subscriptions.filter(s => s.entity_type === 'institute').length}</p>
                  <p className="text-xs text-gray-500">Institute</p>
                </div>
              </div>
            </div>
          </>
        )}
      </div>

      {/* Filters */}
      <div className="bg-white rounded-xl border border-gray-200">
        <div className="p-4 border-b border-gray-200">
          <div className="flex flex-wrap gap-4">
            {activeTab === 'payments' ? (
              <>
                <select
                  value={filters.status}
                  onChange={(e) => { setFilters({ ...filters, status: e.target.value }); setPagination(p => ({ ...p, page: 1 })); }}
                  className="px-4 py-2.5 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 text-sm"
                >
                  <option value="">All Status</option>
                  <option value="completed">Completed</option>
                  <option value="pending">Pending</option>
                  <option value="failed">Failed</option>
                  <option value="refunded">Refunded</option>
                </select>
                <select
                  value={filters.purpose}
                  onChange={(e) => { setFilters({ ...filters, purpose: e.target.value }); setPagination(p => ({ ...p, page: 1 })); }}
                  className="px-4 py-2.5 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 text-sm"
                >
                  <option value="">All Purposes</option>
                  <option value="subscription">Subscription</option>
                  <option value="wallet_topup">Wallet Topup</option>
                  <option value="exam_purchase">Exam Purchase</option>
                  <option value="ebook_purchase">Ebook Purchase</option>
                </select>
              </>
            ) : (
              <>
                <select
                  value={filters.status}
                  onChange={(e) => { setFilters({ ...filters, status: e.target.value }); setPagination(p => ({ ...p, page: 1 })); }}
                  className="px-4 py-2.5 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 text-sm"
                >
                  <option value="">All Status</option>
                  <option value="active">Active</option>
                  <option value="expired">Expired</option>
                  <option value="cancelled">Cancelled</option>
                </select>
                <select
                  value={filters.entity_type}
                  onChange={(e) => { setFilters({ ...filters, entity_type: e.target.value }); setPagination(p => ({ ...p, page: 1 })); }}
                  className="px-4 py-2.5 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 text-sm"
                >
                  <option value="">All Types</option>
                  <option value="institute">Institute</option>
                  <option value="student">Student</option>
                </select>
              </>
            )}
          </div>
        </div>

        {loading ? (
          <div className="p-12 flex justify-center">
            <Loader />
          </div>
        ) : (
          <>
            {activeTab === 'payments' ? (
              <div className="overflow-x-auto">
                <table className="w-full">
                  <thead className="bg-gray-50">
                    <tr>
                      <th className="px-6 py-3 text-left text-xs font-semibold text-gray-500 uppercase tracking-wide">Payment ID</th>
                      <th className="px-6 py-3 text-left text-xs font-semibold text-gray-500 uppercase tracking-wide">Amount</th>
                      <th className="px-6 py-3 text-left text-xs font-semibold text-gray-500 uppercase tracking-wide">Purpose</th>
                      <th className="px-6 py-3 text-left text-xs font-semibold text-gray-500 uppercase tracking-wide">Status</th>
                      <th className="px-6 py-3 text-left text-xs font-semibold text-gray-500 uppercase tracking-wide">Date</th>
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-gray-100">
                    {payments.length === 0 ? (
                      <tr>
                        <td colSpan={5} className="px-6 py-12 text-center">
                          <div className="flex flex-col items-center">
                            <svg className="w-12 h-12 text-gray-300 mb-3" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M3 10h18M7 15h1m4 0h1m-7 4h12a3 3 0 003-3V8a3 3 0 00-3-3H6a3 3 0 00-3 3v8a3 3 0 003 3z" />
                            </svg>
                            <p className="text-gray-500 font-medium">No payments found</p>
                          </div>
                        </td>
                      </tr>
                    ) : (
                      payments.map((payment) => (
                        <tr key={payment.id} className="hover:bg-gray-50 transition-colors">
                          <td className="px-6 py-4">
                            <span className="font-mono text-sm text-gray-600">
                              {payment.id?.slice(-12) || 'N/A'}
                            </span>
                          </td>
                          <td className="px-6 py-4">
                            <span className="font-semibold text-gray-900">{formatCurrency(payment.amount)}</span>
                          </td>
                          <td className="px-6 py-4">
                            <span className="text-sm text-gray-600">{getPurposeLabel(payment.purpose)}</span>
                          </td>
                          <td className="px-6 py-4">
                            {getStatusBadge(payment.status)}
                          </td>
                          <td className="px-6 py-4">
                            <span className="text-sm text-gray-600">{formatDate(payment.created_at)}</span>
                          </td>
                        </tr>
                      ))
                    )}
                  </tbody>
                </table>
              </div>
            ) : (
              <div className="overflow-x-auto">
                <table className="w-full">
                  <thead className="bg-gray-50">
                    <tr>
                      <th className="px-6 py-3 text-left text-xs font-semibold text-gray-500 uppercase tracking-wide">Subscription ID</th>
                      <th className="px-6 py-3 text-left text-xs font-semibold text-gray-500 uppercase tracking-wide">Entity</th>
                      <th className="px-6 py-3 text-left text-xs font-semibold text-gray-500 uppercase tracking-wide">Plan</th>
                      <th className="px-6 py-3 text-left text-xs font-semibold text-gray-500 uppercase tracking-wide">Price</th>
                      <th className="px-6 py-3 text-left text-xs font-semibold text-gray-500 uppercase tracking-wide">Status</th>
                      <th className="px-6 py-3 text-left text-xs font-semibold text-gray-500 uppercase tracking-wide">Expires</th>
                      <th className="px-6 py-3 text-left text-xs font-semibold text-gray-500 uppercase tracking-wide">Created</th>
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-gray-100">
                    {subscriptions.length === 0 ? (
                      <tr>
                        <td colSpan={7} className="px-6 py-12 text-center">
                          <div className="flex flex-col items-center">
                            <svg className="w-12 h-12 text-gray-300 mb-3" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M9 12l2 2 4-4m5.618-4.016A11.955 11.955 0 0112 2.944a11.955 11.955 0 01-8.618 3.04A12.02 12.02 0 003 9c0 5.591 3.824 10.29 9 11.622 5.176-1.332 9-6.03 9-11.622 0-1.042-.133-2.052-.382-3.016z" />
                            </svg>
                            <p className="text-gray-500 font-medium">No subscriptions found</p>
                          </div>
                        </td>
                      </tr>
                    ) : (
                      subscriptions.map((sub) => (
                        <tr key={sub.id} className="hover:bg-gray-50 transition-colors">
                          <td className="px-6 py-4">
                            <span className="font-mono text-sm text-gray-600">
                              {sub.id?.slice(-12) || 'N/A'}
                            </span>
                          </td>
                          <td className="px-6 py-4">
                            <div>
                              <span className={`px-2 py-0.5 text-xs font-medium rounded ${sub.entity_type === 'institute' ? 'bg-blue-100 text-blue-700' : 'bg-purple-100 text-purple-700'}`}>
                                {sub.entity_type}
                              </span>
                              <p className="text-sm text-gray-600 mt-1">
                                {sub.entity_type === 'institute' ? sub.institute_name : sub.student_email}
                              </p>
                            </div>
                          </td>
                          <td className="px-6 py-4">
                            <span className="text-sm font-medium text-gray-900">{sub.plan_name || 'N/A'}</span>
                          </td>
                          <td className="px-6 py-4">
                            <span className="text-sm text-gray-900">{formatCurrency(sub.plan_price)}</span>
                          </td>
                          <td className="px-6 py-4">
                            {getStatusBadge(sub.status)}
                          </td>
                          <td className="px-6 py-4">
                            <span className="text-sm text-gray-600">{formatDate(sub.expires_at)}</span>
                          </td>
                          <td className="px-6 py-4">
                            <span className="text-sm text-gray-600">{formatDate(sub.created_at)}</span>
                          </td>
                        </tr>
                      ))
                    )}
                  </tbody>
                </table>
              </div>
            )}

            {pagination.total_pages > 1 && (
              <div className="px-6 py-4 border-t border-gray-200 flex items-center justify-between">
                <p className="text-sm text-gray-500">
                  Showing {((pagination.page - 1) * pagination.limit) + 1} to {Math.min(pagination.page * pagination.limit, pagination.total)} of {pagination.total} {activeTab === 'payments' ? 'payments' : 'subscriptions'}
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
    </div>
  );
}
