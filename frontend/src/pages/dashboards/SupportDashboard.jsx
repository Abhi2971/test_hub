import { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { useAuth } from '../../contexts/AuthContext';
import { supportService } from '../../services/supportService';
import Card from '../../components/ui/Card';
import Button from '../../components/ui/Button';
import Badge from '../../components/ui/Badge';

export default function SupportDashboard() {
  const { user } = useAuth();
  const [stats, setStats] = useState({ openTickets: 0, pendingTickets: 0, resolvedTickets: 0 });
  const [tickets, setTickets] = useState([]);
  const [filter, setFilter] = useState('all');
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchData = async () => {
      try {
        const response = await supportService.getTickets({ limit: 20 });
        const allTickets = response?.tickets || [];
        setTickets(allTickets);
        
        setStats({
          openTickets: allTickets.filter(t => t.status === 'open').length,
          pendingTickets: allTickets.filter(t => t.status === 'pending').length,
          resolvedTickets: allTickets.filter(t => t.status === 'resolved' || t.status === 'closed').length,
        });
      } catch (err) {
        console.error(err);
      } finally {
        setLoading(false);
      }
    };
    fetchData();
  }, []);

  const filteredTickets = filter === 'all' ? tickets : tickets.filter(t => t.status === filter);

  const statusColors = {
    open: { bg: 'bg-blue-100', text: 'text-blue-700' },
    pending: { bg: 'bg-yellow-100', text: 'text-yellow-700' },
    resolved: { bg: 'bg-green-100', text: 'text-green-700' },
    closed: { bg: 'bg-gray-100', text: 'text-gray-700' },
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
          <p className="text-4xl font-bold text-gray-900">{stats.openTickets}</p>
          <p className="text-sm text-gray-500 mt-2">Open Tickets</p>
        </Card>
        <Card className="text-center">
          <p className="text-4xl font-bold text-gray-900">{stats.pendingTickets}</p>
          <p className="text-sm text-gray-500 mt-2">Pending Tickets</p>
        </Card>
        <Card className="text-center">
          <p className="text-4xl font-bold text-gray-900">{stats.resolvedTickets}</p>
          <p className="text-sm text-gray-500 mt-2">Resolved Tickets</p>
        </Card>
      </div>

      <Card header="Recent Tickets">
        <div className="mb-4 flex gap-2">
          {['all', 'open', 'pending', 'resolved'].map((status) => (
            <button
              key={status}
              onClick={() => setFilter(status)}
              className={`px-3 py-1.5 rounded-lg text-sm font-medium transition ${
                filter === status
                  ? 'bg-blue-600 text-white'
                  : 'bg-white border border-gray-200 text-gray-600 hover:bg-gray-50'
              }`}
            >
              {status.charAt(0).toUpperCase() + status.slice(1)}
            </button>
          ))}
        </div>

        {filteredTickets.length === 0 ? (
          <p className="text-gray-500 text-center py-4">No tickets found</p>
        ) : (
          <div className="space-y-3">
            {filteredTickets.map((ticket) => (
              <div key={ticket.id} className="flex items-center justify-between p-4 bg-gray-50 rounded-lg">
                <div className="flex-1">
                  <p className="font-medium text-gray-900">{ticket.subject}</p>
                  <p className="text-sm text-gray-500">
                    {ticket.user_name || 'Anonymous'} • {new Date(ticket.created_at).toLocaleDateString()}
                  </p>
                </div>
                <Badge className={statusColors[ticket.status]?.bg + ' ' + statusColors[ticket.status]?.text}>
                  {ticket.status}
                </Badge>
                <Link to={`/support/tickets/${ticket.id}`} className="ml-4 text-blue-600 hover:underline text-sm">
                  View
                </Link>
              </div>
            ))}
          </div>
        )}
      </Card>
    </div>
  );
}
