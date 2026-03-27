import { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { supportService } from '../../services/supportService';
import { useToast } from '../../contexts/ToastContext';
import { useAuth } from '../../contexts/AuthContext';
import Loader from '../../components/ui/Loader';
import Button from '../../components/ui/Button';
import Modal from '../../components/ui/Modal';

export default function TicketList() {
  const { user } = useAuth();
  const { showToast } = useToast();
  const [tickets, setTickets] = useState([]);
  const [loading, setLoading] = useState(true);
  const [statusFilter, setStatusFilter] = useState('all');
  const [page, setPage] = useState(1);
  const [showCreateModal, setShowCreateModal] = useState(false);
  const [creating, setCreating] = useState(false);

  const isStudent = ['student_registered', 'student_assigned'].includes(user?.role);
  const isSupportTeam = ['support_agent', 'admin_college', 'admin_public', 'teacher'].includes(user?.role);

  useEffect(() => {
    fetchTickets();
  }, [statusFilter, page]);

  const fetchTickets = async () => {
    try {
      setLoading(true);
      const params = { page, per_page: 20 };
      if (statusFilter !== 'all') params.status = statusFilter;
      const response = await supportService.getTickets(params);
      setTickets(response?.tickets || []);
    } catch (err) {
      console.error('Failed to load tickets:', err);
    } finally {
      setLoading(false);
    }
  };

  const getStatusBadge = (status) => {
    const colors = {
      open: 'bg-yellow-100 text-yellow-700',
      in_progress: 'bg-blue-100 text-blue-700',
      resolved: 'bg-green-100 text-green-700',
      closed: 'bg-gray-100 text-gray-700',
    };
    return <span className={`px-2.5 py-1 text-xs font-semibold rounded-full ${colors[status] || 'bg-gray-100 text-gray-700'}`}>{status?.replace(/_/g, ' ')}</span>;
  };

  const getPriorityBadge = (priority) => {
    const colors = {
      low: 'bg-gray-100 text-gray-600',
      medium: 'bg-blue-100 text-blue-700',
      high: 'bg-orange-100 text-orange-700',
      urgent: 'bg-red-100 text-red-700',
      critical: 'bg-red-100 text-red-700',
    };
    return <span className={`px-2.5 py-1 text-xs font-semibold rounded-full ${colors[priority] || 'bg-gray-100 text-gray-700'}`}>{priority}</span>;
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-lg font-semibold text-gray-900">Support Tickets</h2>
          <p className="text-sm text-gray-500">Manage and respond to user support requests</p>
        </div>
        {isStudent && (
          <Button onClick={() => setShowCreateModal(true)}>
            Create Ticket
          </Button>
        )}
        {isSupportTeam && (
          <Button onClick={() => setShowCreateModal(true)}>
            Create Ticket
          </Button>
        )}
      </div>

      {/* Stats */}
      <div className="grid grid-cols-2 lg:grid-cols-4 gap-4">
        <div className="bg-white rounded-xl border border-gray-200 p-4">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 rounded-lg bg-yellow-100 flex items-center justify-center">
              <svg className="w-5 h-5 text-yellow-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8 10h.01M12 10h.01M16 10h.01M21 12c0 4.418-4.03 8-9 8a9.863 9.863 0 01-4.255-.949L3 20l1.395-3.72C3.512 15.042 3 13.574 3 12c0-4.418 4.03-8 9-8s9 3.582 9 8z" />
              </svg>
            </div>
            <div>
              <p className="text-2xl font-bold text-gray-900">{tickets.length}</p>
              <p className="text-xs text-gray-500">Total</p>
            </div>
          </div>
        </div>
        <div className="bg-white rounded-xl border border-gray-200 p-4">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 rounded-lg bg-red-100 flex items-center justify-center">
              <svg className="w-5 h-5 text-red-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />
              </svg>
            </div>
            <div>
              <p className="text-2xl font-bold text-gray-900">{tickets.filter(t => t.priority === 'high' || t.priority === 'critical').length}</p>
              <p className="text-xs text-gray-500">High Priority</p>
            </div>
          </div>
        </div>
        <div className="bg-white rounded-xl border border-gray-200 p-4">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 rounded-lg bg-blue-100 flex items-center justify-center">
              <svg className="w-5 h-5 text-blue-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z" />
              </svg>
            </div>
            <div>
              <p className="text-2xl font-bold text-gray-900">{tickets.filter(t => t.status === 'open' || t.status === 'in_progress').length}</p>
              <p className="text-xs text-gray-500">Open</p>
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
              <p className="text-2xl font-bold text-gray-900">{tickets.filter(t => t.status === 'resolved').length}</p>
              <p className="text-xs text-gray-500">Resolved</p>
            </div>
          </div>
        </div>
      </div>

      {/* Filter */}
      <div className="bg-white rounded-xl border border-gray-200">
        <div className="p-4 border-b border-gray-200">
          <div className="flex flex-wrap gap-2">
            {['all', 'open', 'in_progress', 'resolved', 'closed'].map((status) => (
              <button
                key={status}
                onClick={() => { setStatusFilter(status); setPage(1); }}
                className={`px-3 py-1.5 rounded-lg text-sm font-medium transition ${
                  statusFilter === status
                    ? 'bg-blue-600 text-white'
                    : 'bg-white border border-gray-200 text-gray-600 hover:bg-gray-50'
                }`}
              >
                {status === 'all' ? 'All' : status.replace(/_/g, ' ')}
              </button>
            ))}
          </div>
        </div>

        {loading ? (
          <div className="p-12 flex justify-center">
            <Loader />
          </div>
        ) : (
          <>
            <div className="divide-y divide-gray-100">
              {tickets.length === 0 ? (
                <div className="p-12 text-center">
                  <svg className="w-12 h-12 text-gray-300 mx-auto mb-3" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M8 10h.01M12 10h.01M16 10h.01M21 12c0 4.418-4.03 8-9 8a9.863 9.863 0 01-4.255-.949L3 20l1.395-3.72C3.512 15.042 3 13.574 3 12c0-4.418 4.03-8 9-8s9 3.582 9 8z" />
                  </svg>
                  <p className="text-gray-500 font-medium">No tickets found</p>
                </div>
              ) : (
                tickets.map((ticket) => (
                  <Link
                    key={ticket.id}
                    to={`/support/tickets/${ticket.id}`}
                    className="block p-4 hover:bg-gray-50 transition-colors"
                  >
                    <div className="flex items-start gap-4">
                      <div className={`w-2 h-2 rounded-full mt-2 flex-shrink-0 ${
                        ticket.priority === 'critical' ? 'bg-red-600' :
                        ticket.priority === 'urgent' ? 'bg-red-500' :
                        ticket.priority === 'high' ? 'bg-orange-500' :
                        ticket.priority === 'medium' ? 'bg-blue-500' : 'bg-gray-400'
                      }`} />
                      <div className="flex-1 min-w-0">
                        <div className="flex items-center gap-2 mb-1">
                          <h4 className="font-medium text-gray-900 truncate">{ticket.subject || ticket.title || 'No Subject'}</h4>
                          {getPriorityBadge(ticket.priority)}
                          {getStatusBadge(ticket.status)}
                        </div>
                        <p className="text-sm text-gray-500 truncate">{ticket.description || 'No description'}</p>
                        <div className="flex items-center gap-4 mt-2 text-xs text-gray-400">
                          <span>{ticket.ticket_number || ''}</span>
                          <span>•</span>
                          <span>{ticket.created_at ? new Date(ticket.created_at).toLocaleDateString('en-IN', { day: 'numeric', month: 'short', year: 'numeric' }) : '-'}</span>
                        </div>
                      </div>
                      <div className="flex-shrink-0">
                        <svg className="w-5 h-5 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5l7 7-7 7" />
                        </svg>
                      </div>
                    </div>
                  </Link>
                ))
              )}
            </div>
          </>
        )}
      </div>

      {/* Create Ticket Modal */}
      <CreateTicketModal
        isOpen={showCreateModal}
        onClose={() => setShowCreateModal(false)}
        onSuccess={() => {
          setShowCreateModal(false);
          fetchTickets();
        }}
      />
    </div>
  );
}

function CreateTicketModal({ isOpen, onClose, onSuccess }) {
  const { showToast } = useToast();
  const [formData, setFormData] = useState({
    subject: '',
    description: '',
    category: 'technical',
    priority: 'medium'
  });
  const [loading, setLoading] = useState(false);

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!formData.subject.trim() || !formData.description.trim()) {
      showToast('Please fill all fields', 'error');
      return;
    }

    setLoading(true);
    try {
      await supportService.createTicket(formData);
      showToast('Ticket created successfully', 'success');
      setFormData({ subject: '', description: '', category: 'technical', priority: 'medium' });
      onSuccess();
    } catch (error) {
      showToast(error.message || 'Failed to create ticket', 'error');
    } finally {
      setLoading(false);
    }
  };

  return (
    <Modal
      isOpen={isOpen}
      onClose={onClose}
      title="Create Support Ticket"
      footer={
        <div className="flex gap-3">
          <Button variant="secondary" onClick={onClose}>Cancel</Button>
          <Button onClick={handleSubmit} loading={loading}>Submit Ticket</Button>
        </div>
      }
    >
      <form onSubmit={handleSubmit} className="space-y-4">
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">Subject *</label>
          <input
            type="text"
            value={formData.subject}
            onChange={(e) => setFormData({ ...formData, subject: e.target.value })}
            className="w-full px-4 py-2.5 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
            placeholder="Brief description of your issue"
            required
          />
        </div>
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">Description *</label>
          <textarea
            value={formData.description}
            onChange={(e) => setFormData({ ...formData, description: e.target.value })}
            className="w-full px-4 py-2.5 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
            rows={4}
            placeholder="Detailed description of your issue..."
            required
          />
        </div>
        <div className="grid grid-cols-2 gap-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">Category</label>
            <select
              value={formData.category}
              onChange={(e) => setFormData({ ...formData, category: e.target.value })}
              className="w-full px-4 py-2.5 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
            >
              <option value="technical">Technical</option>
              <option value="billing">Billing</option>
              <option value="exam">Exam</option>
              <option value="account">Account</option>
              <option value="other">Other</option>
            </select>
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">Priority</label>
            <select
              value={formData.priority}
              onChange={(e) => setFormData({ ...formData, priority: e.target.value })}
              className="w-full px-4 py-2.5 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
            >
              <option value="low">Low</option>
              <option value="medium">Medium</option>
              <option value="high">High</option>
              <option value="critical">Critical</option>
            </select>
          </div>
        </div>
      </form>
    </Modal>
  );
}
