import { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { useAuth } from '../../contexts/AuthContext';
import { adminService } from '../../services/adminService';
import Card from '../../components/ui/Card';
import Button from '../../components/ui/Button';

export default function AdminPublicDashboard() {
  const { user } = useAuth();
  const [stats, setStats] = useState({ institutes: 0, revenue: 0, activeSubscriptions: 0 });
  const [subscription, setSubscription] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchData = async () => {
      try {
        const [subRes, plansRes] = await Promise.all([
          adminService.getSubscription().catch(() => ({ data: { data: null } })),
          adminService.getPlans().catch(() => ({ data: { data: { items: [] } } })),
        ]);

        setSubscription(subRes.data?.data);
        
        setStats({
          institutes: 0,
          revenue: 0,
          activeSubscriptions: 0,
        });
      } catch (err) {
        console.error(err);
      } finally {
        setLoading(false);
      }
    };
    fetchData();
  }, []);

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <h1 className="text-2xl font-bold text-gray-900">
          Welcome, {user?.first_name}!
        </h1>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        <Card className="text-center">
          <p className="text-4xl font-bold text-gray-900">{stats.institutes}</p>
          <p className="text-sm text-gray-500 mt-2">Institutes</p>
        </Card>
        <Card className="text-center">
          <p className="text-4xl font-bold text-gray-900">₹{stats.revenue}</p>
          <p className="text-sm text-gray-500 mt-2">Revenue</p>
        </Card>
        <Card className="text-center">
          <p className="text-4xl font-bold text-gray-900">{stats.activeSubscriptions}</p>
          <p className="text-sm text-gray-500 mt-2">Active Subscriptions</p>
        </Card>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <Card header="Subscription Management">
          {subscription ? (
            <div className="space-y-4">
              <div className="p-4 bg-gray-50 rounded-lg">
                <p className="font-medium text-gray-900">Current Plan: {subscription.plan_name || 'N/A'}</p>
                <p className="text-sm text-gray-500">Status: {subscription.status}</p>
              </div>
              <div className="flex gap-3">
                <Link to="/admin/plans">
                  <Button variant="secondary">Manage Plans</Button>
                </Link>
                <Button variant="secondary">Renew Subscription</Button>
              </div>
            </div>
          ) : (
            <p className="text-gray-500 text-center py-4">No active subscription</p>
          )}
        </Card>

        <Card header="Quick Actions">
          <div className="flex flex-wrap gap-3">
            <Link to="/admin/institutes">
              <Button variant="secondary">View Institutes</Button>
            </Link>
            <Link to="/admin/users">
              <Button variant="secondary">Manage Users</Button>
            </Link>
          </div>
        </Card>
      </div>
    </div>
  );
}
