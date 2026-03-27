import { useState, useEffect } from 'react';
import { superadminService } from '../../services/superadminService';
import Loader from '../../components/ui/Loader';
import { 
  Users, Building2, FileText, DollarSign, TrendingUp, Activity, 
  CreditCard, BookOpen, Award, CheckCircle, Clock, Wallet 
} from 'lucide-react';

const COLORS = ['#3B82F6', '#10B981', '#F59E0B', '#EF4444', '#8B5CF6', '#EC4899'];

export default function PlatformAnalytics() {
  const [stats, setStats] = useState({
    mau: 0,
    totalRevenue: 0,
    activeInstitutes: 0,
    totalInstitutes: 0,
    totalStudents: 0,
    totalTeachers: 0,
    totalExams: 0,
    totalSubscriptions: 0,
    activeSubscriptions: 0,
  });
  const [examTrend, setExamTrend] = useState([]);
  const [planDistribution, setPlanDistribution] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchAnalytics();
  }, []);

  const fetchAnalytics = async () => {
    try {
      setLoading(true);
      const response = await superadminService.getPlatformAnalytics();
      
      // Get the analytics data - service returns {data: {...}, success: true}
      const data = response?.data || {};
      
      setStats({
        mau: data.mau || 0,
        totalRevenue: data.total_revenue || 0,
        activeInstitutes: data.active_institutes || 0,
        totalInstitutes: data.total_institutes || 0,
        totalStudents: data.total_students || 0,
        totalTeachers: data.total_teachers || 0,
        totalExams: data.total_exams || 0,
        totalSubscriptions: data.total_subscriptions || 0,
        activeSubscriptions: data.active_subscriptions || 0,
      });
      
      setExamTrend(data.daily_exams_30d || []);
      setPlanDistribution(data.plan_distribution || []);
    } catch (error) {
      console.error('Failed to load analytics:', error);
    } finally {
      setLoading(false);
    }
  };

  const formatCurrency = (amount) => {
    if (!amount) return '₹0';
    if (amount >= 10000000) return `₹${(amount / 10000000).toFixed(2)} Cr`;
    if (amount >= 100000) return `₹${(amount / 100000).toFixed(2)} L`;
    if (amount >= 1000) return `₹${(amount / 1000).toFixed(1)} K`;
    return new Intl.NumberFormat('en-IN', {
      style: 'currency',
      currency: 'INR',
      maximumFractionDigits: 0
    }).format(amount / 100);
  };

  const statCards = [
    {
      label: 'Total Revenue',
      value: formatCurrency(stats.totalRevenue),
      subtext: 'All time earnings',
      icon: <DollarSign className="w-6 h-6" />,
      color: 'bg-gradient-to-br from-green-500 to-green-600'
    },
    {
      label: 'Active Institutes',
      value: stats.activeInstitutes || 0,
      subtext: `${stats.totalInstitutes || 0} total institutes`,
      icon: <Building2 className="w-6 h-6" />,
      color: 'bg-gradient-to-br from-blue-500 to-blue-600'
    },
    {
      label: 'Total Students',
      value: (stats.totalStudents || 0).toLocaleString(),
      subtext: `${stats.mau || 0} active this month`,
      icon: <Users className="w-6 h-6" />,
      color: 'bg-gradient-to-br from-purple-500 to-purple-600'
    },
    {
      label: 'Total Exams',
      value: (stats.totalExams || 0).toLocaleString(),
      subtext: 'Created exams',
      icon: <FileText className="w-6 h-6" />,
      color: 'bg-gradient-to-br from-orange-500 to-orange-600'
    },
    {
      label: 'Teachers',
      value: (stats.totalTeachers || 0).toLocaleString(),
      subtext: 'Registered teachers',
      icon: <BookOpen className="w-6 h-6" />,
      color: 'bg-gradient-to-br from-indigo-500 to-indigo-600'
    },
    {
      label: 'Subscriptions',
      value: stats.activeSubscriptions || 0,
      subtext: `${stats.totalSubscriptions || 0} total subs`,
      icon: <CreditCard className="w-6 h-6" />,
      color: 'bg-gradient-to-br from-pink-500 to-pink-600'
    },
  ];

  const maxCount = Math.max(...examTrend.map(d => d.count || 0), 1);

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-xl font-bold text-gray-900">Dashboard Overview</h2>
          <p className="text-sm text-gray-500 mt-1">Platform performance and analytics</p>
        </div>
        <button
          onClick={fetchAnalytics}
          className="px-4 py-2 bg-white border border-gray-300 rounded-lg text-sm font-medium text-gray-700 hover:bg-gray-50 flex items-center gap-2"
        >
          <TrendingUp className="w-4 h-4" />
          Refresh
        </button>
      </div>

      {loading ? (
        <div className="p-20 flex justify-center">
          <Loader text="Loading analytics..." />
        </div>
      ) : (
        <>
          {/* Stats Grid */}
          <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-6 gap-4">
            {statCards.map((card, idx) => (
              <div key={idx} className="bg-white rounded-xl border border-gray-200 p-5 hover:shadow-lg transition-shadow">
                <div className="flex items-start justify-between">
                  <div>
                    <p className="text-xs font-medium text-gray-500 uppercase tracking-wide">{card.label}</p>
                    <p className="text-2xl font-bold text-gray-900 mt-2">{card.value}</p>
                    <p className="text-xs text-gray-400 mt-1">{card.subtext}</p>
                  </div>
                  <div className={`w-12 h-12 rounded-xl flex items-center justify-center ${card.color}`}>
                    <span className="text-white">{card.icon}</span>
                  </div>
                </div>
              </div>
            ))}
          </div>

          {/* Charts Section */}
          <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
            {/* Exam Activity Chart */}
            <div className="lg:col-span-2 bg-white rounded-xl border border-gray-200 p-6">
              <div className="flex items-center justify-between mb-6">
                <div>
                  <h3 className="text-lg font-semibold text-gray-900">Exam Activity</h3>
                  <p className="text-sm text-gray-500">Daily exam attempts - Last 30 days</p>
                </div>
                <div className="flex items-center gap-4">
                  <div className="flex items-center gap-2">
                    <span className="w-3 h-3 rounded-full bg-blue-500"></span>
                    <span className="text-sm text-gray-600">Attempts</span>
                  </div>
                </div>
              </div>
              
              {examTrend.length === 0 ? (
                <div className="h-64 flex flex-col items-center justify-center text-gray-400">
                  <Activity className="w-12 h-12 mb-2 opacity-50" />
                  <p>No exam activity data available</p>
                </div>
              ) : (
                <div className="h-64 flex items-end gap-1">
                  {examTrend.map((d, i) => (
                    <div key={i} className="flex-1 flex flex-col items-center gap-2 group relative">
                      <div
                        className="w-full bg-gradient-to-t from-blue-600 to-blue-400 rounded-t transition-all hover:from-blue-700 hover:to-blue-500"
                        style={{ height: `${Math.max((d.count / maxCount) * 100, 4)}%` }}
                      />
                      <div className="absolute bottom-full mb-2 hidden group-hover:block bg-gray-900 text-white text-xs px-2 py-1 rounded whitespace-nowrap z-10">
                        {d.date}: {d.count} attempts
                      </div>
                    </div>
                  ))}
                </div>
              )}
              
              {examTrend.length > 0 && (
                <div className="flex justify-between mt-4 text-xs text-gray-400">
                  <span>{examTrend[0]?.date || '-'}</span>
                  <span>{examTrend[examTrend.length - 1]?.date || '-'}</span>
                </div>
              )}
            </div>

            {/* Plan Distribution */}
            <div className="bg-white rounded-xl border border-gray-200 p-6">
              <div className="flex items-center justify-between mb-6">
                <div>
                  <h3 className="text-lg font-semibold text-gray-900">Subscriptions</h3>
                  <p className="text-sm text-gray-500">Plan distribution</p>
                </div>
              </div>
              
              {planDistribution.length === 0 ? (
                <div className="h-64 flex flex-col items-center justify-center text-gray-400">
                  <Award className="w-12 h-12 mb-2 opacity-50" />
                  <p>No subscription data</p>
                </div>
              ) : (
                <div className="space-y-4">
                  {planDistribution.slice(0, 5).map((p, idx) => {
                    const total = planDistribution.reduce((sum, x) => sum + (x.count || 0), 0);
                    const percent = total > 0 ? ((p.count || 0) / total * 100) : 0;
                    return (
                      <div key={idx}>
                        <div className="flex items-center justify-between mb-1">
                          <div className="flex items-center gap-2">
                            <div
                              className="w-3 h-3 rounded-full"
                              style={{ backgroundColor: COLORS[idx % COLORS.length] }}
                            />
                            <span className="text-sm font-medium text-gray-900 truncate max-w-[120px]">{p.plan_name || 'Unknown'}</span>
                          </div>
                          <span className="text-sm font-semibold text-gray-900">{p.count || 0}</span>
                        </div>
                        <div className="ml-5 h-2 bg-gray-100 rounded-full overflow-hidden">
                          <div
                            className="h-full rounded-full transition-all"
                            style={{
                              width: `${percent}%`,
                              backgroundColor: COLORS[idx % COLORS.length]
                            }}
                          />
                        </div>
                      </div>
                    );
                  })}
                </div>
              )}

              {planDistribution.length > 0 && (
                <div className="mt-6 pt-4 border-t border-gray-100">
                  <div className="flex items-center justify-between text-sm">
                    <span className="text-gray-500">Total</span>
                    <span className="font-semibold text-gray-900">
                      {planDistribution.reduce((sum, p) => sum + (p.count || 0), 0)} subscriptions
                    </span>
                  </div>
                </div>
              )}
            </div>
          </div>

          {/* Quick Stats Cards */}
          <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
            <div className="bg-gradient-to-br from-emerald-500 to-emerald-600 rounded-xl p-5 text-white">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-emerald-100 text-sm">Monthly Active</p>
                  <p className="text-3xl font-bold mt-1">{stats.mau}</p>
                  <p className="text-emerald-100 text-xs mt-1">Users with activity</p>
                </div>
                <div className="w-12 h-12 bg-white/20 rounded-xl flex items-center justify-center">
                  <Activity className="w-6 h-6" />
                </div>
              </div>
            </div>

            <div className="bg-gradient-to-br from-amber-500 to-amber-600 rounded-xl p-5 text-white">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-amber-100 text-sm">Revenue Growth</p>
                  <p className="text-3xl font-bold mt-1">+12.5%</p>
                  <p className="text-amber-100 text-xs mt-1">vs last month</p>
                </div>
                <div className="w-12 h-12 bg-white/20 rounded-xl flex items-center justify-center">
                  <TrendingUp className="w-6 h-6" />
                </div>
              </div>
            </div>

            <div className="bg-gradient-to-br from-cyan-500 to-cyan-600 rounded-xl p-5 text-white">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-cyan-100 text-sm">Active Subs</p>
                  <p className="text-3xl font-bold mt-1">{stats.activeSubscriptions}</p>
                  <p className="text-cyan-100 text-xs mt-1">Current plans</p>
                </div>
                <div className="w-12 h-12 bg-white/20 rounded-xl flex items-center justify-center">
                  <CheckCircle className="w-6 h-6" />
                </div>
              </div>
            </div>

            <div className="bg-gradient-to-br from-rose-500 to-rose-600 rounded-xl p-5 text-white">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-rose-100 text-sm">Avg. Revenue</p>
                  <p className="text-3xl font-bold mt-1">
                    {stats.totalSubscriptions > 0 
                      ? formatCurrency(Math.round(stats.totalRevenue / stats.totalSubscriptions)) 
                      : '₹0'}
                  </p>
                  <p className="text-rose-100 text-xs mt-1">Per subscription</p>
                </div>
                <div className="w-12 h-12 bg-white/20 rounded-xl flex items-center justify-center">
                  <Wallet className="w-6 h-6" />
                </div>
              </div>
            </div>
          </div>
        </>
      )}
    </div>
  );
}
