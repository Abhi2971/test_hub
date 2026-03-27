import { useState, useEffect } from 'react';
import { useParams, useNavigate, Link } from 'react-router-dom';
import { authService } from '../../services/authService';
import { useAuth } from '../../contexts/AuthContext';
import { ROLE_REDIRECT } from '../../utils/constants';
import Loader from '../../components/ui/Loader';
import Button from '../../components/ui/Button';
import Card from '../../components/ui/Card';

export default function MagicLinkHandler() {
  const { token } = useParams();
  const navigate = useNavigate();
  const { login } = useAuth();
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [success, setSuccess] = useState(false);
  const [examId, setExamId] = useState(null);

  useEffect(() => {
    const verifyMagicLink = async () => {
      try {
        const response = await authService.verifyMagicLink(token);
        const { access_token, refresh_token, user, exam_id } = response.data.data;
        
        localStorage.setItem('auth_access_token', access_token);
        localStorage.setItem('auth_refresh_token', refresh_token);
        localStorage.setItem('auth_user', JSON.stringify(user));
        
        setSuccess(true);
        setExamId(exam_id);
        
        setTimeout(() => {
          if (exam_id) {
            navigate(`/exam/${exam_id}/take`);
          } else {
            navigate(ROLE_REDIRECT[user.role] || '/dashboard/student');
          }
        }, 1500);
      } catch (err) {
        setError(err.response?.data?.message || 'Invalid or expired magic link');
      } finally {
        setLoading(false);
      }
    };

    if (token) {
      verifyMagicLink();
    }
  }, [token, navigate]);

  if (loading) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-center">
          <Loader size="lg" text="Verifying magic link..." />
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center px-4">
        <Card className="max-w-md w-full text-center">
          <div className="w-16 h-16 bg-red-100 rounded-full flex items-center justify-center mx-auto mb-4">
            <svg className="w-8 h-8 text-red-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
            </svg>
          </div>
          <h2 className="text-xl font-bold text-gray-900 mb-2">Link Expired or Invalid</h2>
          <p className="text-gray-600 mb-6">{error}</p>
          <Link to="/dashboard">
            <Button variant="secondary">Go to Dashboard</Button>
          </Link>
        </Card>
      </div>
    );
  }

  if (success) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <Card className="max-w-md w-full text-center">
          <div className="w-16 h-16 bg-green-100 rounded-full flex items-center justify-center mx-auto mb-4">
            <svg className="w-8 h-8 text-green-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
            </svg>
          </div>
          <h2 className="text-xl font-bold text-gray-900 mb-2">Link Verified!</h2>
          <p className="text-gray-600 mb-4">Redirecting you to the exam...</p>
          <Loader size="sm" />
        </Card>
      </div>
    );
  }

  return null;
}
