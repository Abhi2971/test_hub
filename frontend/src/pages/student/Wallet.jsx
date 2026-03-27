import { useState, useEffect } from 'react'
import { useNavigate } from 'react-router-dom'
import { useAuth } from '../../contexts/AuthContext'
import { useToast } from '../../contexts/ToastContext'
import { paymentService } from '../../services/paymentService'
import Button from '../../components/ui/Button'
import Card from '../../components/ui/Card'
import Badge from '../../components/ui/Badge'
import Input from '../../components/ui/Input'
import Modal from '../../components/ui/Modal'
import Pagination from '../../components/ui/Pagination'
import Loader from '../../components/ui/Loader'
import { CreditCard, Plus, TrendingUp, TrendingDown, ArrowRight } from 'lucide-react'

export default function Wallet() {
  const navigate = useNavigate()
  const { user } = useAuth()
  const { showToast } = useToast()
  const [wallet, setWallet] = useState(null)
  const [transactions, setTransactions] = useState([])
  const [loading, setLoading] = useState(true)
  const [topUpModal, setTopUpModal] = useState(false)
  const [amount, setAmount] = useState(100)
  const [customAmount, setCustomAmount] = useState('')
  const [processing, setProcessing] = useState(false)
  const [pagination, setPagination] = useState({ page: 1, limit: 10, total: 0 })

  useEffect(() => {
    if (user?.role !== 'student_registered' && user?.role !== 'student_assigned') {
      navigate('/dashboard')
      return
    }
    fetchWalletData()
  }, [user, pagination.page])

  const fetchWalletData = async () => {
    try {
      setLoading(true)
      const [walletRes, transactionsRes] = await Promise.all([
        paymentService.getWallet(),
        paymentService.getTransactions(pagination.page)
      ])
      setWallet(walletRes?.data)
      setTransactions(transactionsRes?.data?.items || [])
      setPagination(prev => ({ ...prev, total: transactionsRes?.data?.total || 0 }))
    } catch (error) {
      showToast('Failed to load wallet', 'error')
    } finally {
      setLoading(false)
    }
  }

  const handleTopUp = async (selectedAmount) => {
    const topUpAmount = selectedAmount || (customAmount ? parseInt(customAmount) : amount)
    if (!topUpAmount || topUpAmount < 10) {
      showToast('Please enter a valid amount (minimum ₹10)', 'error')
      return
    }

    setProcessing(true)
    try {
      const response = await paymentService.topUp(topUpAmount)
      const orderData = response.data

      await paymentService.initiateRazorpay(
        orderData,
        async (razorpayResponse) => {
          try {
            await paymentService.verifyPayment(
              orderData.order_id,
              razorpayResponse.razorpay_payment_id,
              razorpayResponse.razorpay_signature
            )
            showToast('Wallet topped up successfully!', 'success')
            setTopUpModal(false)
            fetchWalletData()
          } catch (error) {
            showToast('Payment verification failed', 'error')
          }
        },
        (error) => {
          showToast('Payment failed: ' + error.description, 'error')
        }
      )
    } catch (error) {
      showToast('Failed to initiate payment', 'error')
    } finally {
      setProcessing(false)
    }
  }

  const quickAmounts = [50, 100, 500, 1000]

  const getTransactionIcon = (type) => {
    if (type === 'credit') return <TrendingUp className="text-green-600" size={18} />
    return <TrendingDown className="text-red-600" size={18} />
  }

  const formatAmount = (amount) => {
    return new Intl.NumberFormat('en-IN', { style: 'currency', currency: 'INR' }).format(amount)
  }

  if (loading) {
    return <Loader text="Loading wallet..." />
  }

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold text-gray-900">Wallet</h1>
        <p className="text-gray-500 mt-1">Manage your wallet balance</p>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        <div className="lg:col-span-2 space-y-6">
          <Card>
            <div className="p-6">
              <div className="flex items-center justify-between mb-4">
                <div className="flex items-center gap-3">
                  <div className="w-12 h-12 bg-blue-100 rounded-xl flex items-center justify-center">
                    <CreditCard className="text-blue-600" size={24} />
                  </div>
                  <div>
                    <p className="text-sm text-gray-500">Available Balance</p>
                    <p className="text-3xl font-bold text-gray-900">{formatAmount(wallet?.balance || 0)}</p>
                  </div>
                </div>
                <Button onClick={() => setTopUpModal(true)} leftIcon={<Plus size={18} />}>
                  Top Up
                </Button>
              </div>

              <div className="grid grid-cols-3 gap-4 mt-6">
                <div className="bg-green-50 rounded-lg p-4 text-center">
                  <p className="text-sm text-green-600">Total Credited</p>
                  <p className="text-xl font-bold text-green-700">{formatAmount(wallet?.total_credited || 0)}</p>
                </div>
                <div className="bg-red-50 rounded-lg p-4 text-center">
                  <p className="text-sm text-red-600">Total Spent</p>
                  <p className="text-xl font-bold text-red-700">{formatAmount(wallet?.total_spent || 0)}</p>
                </div>
                <div className="bg-blue-50 rounded-lg p-4 text-center">
                  <p className="text-sm text-blue-600">Transactions</p>
                  <p className="text-xl font-bold text-blue-700">{wallet?.transactions_count || 0}</p>
                </div>
              </div>
            </div>
          </Card>

          <Card header="Transaction History">
            {transactions.length === 0 ? (
              <div className="p-8 text-center text-gray-500">
                No transactions yet
              </div>
            ) : (
              <div className="divide-y divide-gray-100">
                {transactions.map((txn) => (
                  <div key={txn.id} className="p-4 flex items-center justify-between hover:bg-gray-50">
                    <div className="flex items-center gap-3">
                      <div className={`w-10 h-10 rounded-full flex items-center justify-center ${
                        txn.type === 'credit' ? 'bg-green-100' : 'bg-red-100'
                      }`}>
                        {getTransactionIcon(txn.type)}
                      </div>
                      <div>
                        <p className="font-medium text-gray-900">{txn.purpose || txn.description}</p>
                        <p className="text-sm text-gray-500">{new Date(txn.created_at).toLocaleString()}</p>
                      </div>
                    </div>
                    <div className="text-right">
                      <p className={`font-bold ${
                        txn.type === 'credit' ? 'text-green-600' : 'text-red-600'
                      }`}>
                        {txn.type === 'credit' ? '+' : '-'}{formatAmount(txn.amount)}
                      </p>
                      <p className="text-sm text-gray-500">Bal: {formatAmount(txn.balance_after)}</p>
                    </div>
                  </div>
                ))}
              </div>
            )}

            {transactions.length > 0 && (
              <div className="p-4 border-t border-gray-200">
                <Pagination
                  page={pagination.page}
                  totalPages={Math.ceil(pagination.total / pagination.limit)}
                  onPageChange={(page) => setPagination(prev => ({ ...prev, page }))}
                  total={pagination.total}
                />
              </div>
            )}
          </Card>
        </div>

        <div>
          <Card header="Quick Top Up">
            <div className="p-4 space-y-4">
              <p className="text-sm text-gray-600">
                Select an amount or enter a custom amount to top up your wallet
              </p>
              <div className="grid grid-cols-2 gap-3">
                {quickAmounts.map((amt) => (
                  <button
                    key={amt}
                    onClick={() => { setAmount(amt); setTopUpModal(true) }}
                    className="py-3 px-4 border-2 border-gray-200 rounded-lg hover:border-blue-500 hover:bg-blue-50 transition-colors font-medium text-gray-700"
                  >
                    ₹{amt}
                  </button>
                ))}
              </div>
              <Button className="w-full" onClick={() => setTopUpModal(true)}>
                Custom Amount
              </Button>
            </div>
          </Card>

          <Card header="How to Use" className="mt-4">
            <div className="p-4 text-sm text-gray-600 space-y-3">
              <p>Your wallet can be used for:</p>
              <ul className="space-y-2">
                <li className="flex items-start gap-2">
                  <ArrowRight size={14} className="mt-1 text-blue-500" />
                  <span>Purchasing paid exams from marketplace</span>
                </li>
                <li className="flex items-start gap-2">
                  <ArrowRight size={14} className="mt-1 text-blue-500" />
                  <span>AI Recommendations plan subscription</span>
                </li>
                <li className="flex items-start gap-2">
                  <ArrowRight size={14} className="mt-1 text-blue-500" />
                  <span>Premium content access</span>
                </li>
              </ul>
            </div>
          </Card>
        </div>
      </div>

      <Modal
        isOpen={topUpModal}
        onClose={() => setTopUpModal(false)}
        title="Top Up Wallet"
        footer={
          <div className="flex gap-3">
            <Button variant="secondary" onClick={() => setTopUpModal(false)}>Cancel</Button>
            <Button onClick={() => handleTopUp()} loading={processing}>
              Top Up ₹{customAmount || amount}
            </Button>
          </div>
        }
      >
        <div className="space-y-4">
          <div className="grid grid-cols-4 gap-2">
            {quickAmounts.map((amt) => (
              <button
                key={amt}
                onClick={() => setAmount(amt)}
                className={`py-2 px-3 rounded-lg border font-medium transition-colors ${
                  amount === amt
                    ? 'border-blue-500 bg-blue-50 text-blue-600'
                    : 'border-gray-200 text-gray-700 hover:border-gray-300'
                }`}
              >
                ₹{amt}
              </button>
            ))}
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">Or enter custom amount</label>
            <Input
              type="number"
              value={customAmount}
              onChange={(e) => setCustomAmount(e.target.value)}
              placeholder="Enter amount"
              min="10"
            />
          </div>
          <div className="p-3 bg-gray-50 rounded-lg flex justify-between">
            <span className="text-gray-600">Total to pay:</span>
            <span className="font-bold text-gray-900">₹{customAmount || amount}</span>
          </div>
        </div>
      </Modal>
    </div>
  )
}