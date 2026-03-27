import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../../contexts/AuthContext';
import { paymentService } from '../../services/paymentService';
import { resultService } from '../../services/resultService';
import { examService } from '../../services/examService';
import Card from '../../components/ui/Card';
import Button from '../../components/ui/Button';
import Badge from '../../components/ui/Badge';
import Modal from '../../components/ui/Modal';
import Input from '../../components/ui/Input';
import { GRADE_COLORS } from '../../utils/constants';

const WalletBalanceCard = ({ balance, onTopUp }) => (
  <Card header="Wallet Balance">
    <div className="text-center py-4">
      <p className="text-4xl font-bold text-gray-900">₹{balance?.toFixed(2) || '0.00'}</p>
      <p className="text-sm text-gray-500 mt-2">Available balance</p>
      <Button onClick={onTopUp} className="mt-4" variant="primary">
        Top Up
      </Button>
    </div>
  </Card>
);

const UpcomingExamsCard = ({ exams, onStart }) => (
  <Card header="Upcoming Exams">
    {exams.length === 0 ? (
      <p className="text-gray-500 text-center py-4">No upcoming exams</p>
    ) : (
      <div className="space-y-3">
        {exams.map((exam) => (
          <div key={exam.id} className="flex items-center justify-between p-3 bg-gray-50 rounded-lg">
            <div>
              <p className="font-medium text-gray-900">{exam.title}</p>
              <p className="text-sm text-gray-500">{exam.duration_minutes} min • {exam.total_marks} marks</p>
            </div>
            <Button size="sm" onClick={() => onStart(exam.id)}>
              Start
            </Button>
          </div>
        ))}
      </div>
    )}
  </Card>
);

const RecentResultsCard = ({ results }) => (
  <Card header="Recent Results">
    {results.length === 0 ? (
      <p className="text-gray-500 text-center py-4">No results yet</p>
    ) : (
      <div className="space-y-3">
        {results.map((result) => (
          <div key={result.id} className="flex items-center justify-between p-3 bg-gray-50 rounded-lg">
            <div>
              <p className="font-medium text-gray-900">{result.exam_title}</p>
              <p className="text-sm text-gray-500">
                {result.score}/{result.total_marks} • {result.percentage}%
              </p>
            </div>
            <Badge className={GRADE_COLORS[result.grade]?.bg + ' ' + GRADE_COLORS[result.grade]?.text}>
              {result.grade}
            </Badge>
          </div>
        ))}
      </div>
    )}
  </Card>
);

const CertificatesCard = ({ certificates }) => (
  <Card header="Certificates">
    {certificates.length === 0 ? (
      <p className="text-gray-500 text-center py-4">No certificates earned yet</p>
    ) : (
      <div className="space-y-3">
        {certificates.map((cert) => (
          <div key={cert.id} className="flex items-center justify-between p-3 bg-gray-50 rounded-lg">
            <div>
              <p className="font-medium text-gray-900">{cert.exam_title}</p>
              <p className="text-sm text-gray-500">{new Date(cert.created_at).toLocaleDateString()}</p>
            </div>
            <a href={cert.download_url} target="_blank" rel="noopener noreferrer">
              <Button size="sm" variant="secondary">Download</Button>
            </a>
          </div>
        ))}
      </div>
    )}
  </Card>
);

const AIRecommendationsCard = ({ recommendations }) => (
  <Card header="AI Recommendations">
    {recommendations.length === 0 ? (
      <p className="text-gray-500 text-center py-4">Complete exams to get AI recommendations</p>
    ) : (
      <div className="space-y-2">
        {recommendations.map((rec, idx) => (
          <div key={idx} className="flex items-start gap-2 text-sm">
            <span className="text-blue-600 mt-1">•</span>
            <span className="text-gray-700">{rec}</span>
          </div>
        ))}
      </div>
    )}
  </Card>
);

