import { useState, useEffect } from 'react'
import { useNavigate } from 'react-router-dom'
import { useAuth } from '../../contexts/AuthContext'
import { useToast } from '../../contexts/ToastContext'
import { resultService } from '../../services/resultService'
import { paymentService, subscriptionService } from '../../services/paymentService'
import api from '../../services/api'
import Button from '../../components/ui/Button'
import Card from '../../components/ui/Card'
import Badge from '../../components/ui/Badge'
import Loader from '../../components/ui/Loader'
import Modal from '../../components/ui/Modal'
import { Lightbulb, TrendingUp, BookOpen, Target, Zap, Crown, Check, CreditCard } from 'lucide-react'

export default function AIRecommendations() {
  const navigate = useNavigate()
  const { user } = useAuth()
  const { showToast } = useToast()
  const [recommendations, setRecommendations] = useState([])
  const [loading, setLoading] = useState(true)
  const [subscription, setSubscription] = useState(null)
  const [plans, setPlans] = useState([])
  const [plansLoading, setPlansLoading] = useState(false)
  const [subscribeModal, setSubscribeModal] = useState(false)
  const [selectedPlan, setSelectedPlan] = useState(null)
  const [processing, setProcessing] = useState(false)
  const [wallet, setWallet] = useState(null)

  useEffect(() => {
    if (user?.role !== 'student_registered' && user?.role !== 'student_assigned') {
      navigate('/dashboard')
      return
    }
    fetchData()
  }, [user])

  const fetchData = async () => {
    try {
      setLoading(true)
      const [recResponse, subResponse, walletRes] = await Promise.all([
        api.get('/results/ai-recommendations').catch(() => ({ data: { data: [] } })),
        subscriptionService.getMySubscription().catch(() => ({ data: { data: { status: 'none' } } })),
        paymentService.getWallet().catch(() => ({ data: { data: { balance: 0 } } })),
      ])
      setRecommendations(recResponse.data.data || [])
      setSubscription(subResponse.data.data)
      setWallet(walletRes.data.data)
    } catch (error) {
      console.error('Failed to load data', error)
    } finally {
      setLoading(false)
    }
  }

  const fetchPlans = async () => {
    try {
      setPlansLoading(true)
      const response = await subscriptionService.getStudentPlans()
      setPlans(response.data.items || [])
    } catch (error) {
      showToast('Failed to load plans', 'error')
    } finally {
      setPlansLoading(false)
    }
  }

  const handleSubscribe = async (plan) => {
    setSelectedPlan(plan)
    setSubscribeModal(true)
  }

  const handleWalletSubscribe = async () => {
    if (!selectedPlan) return
    
    if (wallet?.balance < selectedPlan.price) {
      showToast('Insufficient wallet balance. Please top up first.', 'error')
      return
    }

    setProcessing(true)
    try {
      const result = await subscriptionService.subscribeWithWallet(selectedPlan.id)
      if (result.success) {
        showToast(`Successfully subscribed to ${selectedPlan.name}!`, 'success')
        setSubscribeModal(false)
        fetchData()
      }
    } catch (error) {
      showToast(error.message || 'Failed to subscribe', 'error')
    } finally {
      setProcessing(false)
    }
  }

  const handleRazorpaySubscribe = async () => {
    if (!selectedPlan) return

    setProcessing(true)
    try {
      const result = await subscriptionService.subscribeWithRazorpay(selectedPlan.id)
      const orderData = result.data

      await paymentService.initiateRazorpay(
        orderData,
        async (razorpayResponse) => {
          try {
            await api.post('/payments/verify', {
              order_id: orderData.order_id,
              payment_id: razorpayResponse.razorpay_payment_id,
              signature: razorpayResponse.razorpay_signature,
            })
            showToast(`Successfully subscribed to ${selectedPlan.name}!`, 'success')
            setSubscribeModal(false)
            fetchData()
          } catch (error) {
            showToast('Payment verification failed', 'error')
          }
        },
        (error) => {
          showToast('Payment failed: ' + error.description, 'error')
        }
      )
    } catch (error) {
      showToast(error.message || 'Failed to initiate payment', 'error')
    } finally {
      setProcessing(false)
    }
  }

  const getStrengths = (rec) => {
    return rec.strengths || ['Good understanding of basics', 'Strong in conceptual topics']
  }

  const getImprovements = (rec) => {
    return rec.topics_to_improve || ['Need more practice in advanced topics', 'Weak in problem-solving']
  }

  const getStudyTips = (rec) => {
    return rec.study_tips || ['Focus on practice problems', 'Review fundamentals', 'Take mock tests']
  }

  const hasActiveSubscription = subscription?.status === 'active' || subscription?.subscription_active

  const formatCurrency = (amount) => {
    return new Intl.NumberFormat('en-IN', { style: 'currency', currency: 'INR' }).format(amount)
  }

  if (loading) {
    return (
      <div className="flex justify-center py-12">
        <Loader text="Analyzing your performance..." />
      </div>
    )
  }

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">AI Recommendations</h1>
          <p className="text-gray-500 mt-1">Personalized learning insights based on your performance</p>
        </div>
        {!hasActiveSubscription && (
          <Button onClick={() => { fetchPlans(); setSubscribeModal(true) }} leftIcon={<Crown size={18} />}>
            Get AI Plans
          </Button>
        )}
        {hasActiveSubscription && subscription?.plan && (
          <Badge variant="success" className="px-3 py-1">
            <Crown size={14} className="mr-1 inline" />
            {subscription.plan.name} Active
          </Badge>
        )}
      </div>

      {!hasActiveSubscription && recommendations.length === 0 && (
        <Card>
          <div className="p-8 text-center">
            <div className="w-16 h-16 bg-amber-100 rounded-full flex items-center justify-center mx-auto mb-4">
              <Crown className="text-amber-600" size={32} />
            </div>
            <h3 className="text-lg font-semibold text-gray-900 mb-2">Unlock AI Recommendations</h3>
            <p className="text-gray-500 mb-6 max-w-md mx-auto">
              Get personalized learning insights, weakness analysis, and AI-powered study recommendations by subscribing to one of our plans.
            </p>
            <Button onClick={() => { fetchPlans(); setSubscribeModal(true) }}>
              View Available Plans
            </Button>
          </div>
        </Card>
      )}

      {recommendations.length === 0 && hasActiveSubscription && (
        <Card>
          <div className="p-12 text-center">
            <Lightbulb className="mx-auto text-gray-300 mb-4" size={48} />
            <p className="text-gray-500 mb-4">No recommendations yet</p>
            <p className="text-sm text-gray-400">Complete some exams to get personalized insights</p>
          </div>
        </Card>
      )}

      {recommendations.length > 0 && (
        <div className="grid gap-6">
          {recommendations.map((rec) => (
            <Card key={rec.id} className="overflow-hidden">
              <div className="p-6">
                <div className="flex items-center justify-between mb-4">
                  <div>
                    <h3 className="text-lg font-semibold text-gray-900">{rec.exam_name || 'Exam'}</h3>
                    <p className="text-sm text-gray-500">Score: {rec.score}%</p>
                  </div>
                  <Badge variant={rec.score >= 70 ? 'success' : rec.score >= 50 ? 'warning' : 'danger'}>
                    {rec.score >= 70 ? 'Excellent' : rec.score >= 50 ? 'Good' : 'Needs Work'}
                  </Badge>
                </div>

                <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
                  <div className="bg-green-50 rounded-lg p-4">
                    <div className="flex items-center gap-2 mb-3">
                      <TrendingUp className="text-green-600" size={18} />
                      <h4 className="font-medium text-green-900">Strengths</h4>
                    </div>
                    <ul className="space-y-2">
                      {getStrengths(rec).map((item, idx) => (
                        <li key={idx} className="text-sm text-green-700 flex items-start gap-2">
                          <span className="text-green-500 mt-0.5">✓</span>
                          {item}
                        </li>
                      ))}
                    </ul>
                  </div>

                  <div className="bg-amber-50 rounded-lg p-4">
                    <div className="flex items-center gap-2 mb-3">
                      <Target className="text-amber-600" size={18} />
                      <h4 className="font-medium text-amber-900">Topics to Improve</h4>
                    </div>
                    <ul className="space-y-2">
                      {getImprovements(rec).map((item, idx) => (
                        <li key={idx} className="text-sm text-amber-700 flex items-start gap-2">
                          <span className="text-amber-500 mt-0.5">•</span>
                          {item}
                        </li>
                      ))}
                    </ul>
                  </div>

                  <div className="bg-blue-50 rounded-lg p-4">
                    <div className="flex items-center gap-2 mb-3">
                      <BookOpen className="text-blue-600" size={18} />
                      <h4 className="font-medium text-blue-900">Study Tips</h4>
                    </div>
                    <ul className="space-y-2">
                      {getStudyTips(rec).map((item, idx) => (
                        <li key={idx} className="text-sm text-blue-700 flex items-start gap-2">
                          <Zap className="text-blue-500 mt-0.5" size={14} />
                          {item}
                        </li>
                      ))}
                    </ul>
                  </div>
                </div>

                <div className="mt-4 pt-4 border-t border-gray-100 flex justify-end">
                  <Button variant="secondary" onClick={() => navigate(`/dashboard/student/exams/${rec.exam_id}/practice`)}>
                    Practice More
                  </Button>
                </div>
              </div>
            </Card>
          ))}
        </div>
      )}

      <Modal
        isOpen={subscribeModal}
        onClose={() => setSubscribeModal(false)}
        title="AI Recommendation Plans"
        size="lg"
      >
        <div className="space-y-4">
          {plansLoading ? (
            <div className="flex justify-center py-8">
              <Loader text="Loading plans..." />
            </div>
          ) : plans.length === 0 ? (
            <div className="text-center py-8 text-gray-500">
              No plans available at the moment
            </div>
          ) : (
            <>
              <p className="text-sm text-gray-500 mb-4">
                Choose a plan to unlock AI-powered recommendations and personalized learning insights.
              </p>
              <div className="grid gap-4">
                {plans.map((plan) => (
                  <div
                    key={plan.id}
                    className={`border-2 rounded-xl p-4 transition-colors ${
                      selectedPlan?.id === plan.id ? 'border-blue-500 bg-blue-50' : 'border-gray-200 hover:border-gray-300'
                    }`}
                  >
                    <div className="flex items-center justify-between">
                      <div className="flex-1">
                        <div className="flex items-center gap-2">
                          <h4 className="font-semibold text-gray-900">{plan.name}</h4>
                          {plan.is_featured && <Badge variant="warning">Popular</Badge>}
                        </div>
                        <p className="text-sm text-gray-500 mt-1">{plan.description}</p>
                        {plan.features && plan.features.length > 0 && (
                          <ul className="mt-2 space-y-1">
                            {plan.features.slice(0, 3).map((feature, idx) => (
                              <li key={idx} className="text-sm text-gray-600 flex items-center gap-2">
                                <Check size={14} className="text-green-500" />
                                {feature}
                              </li>
                            ))}
                          </ul>
                        )}
                      </div>
                      <div className="text-right ml-4">
                        <div className="text-2xl font-bold text-gray-900">{formatCurrency(plan.price)}</div>
                        <p className="text-xs text-gray-500">{plan.duration_days} days</p>
                        <Button
                          size="sm"
                          className="mt-2"
                          onClick={() => handleSubscribe(plan)}
                        >
                          Subscribe
                        </Button>
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            </>
          )}
        </div>
      </Modal>

      <Modal
        isOpen={!!selectedPlan}
        onClose={() => setSelectedPlan(null)}
        title={`Subscribe to ${selectedPlan?.name}`}
        footer={
          <div className="flex gap-3">
            <Button variant="secondary" onClick={() => setSelectedPlan(null)}>
              Cancel
            </Button>
            <Button
              variant="outline"
              onClick={handleRazorpaySubscribe}
              loading={processing}
              leftIcon={<CreditCard size={16} />}
            >
              Pay with Card/UPI
            </Button>
            <Button
              onClick={handleWalletSubscribe}
              loading={processing}
              disabled={wallet?.balance < selectedPlan?.price}
            >
              Pay from Wallet ({formatCurrency(wallet?.balance || 0)})
            </Button>
          </div>
        }
      >
        {selectedPlan && (
          <div className="space-y-4">
            <div className="bg-gray-50 rounded-lg p-4">
              <div className="flex justify-between items-center mb-2">
                <span className="text-gray-600">Plan</span>
                <span className="font-medium">{selectedPlan.name}</span>
              </div>
              <div className="flex justify-between items-center mb-2">
                <span className="text-gray-600">Duration</span>
                <span className="font-medium">{selectedPlan.duration_days} days</span>
              </div>
              <div className="flex justify-between items-center mb-2">
                <span className="text-gray-600">Features</span>
                <span className="font-medium">{selectedPlan.features?.length || 0} included</span>
              </div>
              <hr className="my-3" />
              <div className="flex justify-between items-center">
                <span className="text-lg font-semibold">Total</span>
                <span className="text-2xl font-bold text-blue-600">{formatCurrency(selectedPlan.price)}</span>
              </div>
            </div>
            {wallet?.balance < selectedPlan?.price && (
              <div className="p-3 bg-red-50 text-red-700 rounded-lg text-sm">
                Insufficient wallet balance. Please top up ₹{selectedPlan.price - wallet.balance} more or use Card/UPI.
              </div>
            )}
          </div>
        )}
      </Modal>
    </div>
  )
}
