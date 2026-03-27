import { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { useAuth } from '../../contexts/AuthContext';
import { superadminService } from '../../services/superadminService';
import Card from '../../components/ui/Card';
import Button from '../../components/ui/Button';
import Badge from '../../components/ui/Badge';

const StatCard = ({ title, value, subtitle, icon, color = 'blue' }) => {
  const colors = {
    blue: 'bg-blue-100 text-blue-600',
    green: 'bg-green-100 text-green-600',
    purple: 'bg-purple-100 text-purple-600',
    orange: 'bg-orange-100 text-orange-600',
    red: 'bg-red-100 text-red-600',
  };
  return (
    <div className="bg-white rounded-xl border border-gray-200 shadow-sm p-5">
      <div className="flex items-start justify-between">
        <div>
          <p className="text-xs font-medium text-gray-500 uppercase tracking-wide">{title}</p>
          <p className="text-2xl font-bold text-gray-900 mt-2">{value}</p>
          {subtitle && <p className="text-xs text-gray-400 mt-1">{subtitle}</p>}
        </div>
        <div className={`w-12 h-12 rounded-xl flex items-center justify-center ${colors[color] || colors.blue}`}>
          {icon}
        </div>
      </div>
    </div>
  );
};

const ActivityChart = ({ data }) => {
  if (!data || data.length === 0) return (
    <div className="bg-white rounded-xl border border-gray-200 shadow-sm">
      <div className="px-6 py-4 border-b border-gray-200">
        <h3 className="text-lg font-semibold text-gray-900">Exam Activity (Last 30 Days)</h3>
      </div>
      <div className="p-6">
        <p className="text-gray-400 text-center py-8">No activity data available</p>
      </div>
    </div>
  );

  const maxCount = Math.max(...data.map(d => d.count), 1);
  
  return (
    <div className="bg-white rounded-xl border border-gray-200 shadow-sm">
      <div className="px-6 py-4 border-b border-gray-200">
        <h3 className="text-lg font-semibold text-gray-900">Exam Activity (Last 30 Days)</h3>
      </div>
      <div className="p-6">
        <div className="flex items-end gap-1 h-40">
          {data.map((d, i) => (
            <div key={i} className="flex-1 flex flex-col items-center gap-1 group relative">
              <div
                className="w-full bg-gradient-to-t from-blue-600 to-blue-400 rounded-t transition-all hover:from-blue-700 hover:to-blue-500"
                style={{ height: `${Math.max((d.count / maxCount) * 100, 4)}%` }}
              />
              <div className="absolute bottom-full mb-1 hidden group-hover:block bg-gray-800 text-white text-xs px-2 py-1 rounded whitespace-nowrap z-10">
                {d.date}: {d.count} exams
              </div>
            </div>
          ))}
        </div>
        <div className="flex justify-between mt-3 text-xs text-gray-400">
          <span>{data[0]?.date}</span>
          <span>{data[data.length - 1]?.date}</span>
        </div>
      </div>
    </div>
  );
};

const PlanDistribution = ({ plans }) => {
  if (!plans || plans.length === 0) {
    return (
      <div className="bg-white rounded-xl border border-gray-200 shadow-sm">
        <div className="px-6 py-4 border-b border-gray-200">
          <h3 className="text-lg font-semibold text-gray-900">Plan Distribution</h3>
        </div>
        <div className="p-6">
          <p className="text-gray-400 text-center py-8">No plan data available</p>
        </div>
      </div>
    );
  }
  
  const colors = ['bg-blue-500', 'bg-green-500', 'bg-purple-500', 'bg-orange-500', 'bg-red-500', 'bg-gray-500'];
  const total = plans.reduce((sum, p) => sum + p.count, 0);

  return (
    <div className="bg-white rounded-xl border border-gray-200 shadow-sm">
      <div className="px-6 py-4 border-b border-gray-200">
        <h3 className="text-lg font-semibold text-gray-900">Plan Distribution</h3>
      </div>
      <div className="p-6">
        <div className="space-y-4">
          {plans.map((p, i) => {
            const percent = total > 0 ? Math.round((p.count / total) * 100) : 0;
            return (
              <div key={p.plan_name}>
                <div className="flex items-center justify-between mb-1">
                  <div className="flex items-center gap-2">
                    <div className={`w-3 h-3 rounded-full ${colors[i % colors.length]}`} />
                    <span className="text-sm font-medium text-gray-700">{p.plan_name}</span>
                  </div>
                  <span className="text-sm font-semibold text-gray-900">{p.count}</span>
                </div>
                <div className="ml-5 h-2 bg-gray-100 rounded-full overflow-hidden">
                  <div 
                    className={`h-full rounded-full ${colors[i % colors.length]}`} 
                    style={{ width: `${percent}%` }}
                  />
                </div>
                <p className="text-xs text-gray-400 ml-5 mt-1">{percent}%</p>
              </div>
            );
          })}
        </div>
        <div className="mt-6 pt-4 border-t border-gray-100">
          <div className="flex justify-between text-sm">
            <span className="text-gray-500">Total</span>
            <span className="font-semibold text-gray-900">{total} subscriptions</span>
          </div>
        </div>
      </div>
    </div>
  );
};

const QuickActions = () => (
  <div className="bg-white rounded-xl border border-gray-200 shadow-sm">
    <div className="px-6 py-4 border-b border-gray-200">
      <h3 className="text-lg font-semibold text-gray-900">Quick Actions</h3>
    </div>
    <div className="p-6">
      <div className="grid grid-cols-2 gap-3">
        <Link to="/superadmin/institutes" className="flex items-center gap-3 p-3 rounded-lg border border-gray-200 hover:bg-gray-50 transition-colors">
          <div className="w-10 h-10 rounded-lg bg-blue-100 flex items-center justify-center">
            <svg className="w-5 h-5 text-blue-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 21V5a2 2 0 00-2-2H7a2 2 0 00-2 2v16m14 0h2m-2 0h-5m-9 0H3m2 0h5M9 7h1m-1 4h1m4-4h1m-1 4h1m-5 10v-5a1 1 0 011-1h2a1 1 0 011 1v5m-4 0h4" />
            </svg>
          </div>
          <span className="text-sm font-medium text-gray-700">Institutes</span>
        </Link>
        <Link to="/superadmin/plans" className="flex items-center gap-3 p-3 rounded-lg border border-gray-200 hover:bg-gray-50 transition-colors">
          <div className="w-10 h-10 rounded-lg bg-green-100 flex items-center justify-center">
            <svg className="w-5 h-5 text-green-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M3 10h18M7 15h1m4 0h1m-7 4h12a3 3 0 003-3V8a3 3 0 00-3-3H6a3 3 0 00-3 3v8a3 3 0 003 3z" />
            </svg>
          </div>
          <span className="text-sm font-medium text-gray-700">Plans</span>
        </Link>
        <Link to="/superadmin/audit-logs" className="flex items-center gap-3 p-3 rounded-lg border border-gray-200 hover:bg-gray-50 transition-colors">
          <div className="w-10 h-10 rounded-lg bg-purple-100 flex items-center justify-center">
            <svg className="w-5 h-5 text-purple-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2" />
            </svg>
          </div>
          <span className="text-sm font-medium text-gray-700">Audit Logs</span>
        </Link>
        <Link to="/support/tickets" className="flex items-center gap-3 p-3 rounded-lg border border-gray-200 hover:bg-gray-50 transition-colors">
          <div className="w-10 h-10 rounded-lg bg-orange-100 flex items-center justify-center">
            <svg className="w-5 h-5 text-orange-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8 10h.01M12 10h.01M16 10h.01M21 12c0 4.418-4.03 8-9 8a9.863 9.863 0 01-4.255-.949L3 20l1.395-3.72C3.512 15.042 3 13.574 3 12c0-4.418 4.03-8 9-8s9 3.582 9 8z" />
            </svg>
          </div>
          <span className="text-sm font-medium text-gray-700">Support</span>
        </Link>
      </div>
    </div>
  </div>
);

export default function SuperAdminDashboard() {
  const { user } = useAuth();
  const [analytics, setAnalytics] = useState(null);
  const [institutes, setInstitutes] = useState([]);
  const [plans, setPlans] = useState([]);
  const [exams, setExams] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchData = async () => {
      try {
        const [analyticsRes, institutesRes, plansRes, examsRes] = await Promise.all([
          superadminService.getPlatformAnalytics().catch(() => ({ data: null })),
          superadminService.getInstitutes({ page: 1, per_page: 10 }).catch(() => ({ data: { items: [] } })),
          superadminService.getPlans().catch(() => ({ data: { items: [] } })),
          superadminService.getExams({ page: 1, per_page: 10 }).catch(() => ({ data: { items: [] } })),
        ]);
        
        setAnalytics(analyticsRes?.data || analyticsRes || null);
        setInstitutes(institutesRes?.data?.items || []);
        setPlans(plansRes?.data?.items || []);
        setExams(examsRes?.data?.items || []);
      } catch (err) {
        console.error('Dashboard fetch error:', err);
      } finally {
        setLoading(false);
      }
    };
    fetchData();
  }, []);

  const formatCurrency = (amount) => {
    if (amount === null || amount === undefined) return '₹0';
    return new Intl.NumberFormat('en-IN', { style: 'currency', currency: 'INR', maximumFractionDigits: 0 }).format(amount / 100);
  };

  const totalRevenue = analytics?.total_revenue || 0;
  const activeInstitutes = analytics?.active_institutes || 0;
  const mau = analytics?.mau || 0;
  const totalInstitutes = institutes.length || 0;
  const totalExams = analytics?.total_exams || 0;

  return (
    <div className="space-y-6">
      {/* Welcome Banner */}
      <div className="bg-gradient-to-r from-blue-600 to-purple-600 rounded-xl p-6 text-white">
        <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
          <div>
            <h2 className="text-2xl font-bold">
              Welcome back, {user?.full_name?.split(' ')[0] || 'Admin'}!
            </h2>
            <p className="text-blue-100 mt-1">
              Here's what's happening with your platform today.
            </p>
          </div>
          <div className="flex items-center gap-2 bg-white/10 backdrop-blur-sm px-4 py-2 rounded-lg">
            <span className="relative flex h-3 w-3">
              <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-green-400 opacity-75"></span>
              <span className="relative inline-flex rounded-full h-3 w-3 bg-green-400"></span>
            </span>
            <span className="text-sm font-medium">System Online</span>
          </div>
        </div>
      </div>

      {/* Stats Row */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        <StatCard
          title="Total Revenue"
          value={formatCurrency(totalRevenue)}
          subtitle="All time captured payments"
          color="green"
          icon={
            <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M12 8c-1.657 0-3 .895-3 2s1.343 2 3 2 3 .895 3 2-1.343 2-3 2m0-8c1.11 0 2.08.402 2.599 1M12 8V7m0 1v8m0 0v1m0-1c-1.11 0-2.08-.402-2.599-1M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
            </svg>
          }
        />
        <StatCard
          title="Active Institutes"
          value={activeInstitutes}
          subtitle={`${totalInstitutes} total registered`}
          color="blue"
          icon={
            <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M19 21V5a2 2 0 00-2-2H7a2 2 0 00-2 2v16m14 0h2m-2 0h-5m-9 0H3m2 0h5M9 7h1m-1 4h1m4-4h1m-1 4h1m-5 10v-5a1 1 0 011-1h2a1 1 0 011 1v5m-4 0h4" />
            </svg>
          }
        />
        <StatCard
          title="Monthly Active Users"
          value={mau}
          subtitle="Students with attempts (30d)"
          color="purple"
          icon={
            <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M17 20h5v-2a3 3 0 00-5.356-1.857M17 20H7m10 0v-2c0-.656-.126-1.283-.356-1.857M7 20H2v-2a3 3 0 015.356-1.857M7 20v-2c0-.656.126-1.283.356-1.857m0 0a5.002 5.002 0 019.288 0M15 7a3 3 0 11-6 0 3 3 0 016 0zm6 3a2 2 0 11-4 0 2 2 0 014 0zM7 10a2 2 0 11-4 0 2 2 0 014 0z" />
            </svg>
          }
        />
        <StatCard
          title="Exams Created"
          value={analytics?.daily_exams_30d?.reduce((sum, d) => sum + d.count, 0) || 0}
          subtitle="Last 30 days"
          color="orange"
          icon={
            <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2m-3 7h3m-3 4h3m-6-4h.01M9 16h.01" />
            </svg>
          }
        />
      </div>

      {/* Charts and Tables */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        <div className="lg:col-span-2">
          <ActivityChart data={analytics?.daily_exams_30d || []} />
        </div>
        <div>
          <PlanDistribution plans={analytics?.plan_distribution || []} />
        </div>
      </div>

      {/* Institutes Table and Quick Actions */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        <div className="lg:col-span-2">
          <div className="bg-white rounded-xl border border-gray-200 shadow-sm">
            <div className="px-6 py-4 border-b border-gray-200 flex items-center justify-between">
              <h3 className="text-lg font-semibold text-gray-900">Recent Institutes</h3>
              <Link to="/superadmin/institutes" className="text-sm text-blue-600 hover:underline font-medium">
                View all →
              </Link>
            </div>
            <div className="p-6">
              {institutes.length === 0 ? (
                <p className="text-gray-400 text-center py-8">No institutes found</p>
              ) : (
                <div className="overflow-x-auto">
                  <table className="w-full">
                    <thead>
                      <tr className="border-b border-gray-200">
                        <th className="text-left pb-3 text-xs font-semibold text-gray-500 uppercase tracking-wide">Institute</th>
                        <th className="text-left pb-3 text-xs font-semibold text-gray-500 uppercase tracking-wide">Location</th>
                        <th className="text-left pb-3 text-xs font-semibold text-gray-500 uppercase tracking-wide">Plan</th>
                        <th className="text-left pb-3 text-xs font-semibold text-gray-500 uppercase tracking-wide">Status</th>
                      </tr>
                    </thead>
                    <tbody className="divide-y divide-gray-100">
                      {institutes.map((inst) => (
                        <tr key={inst.id} className="hover:bg-gray-50 transition-colors">
                          <td className="py-3">
                            <p className="font-medium text-gray-900 text-sm">{inst.name}</p>
                            <p className="text-xs text-gray-400">{inst.slug}</p>
                          </td>
                          <td className="py-3">
                            <p className="text-sm text-gray-600">{inst.city}, {inst.state}</p>
                          </td>
                          <td className="py-3">
                            <span className={`px-2.5 py-1 text-xs font-medium rounded-full ${
                              inst.plan === 'Enterprise' ? 'bg-purple-100 text-purple-700' :
                              inst.plan === 'Growth' ? 'bg-blue-100 text-blue-700' :
                              inst.plan === 'Starter' ? 'bg-green-100 text-green-700' :
                              'bg-gray-100 text-gray-600'
                            }`}>
                              {inst.plan || 'Free'}
                            </span>
                          </td>
                          <td className="py-3">
                            <span className={`px-2.5 py-1 text-xs font-medium rounded-full ${
                              inst.is_suspended ? 'bg-red-100 text-red-700' :
                              inst.is_active ? 'bg-green-100 text-green-700' :
                              'bg-gray-100 text-gray-600'
                            }`}>
                              {inst.is_suspended ? 'Suspended' : inst.is_active ? 'Active' : 'Inactive'}
                            </span>
                          </td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              )}
            </div>
          </div>
        </div>

        <div className="space-y-6">
          <QuickActions />
          
          {/* Plans Overview */}
          <div className="bg-white rounded-xl border border-gray-200 shadow-sm">
            <div className="px-6 py-4 border-b border-gray-200 flex items-center justify-between">
              <h3 className="text-lg font-semibold text-gray-900">Plans</h3>
              <Link to="/superadmin/plans" className="text-sm text-blue-600 hover:underline font-medium">
                Manage →
              </Link>
            </div>
            <div className="p-6">
              <div className="space-y-4">
                {plans.slice(0, 5).map((plan) => (
                  <div key={plan.id} className="flex items-center justify-between py-2 border-b border-gray-100 last:border-0 last:pb-0">
                    <div>
                      <p className="text-sm font-medium text-gray-900">{plan.name}</p>
                      <p className="text-xs text-gray-400">
                        {plan.price === 0 ? 'Free' : new Intl.NumberFormat('en-IN', { style: 'currency', currency: 'INR', maximumFractionDigits: 0 }).format(plan.price / 100) + '/mo'}
                      </p>
                    </div>
                    <span className={`w-2.5 h-2.5 rounded-full ${plan.is_active ? 'bg-green-500' : 'bg-gray-300'}`} />
                  </div>
                ))}
              </div>
            </div>
          </div>
          
          {/* Exams Overview */}
          <div className="bg-white rounded-xl border border-gray-200 shadow-sm">
            <div className="px-6 py-4 border-b border-gray-200 flex items-center justify-between">
              <h3 className="text-lg font-semibold text-gray-900">Recent Exams</h3>
              <Link to="/exams" className="text-sm text-blue-600 hover:underline font-medium">
                View all →
              </Link>
            </div>
            <div className="p-6">
              {exams.length === 0 ? (
                <p className="text-gray-400 text-center py-8">No exams found</p>
              ) : (
                <div className="space-y-3">
                  {exams.slice(0, 5).map((exam) => (
                    <div key={exam.id} className="flex items-center justify-between py-3 border-b border-gray-100 last:border-0">
                      <div>
                        <p className="text-sm font-medium text-gray-900">{exam.title}</p>
                        <p className="text-xs text-gray-500">
                          {exam.institute_name || 'No institute'}
                        </p>
                      </div>
                      <div className="flex items-center gap-3">
                        <span className="px-2.5 py-0.5 text-xs font-medium rounded-full 
                          {exam.status === 'published' ? 'bg-green-100 text-green-700' :
                            exam.status === 'draft' ? 'bg-yellow-100 text-yellow-700' :
                            exam.status === 'active' ? 'bg-blue-100 text-blue-700' :
                            exam.status === 'closed' ? 'bg-gray-100 text-gray-700' :
                            'bg-purple-100 text-purple-700'}
                        ">
                          {exam.status}
                        </span>
                        <span className="text-xs text-gray-500">
                          {exam.questions_count || 0} questions
                        </span>
                        <span className="text-xs text-gray-500">
                          {exam.attempts_count || 0} attempts
                        </span>
                      </div>
                    </div>
                  ))}
                </div>
              )}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
