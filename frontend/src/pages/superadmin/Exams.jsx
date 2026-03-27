import { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { useAuth } from '../../contexts/AuthContext';
import { useToast } from '../../contexts/ToastContext';
import { superadminService } from '../../services/superadminService';
import Loader from '../../components/ui/Loader';

export default function Exams() {
  const { user } = useAuth();
  const { showToast } = useToast();
  const [exams, setExams] = useState([]);
  const [loading, setLoading] = useState(true);
  const [pagination, setPagination] = useState({ page: 1, limit: 10, total: 0 });
  const [statusFilter, setStatusFilter] = useState('');
  const [examTypeFilter, setExamTypeFilter] = useState('');
  const [selectedExam, setSelectedExam] = useState(null);
  const [examDetails, setExamDetails] = useState(null);
  const [detailsLoading, setDetailsLoading] = useState(false);

  useEffect(() => {
    fetchExams();
  }, [pagination.page, statusFilter, examTypeFilter]);

  const fetchExams = async () => {
    try {
      setLoading(true);
      const params = {
        page: pagination.page,
        limit: pagination.limit,
        status: statusFilter || undefined,
        exam_type: examTypeFilter || undefined,
      };
      const response = await superadminService.getExams(params);
      setExams(response?.data?.items || []);
      setPagination(prev => ({
        ...prev,
        total: response?.data?.total || 0,
      }));
    } catch (error) {
      console.error('Failed to load exams:', error);
      showToast('Failed to load exams', 'error');
    } finally {
      setLoading(false);
    }
  };

  const fetchExamDetails = async (examId) => {
    setDetailsLoading(true);
    try {
      const response = await superadminService.getExamAnalytics(examId);
      setExamDetails(response?.data || {});
    } catch (error) {
      console.error('Failed to load exam details:', error);
      setExamDetails({});
    } finally {
      setDetailsLoading(false);
    }
  };

  const handleExamClick = (exam) => {
    setSelectedExam(exam);
    fetchExamDetails(exam.id);
  };

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-lg font-semibold text-gray-900">All Exams</h2>
          <p className="text-sm text-gray-500">View exams from all institutes</p>
        </div>
      </div>

      {/* Filters */}
      <div className="flex flex-wrap gap-4">
        <select
          value={examTypeFilter}
          onChange={(e) => { setExamTypeFilter(e.target.value); setPagination(p => ({ ...p, page: 1 })); }}
          className="px-4 py-2.5 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
        >
          <option value="">All Types</option>
          <option value="institute">College Admin Exams</option>
          <option value="public">Platform Admin Exams</option>
        </select>
        <select
          value={statusFilter}
          onChange={(e) => { setStatusFilter(e.target.value); setPagination(p => ({ ...p, page: 1 })); }}
          className="px-4 py-2.5 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
        >
          <option value="">All Status</option>
          <option value="draft">Draft</option>
          <option value="pending_approval">Pending Approval</option>
          <option value="published">Published</option>
          <option value="active">Active</option>
          <option value="closed">Closed</option>
        </select>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Exam List */}
        <div className="lg:col-span-2">
          <div className="bg-white rounded-xl border border-gray-200">
            {loading ? (
              <div className="p-12 flex justify-center">
                <Loader />
              </div>
            ) : exams.length === 0 ? (
              <div className="p-12 text-center">
                <p className="text-gray-500">No exams found</p>
              </div>
            ) : (
              <div className="divide-y divide-gray-100">
                {exams.map((exam) => (
                  <div
                    key={exam.id}
                    onClick={() => handleExamClick(exam)}
                    className={`p-4 cursor-pointer hover:bg-gray-50 transition-colors ${selectedExam?.id === exam.id ? 'bg-blue-50 border-l-4 border-blue-500' : ''
                      }`}
                  >
                    <div className="flex items-start justify-between">
                      <div>
                        <h3 className="font-medium text-gray-900">{exam.title}</h3>
                        <p className="text-sm text-gray-500 mt-1">
                          {exam.subject} • {exam.exam_type === 'institute' ? 'College Admin' : 'Platform Admin'}
                        </p>
                        <div className="flex items-center gap-3 mt-2 text-xs text-gray-400">
                          <span>{exam.question_count || 0} questions</span>
                          <span>•</span>
                          <span>{exam.duration_minutes || 60} min</span>
                          <span>•</span>
                          <span>{exam.total_marks || 0} marks</span>
                        </div>
                      </div>
                      <span className={`px-2.5 py-1 text-xs font-medium rounded-full ${exam.status === 'published' || exam.status === 'active' ? 'bg-green-100 text-green-700' :
                          exam.status === 'draft' ? 'bg-gray-100 text-gray-700' :
                            exam.status === 'pending_approval' ? 'bg-yellow-100 text-yellow-700' :
                              'bg-red-100 text-red-700'
                        }`}>
                        {exam.status}
                      </span>
                    </div>
                  </div>
                ))}
              </div>
            )}

            {pagination.total > pagination.limit && (
              <div className="p-4 border-t border-gray-200 flex items-center justify-between">
                <p className="text-sm text-gray-500">
                  Showing {((pagination.page - 1) * pagination.limit) + 1} to{' '}
                  {Math.min(pagination.page * pagination.limit, pagination.total)} of {pagination.total}
                </p>
                <div className="flex gap-2">
                  <button
                    onClick={() => setPagination(p => ({ ...p, page: p.page - 1 }))}
                    disabled={pagination.page === 1}
                    className="px-3 py-1.5 text-sm border border-gray-300 rounded-lg disabled:opacity-50"
                  >
                    Previous
                  </button>
                  <button
                    onClick={() => setPagination(p => ({ ...p, page: p.page + 1 }))}
                    disabled={pagination.page >= Math.ceil(pagination.total / pagination.limit)}
                    className="px-3 py-1.5 text-sm border border-gray-300 rounded-lg disabled:opacity-50"
                  >
                    Next
                  </button>
                </div>
              </div>
            )}
          </div>
        </div>

        {/* Exam Details & Analytics */}
        <div className="lg:col-span-1">
          {selectedExam ? (
            <div className="bg-white rounded-xl border border-gray-200">
              <div className="p-4 border-b border-gray-200">
                <h3 className="font-semibold text-gray-900">{selectedExam.title}</h3>
                <p className="text-sm text-gray-500">{selectedExam.subject}</p>
              </div>
              <div className="p-4 space-y-4">
                {detailsLoading ? (
                  <div className="p-8 flex justify-center">
                    <Loader />
                  </div>
                ) : (
                  <>
                    <div className="grid grid-cols-2 gap-4">
                      <div className="bg-blue-50 rounded-lg p-3">
                        <p className="text-xs font-medium text-blue-600">Pass Rate</p>
                        <p className="text-2xl font-bold text-blue-700">
                          {examDetails?.pass_rate?.toFixed(1) || 0}%
                        </p>
                      </div>
                      <div className="bg-green-50 rounded-lg p-3">
                        <p className="text-xs font-medium text-green-600">Avg Score</p>
                        <p className="text-2xl font-bold text-green-700">
                          {examDetails?.avg_score?.toFixed(1) || 0}
                        </p>
                      </div>
                    </div>
                    <div className="bg-gray-50 rounded-lg p-3">
                      <p className="text-xs font-medium text-gray-600">Total Attempts</p>
                      <p className="text-xl font-bold text-gray-700">
                        {examDetails?.total_attempts || 0}
                      </p>
                    </div>
                    <div className="grid grid-cols-2 gap-4">
                      <div className="bg-green-50 rounded-lg p-3">
                        <p className="text-xs font-medium text-green-600">Passed</p>
                        <p className="text-xl font-bold text-green-700">
                          {examDetails?.passed_count || 0}
                        </p>
                      </div>
                      <div className="bg-red-50 rounded-lg p-3">
                        <p className="text-xs font-medium text-red-600">Failed</p>
                        <p className="text-xl font-bold text-red-700">
                          {examDetails?.failed_count || 0}
                        </p>
                      </div>
                    </div>
                    <div className="bg-yellow-50 rounded-lg p-3">
                      <p className="text-xs font-medium text-yellow-600">Attendance Rate</p>
                      <p className="text-xl font-bold text-yellow-700">
                        {examDetails?.attendance_rate?.toFixed(1) || 0}%
                      </p>
                    </div>
                  </>
                )}
              </div>
            </div>
          ) : (
            <div className="bg-white rounded-xl border border-gray-200 p-12 text-center">
              <p className="text-gray-500">Select an exam to view analytics</p>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}