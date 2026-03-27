import { useState, useEffect } from 'react'
import { useParams, useNavigate } from 'react-router-dom'
import { useAuth } from '../../contexts/AuthContext'
import { useToast } from '../../contexts/ToastContext'
import { supportService } from '../../services/supportService'
import Button from '../../components/ui/Button'
import Card from '../../components/ui/Card'
import Badge from '../../components/ui/Badge'
import Loader from '../../components/ui/Loader'
import { ArrowLeft, Send, Clock, User } from 'lucide-react'

export default function TicketDetail() {
  const { id } = useParams()
  const navigate = useNavigate()
  const { user } = useAuth()
  const { showToast } = useToast()
  const [ticket, setTicket] = useState(null)
  const [messages, setMessages] = useState([])
  const [loading, setLoading] = useState(true)
  const [sending, setSending] = useState(false)
  const [reply, setReply] = useState('')

  const isSupportTeam = ['support_agent', 'admin_college', 'admin_public', 'teacher'].includes(user?.role)
  const isStudent = ['student_registered', 'student_assigned'].includes(user?.role)
  const isTicketOwner = ticket?.user_id === user?.id

  useEffect(() => {
    fetchTicket()
  }, [id])

  const fetchTicket = async () => {
    try {
      setLoading(true)
      const [ticketRes, messagesRes] = await Promise.all([
        supportService.getTicket(id),
        supportService.getTicketMessages(id).catch(() => ({ messages: [] }))
      ])
      setTicket(ticketRes)
      setMessages(messagesRes?.messages || [])
    } catch (error) {
      showToast('Failed to load ticket', 'error')
      navigate('/support/tickets')
    } finally {
      setLoading(false)
    }
  }

  const sendReply = async (e) => {
    e.preventDefault()
    if (!reply.trim()) return

    try {
      setSending(true)
      await supportService.replyTicket(id, reply)
      showToast('Reply sent successfully', 'success')
      setReply('')
      fetchTicket()
    } catch (error) {
      showToast('Failed to send reply', 'error')
    } finally {
      setSending(false)
    }
  }

  const updateStatus = async (status) => {
    try {
      await supportService.updateTicketStatus(id, { status })
      showToast('Status updated', 'success')
      fetchTicket()
    } catch (error) {
      showToast('Failed to update status', 'error')
    }
  }

  const getStatusBadge = (status) => {
    const variants = {
      open: 'warning',
      in_progress: 'info',
      resolved: 'success',
      closed: 'secondary'
    }
    return <Badge variant={variants[status] || 'secondary'}>{status?.replace('_', ' ')}</Badge>
  }

  const getPriorityBadge = (priority) => {
    const colors = {
      low: 'bg-gray-100 text-gray-600',
      medium: 'bg-yellow-100 text-yellow-700',
      high: 'bg-red-100 text-red-700',
      urgent: 'bg-red-200 text-red-800'
    }
    return <span className={`px-2 py-1 rounded text-xs font-medium ${colors[priority]}`}>{priority}</span>
  }

  if (loading) {
    return (
      <div className="flex justify-center py-12">
        <Loader />
      </div>
    )
  }

  return (
    <div className="space-y-6">
      <div className="flex items-center gap-4">
        <Button variant="secondary" size="sm" leftIcon={<ArrowLeft size={16} />} onClick={() => navigate('/support/tickets')}>
          Back
        </Button>
        <h1 className="text-2xl font-bold text-gray-900">Ticket #{ticket?.id}</h1>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        <div className="lg:col-span-2 space-y-6">
          <Card>
            <div className="flex items-start justify-between mb-6">
              <div>
                <h2 className="text-lg font-semibold text-gray-900">{ticket?.subject}</h2>
                <div className="flex items-center gap-3 mt-2">
                  {getStatusBadge(ticket?.status)}
                  {getPriorityBadge(ticket?.priority)}
                  <span className="text-sm text-gray-500">
                    Created {new Date(ticket?.created_at).toLocaleString()}
                  </span>
                </div>
              </div>
            </div>

            <div className="space-y-4">
              <div className="bg-gray-50 rounded-lg p-4">
                <div className="flex items-center gap-2 mb-2">
                  <User size={16} className="text-gray-500" />
                  <span className="text-sm font-medium text-gray-700">User</span>
                  <span className="text-xs text-gray-500">• {new Date(ticket?.created_at).toLocaleString()}</span>
                </div>
                <p className="text-gray-700">{ticket?.description}</p>
              </div>

              {messages?.map((msg, idx) => (
                <div key={idx} className={`rounded-lg p-4 ${msg.is_admin ? 'bg-blue-50' : 'bg-gray-50'}`}>
                  <div className="flex items-center gap-2 mb-2">
                    <User size={16} className="text-gray-500" />
                    <span className="text-sm font-medium text-gray-700">
                      {msg.is_admin ? 'Support Team' : (msg.sender_name || 'You')}
                    </span>
                    <span className="text-xs text-gray-500">• {new Date(msg.created_at).toLocaleString()}</span>
                  </div>
                  <p className="text-gray-700">{msg.message}</p>
                </div>
              ))}
            </div>

            {(isSupportTeam || (isStudent && isTicketOwner)) && ticket?.status !== 'closed' && (
              <form onSubmit={sendReply} className="mt-6 pt-6 border-t border-gray-200">
                <div className="flex gap-3">
                  <input
                    type="text"
                    placeholder="Type your reply..."
                    className="flex-1 px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500"
                    value={reply}
                    onChange={(e) => setReply(e.target.value)}
                  />
                  <Button type="submit" disabled={sending || !reply.trim()} leftIcon={<Send size={16} />}>
                    Send
                  </Button>
                </div>
              </form>
            )}
          </Card>
        </div>

        <div className="space-y-6">
          <Card>
            <h3 className="font-semibold text-gray-900 mb-4">Ticket Details</h3>
            <div className="space-y-3 text-sm">
              <div className="flex justify-between">
                <span className="text-gray-500">Category</span>
                <span className="text-gray-900 capitalize">{ticket?.category}</span>
              </div>
              <div className="flex justify-between">
                <span className="text-gray-500">Created</span>
                <span className="text-gray-900">{new Date(ticket?.created_at).toLocaleDateString()}</span>
              </div>
              <div className="flex justify-between">
                <span className="text-gray-500">Updated</span>
                <span className="text-gray-900">{new Date(ticket?.updated_at).toLocaleDateString()}</span>
              </div>
              {ticket?.resolved_at && (
                <div className="flex justify-between">
                  <span className="text-gray-500">Resolved</span>
                  <span className="text-gray-900">{new Date(ticket?.resolved_at).toLocaleDateString()}</span>
                </div>
              )}
            </div>
          </Card>

          {isSupportTeam && ticket?.status !== 'closed' && (
            <Card>
              <h3 className="font-semibold text-gray-900 mb-4">Actions</h3>
              <div className="space-y-2">
                {ticket?.status === 'open' && (
                  <Button variant="secondary" className="w-full" onClick={() => updateStatus('in_progress')}>
                    Mark In Progress
                  </Button>
                )}
                {ticket?.status === 'in_progress' && (
                  <Button variant="secondary" className="w-full" onClick={() => updateStatus('resolved')}>
                    Mark Resolved
                  </Button>
                )}
                {ticket?.status === 'resolved' && (
                  <Button variant="secondary" className="w-full" onClick={() => updateStatus('open')}>
                    Reopen Ticket
                  </Button>
                )}
                <Button variant="danger" className="w-full" onClick={() => updateStatus('closed')}>
                  Close Ticket
                </Button>
              </div>
            </Card>
          )}
        </div>
      </div>
    </div>
  )
}