export default function StudentDashboard() {
  const { user } = useAuth();
  const navigate = useNavigate();
  const [wallet, setWallet] = useState({ balance: 0 });
  const [results, setResults] = useState([]);
  const [exams, setExams] = useState([]);
  const [certificates, setCertificates] = useState([]);
  const [recommendations, setRecommendations] = useState([]);
  const [loading, setLoading] = useState(true);
  const [showTopUpModal, setShowTopUpModal] = useState(false);
  const [topUpAmount, setTopUpAmount] = useState('');
  const [topUpLoading, setTopUpLoading] = useState(false);

  const predefinedAmounts = [50, 100, 200, 500, 1000, 2000];

  useEffect(() => {
    const fetchData = async () => {
      try {
        const [walletRes, resultsRes, examsRes] = await Promise.all([
          paymentService.getWallet().catch(() => ({ data: { data: { balance: 0 } } })),
          resultService.getResults({ limit: 3 }).catch(() => ({ data: { data: { items: [] } } })),
          examService.getExams({ status: 'active', limit: 5 }).catch(() => ({ data: { data: { items: [] } } })),
        ]);
        setWallet(walletRes.data?.data || { balance: 0 });
        setResults(resultsRes.data?.data?.items || []);
        setExams(examsRes.data?.data?.items || []);
      } catch (err) {
        console.error(err);
      } finally {
        setLoading(false);
      }
    };
    fetchData();
  }, []);

  const handleTopUp = async (amount) => {
    setTopUpLoading(true);
    try {
      const response = await paymentService.topUp(amount);
      const orderData = response.data.data;
      
      await paymentService.initiateRazorpay(
        {
          key: import.meta.env.VITE_RAZORPAY_KEY_ID,
          amount: orderData.amount,
          currency: orderData.currency || 'INR',
          name: 'ExamSaaS Wallet Top Up',
          description: `Top up of ₹${amount}`,
          order_id: orderData.id,
          handler: async (paymentResponse) => {
            await paymentService.verifyPayment(
              orderData.id,
              paymentResponse.razorpay_payment_id,
              paymentResponse.razorpay_signature
            );
            setShowTopUpModal(false);
            const walletRes = await paymentService.getWallet();
            setWallet(walletRes.data?.data || { balance: 0 });
          },
        },
        () => {},
        () => {}
      );
    } catch (err) {
      console.error('Top up failed:', err);
    } finally {
      setTopUpLoading(false);
    }
  };

  const handleStartExam = (examId) => {
    navigate(`/exam/${examId}/take`);
  };

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <h1 className="text-2xl font-bold text-gray-900">
          Welcome, {user?.first_name}!
        </h1>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        <WalletBalanceCard balance={wallet.balance} onTopUp={() => setShowTopUpModal(true)} />
        <UpcomingExamsCard exams={exams} onStart={handleStartExam} />
        <RecentResultsCard results={results} />
        <CertificatesCard certificates={certificates} />
        <AIRecommendationsCard recommendations={recommendations} />
      </div>

      <Modal
        isOpen={showTopUpModal}
        onClose={() => setShowTopUpModal(false)}
        title="Top Up Wallet"
        footer={
          <div className="flex gap-3">
            <Button variant="secondary" onClick={() => setShowTopUpModal(false)}>
              Cancel
            </Button>
            <Button
              loading={topUpLoading}
              disabled={!topUpAmount || parseFloat(topUpAmount) <= 0}
              onClick={() => handleTopUp(parseFloat(topUpAmount))}
            >
              Top Up ₹{topUpAmount || 0}
            </Button>
          </div>
        }
      >
        <div className="space-y-4">
          <p className="text-sm text-gray-600">Select amount or enter custom:</p>
          <div className="grid grid-cols-3 gap-2">
            {predefinedAmounts.map((amount) => (
              <button
                key={amount}
                onClick={() => setTopUpAmount(amount.toString())}
                className={`py-2 px-3 rounded-lg border text-sm font-medium transition ${
                  topUpAmount === amount.toString()
                    ? 'border-blue-500 bg-blue-50 text-blue-700'
                    : 'border-gray-200 hover:border-gray-300'
                }`}
              >
                ₹{amount}
              </button>
            ))}
          </div>
          <Input
            label="Custom Amount"
            type="number"
            min={1}
            value={topUpAmount}
            onChange={(e) => setTopUpAmount(e.target.value)}
            placeholder="Enter amount in rupees"
          />
        </div>
      </Modal>
    </div>
  );
}
