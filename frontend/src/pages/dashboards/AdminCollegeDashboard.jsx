import { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { useAuth } from '../../contexts/AuthContext';
import { adminService } from '../../services/adminService';
import { examService } from '../../services/examService';
import Card from '../../components/ui/Card';
import Button from '../../components/ui/Button';

export default function AdminCollegeDashboard() {
  const { user } = useAuth();
  const [stats, setStats] = useState({ students: 0, teachers: 0, exams: 0, revenue: 0 });
  const [activities, setActivities] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchData = async () => {
      try {
        const [usersRes, examsRes] = await Promise.all([
          adminService.getUsers({ limit: 50 }).catch(() => ({ data: { data: { items: [] } } })),
          examService.getExams({ limit: 10 }).catch(() => ({ data: { data: { items: [] } } })),
        ]);

        const users = usersRes.data?.data?.items || [];
        const exams = examsRes.data?.data?.items || [];

        const students = users.filter(u => u.role === 'student_registered' || u.role === 'student_assigned').length;
        const teachers = users.filter(u => u.role === 'teacher').length;

        setStats({
          students,
          teachers,
          exams: exams.length,
          revenue: 0,
        });

        setActivities([
          { id: 1, type: 'user', message: 'New student registered', time: '2 hours ago' },
          { id: 2, type: 'exam', message: 'Exam "Math Quiz" created', time: '5 hours ago' },
          { id: 3, type: 'result', message: '15 results published', time: '1 day ago' },
        ]);
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

      <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
        <Card className="text-center">
          <p className="text-4xl font-bold text-gray-900">{stats.students}</p>
          <p className="text-sm text-gray-500 mt-2">Students</p>
        </Card>
        <Card className="text-center">
          <p className="text-4xl font-bold text-gray-900">{stats.teachers}</p>
          <p className="text-sm text-gray-500 mt-2">Teachers</p>
        </Card>
        <Card className="text-center">
          <p className="text-4xl font-bold text-gray-900">{stats.exams}</p>
          <p className="text-sm text-gray-500 mt-2">Exams</p>
        </Card>
        <Card className="text-center">
          <p className="text-4xl font-bold text-gray-900">₹{stats.revenue}</p>
          <p className="text-sm text-gray-500 mt-2">Revenue</p>
        </Card>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <Card header="User Management">
          <div className="flex flex-wrap gap-3">
            <Link to="/admin/users">
              <Button variant="secondary">Manage Users</Button>
            </Link>
            <Link to="/exams">
              <Button variant="secondary">Manage Exams</Button>
            </Link>
          </div>
        </Card>

        <Card header="Recent Activity">
          {activities.length === 0 ? (
            <p className="text-gray-500 text-center py-4">No recent activity</p>
          ) : (
            <div className="space-y-3">
              {activities.map((activity) => (
                <div key={activity.id} className="flex items-center justify-between p-3 bg-gray-50 rounded-lg">
                  <p className="text-sm text-gray-700">{activity.message}</p>
                  <p className="text-xs text-gray-400">{activity.time}</p>
                </div>
              ))}
            </div>
          )}
        </Card>
      </div>
    </div>
  );
}
