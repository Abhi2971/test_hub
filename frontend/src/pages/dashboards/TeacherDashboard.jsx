import { useState, useEffect } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { useAuth } from '../../contexts/AuthContext';
import { examService } from '../../services/examService';
import { resultService } from '../../services/resultService';
import Card from '../../components/ui/Card';
import Button from '../../components/ui/Button';
import Badge from '../../components/ui/Badge';

export default function TeacherDashboard() {
  const { user } = useAuth();
  const navigate = useNavigate();
  const [stats, setStats] = useState({ totalExams: 0, totalStudents: 0, passRate: 0 });
  const [recentExams, setRecentExams] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchData = async () => {
      try {
        const [examsRes, resultsRes] = await Promise.all([
          examService.getExams({ limit: 5 }).catch(() => ({ data: { data: { items: [], stats: {} } } })),
          resultService.getResults({ limit: 100 }).catch(() => ({ data: { data: { items: [] } } })),
        ]);
        
        const exams = examsRes.data?.data?.items || [];
        const results = resultsRes.data?.data?.items || [];
        
        setRecentExams(exams);
        
        const uniqueStudents = new Set(results.map(r => r.student_id)).size;
        const passedCount = results.filter(r => r.passed).length;
        const passRate = results.length > 0 ? Math.round((passedCount / results.length) * 100) : 0;
        
        setStats({
          totalExams: exams.length,
          totalStudents: uniqueStudents,
          passRate,
        });
      } catch (err) {
        console.error(err);
      } finally {
        setLoading(false);
      }
    };
    fetchData();
  }, []);

  const statusColors = {
    draft: { bg: 'bg-gray-100', text: 'text-gray-700' },
    published: { bg: 'bg-blue-100', text: 'text-blue-700' },
    active: { bg: 'bg-green-100', text: 'text-green-700' },
    closed: { bg: 'bg-red-100', text: 'text-red-700' },
  };

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <h1 className="text-2xl font-bold text-gray-900">
          Welcome, {user?.first_name}!
        </h1>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        <Card className="text-center">
          <p className="text-4xl font-bold text-gray-900">{stats.totalExams}</p>
          <p className="text-sm text-gray-500 mt-2">Total Exams</p>
        </Card>
        <Card className="text-center">
          <p className="text-4xl font-bold text-gray-900">{stats.totalStudents}</p>
          <p className="text-sm text-gray-500 mt-2">Total Students</p>
        </Card>
        <Card className="text-center">
          <p className="text-4xl font-bold text-gray-900">{stats.passRate}%</p>
          <p className="text-sm text-gray-500 mt-2">Avg Pass Rate</p>
        </Card>
      </div>

      <Card header="Recent Exams">
        {recentExams.length === 0 ? (
          <p className="text-gray-500 text-center py-4">No exams created yet</p>
        ) : (
          <div className="overflow-x-auto">
            <table className="w-full">
              <thead className="bg-gray-50 border-b border-gray-200">
                <tr>
                  <th className="text-left px-4 py-3 text-xs font-semibold text-gray-500 uppercase">Title</th>
                  <th className="text-left px-4 py-3 text-xs font-semibold text-gray-500 uppercase">Status</th>
                  <th className="text-left px-4 py-3 text-xs font-semibold text-gray-500 uppercase">Questions</th>
                  <th className="text-left px-4 py-3 text-xs font-semibold text-gray-500 uppercase">Attempts</th>
                  <th className="text-left px-4 py-3 text-xs font-semibold text-gray-500 uppercase">Actions</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-gray-100">
                {recentExams.map((exam) => (
                  <tr key={exam.id} className="hover:bg-gray-50">
                    <td className="px-4 py-3">
                      <p className="font-medium text-gray-900">{exam.title}</p>
                      <p className="text-sm text-gray-500">{exam.duration_minutes} min • {exam.total_marks} marks</p>
                    </td>
                    <td className="px-4 py-3">
                      <Badge className={statusColors[exam.status]?.bg + ' ' + statusColors[exam.status]?.text}>
                        {exam.status}
                      </Badge>
                    </td>
                    <td className="px-4 py-3 text-sm text-gray-600">{exam.question_count || 0}</td>
                    <td className="px-4 py-3 text-sm text-gray-600">{exam.attempt_count || 0}</td>
                    <td className="px-4 py-3">
                      <div className="flex items-center gap-2">
                        <Link to={`/exams/${exam.id}`} className="text-blue-600 hover:underline text-sm">
                          View
                        </Link>
                        <Link to={`/exams/${exam.id}/edit`} className="text-gray-600 hover:text-gray-900 text-sm">
                          Edit
                        </Link>
                      </div>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </Card>

      <Card header="Quick Actions">
        <div className="flex flex-wrap gap-3">
          <Link to="/exams/create">
            <Button leftIcon={
              <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 4v16m8-8H4" />
              </svg>
            }>
              Create Exam
            </Button>
          </Link>
          <Link to="/questions/create">
            <Button variant="secondary" leftIcon={
              <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 4v16m8-8H4" />
              </svg>
            }>
              Add Questions
            </Button>
          </Link>
        </div>
      </Card>
    </div>
  );
}
