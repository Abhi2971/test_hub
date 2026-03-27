import { useState } from 'react';
import { Link } from 'react-router-dom';
import { authService } from '../../services/authService';
import Input from '../../components/ui/Input';
import Button from '../../components/ui/Button';

const AuthLayout = ({ children }) => (
  <div className="min-h-screen bg-gray-50 flex items-center justify-center px-4">
    <div className="max-w-md w-full">
      <div className="text-center mb-8">
        <h1 className="text-3xl font-bold text-blue-600">ExamSaaS</h1>
        <p className="text-gray-500 mt-2">Your exam management platform</p>
      </div>
      {children}
    </div>
  </div>
);

export default function ForgotPassword() {
  const [email, setEmail] = useState('');
  const [otp, setOtp] = useState('');
  const [newPassword, setNewPassword] = useState('');
  const [confirmPassword, setConfirmPassword] = useState('');
  const [error, setError] = useState('');
  const [success, setSuccess] = useState(false);
  const [loading, setLoading] = useState(false);
  const [step, setStep] = useState(1);

  const handleEmailSubmit = async (e) => {
    e.preventDefault();
    setError('');
    setLoading(true);
    try {
      await authService.forgotPassword(email);
      setStep(2);
    } catch (err) {
      setError(err.response?.data?.message || 'Failed to send reset email.');
    } finally {
      setLoading(false);
    }
  };

  const handleResetSubmit = async (e) => {
    e.preventDefault();
    if (newPassword !== confirmPassword) {
      setError('Passwords do not match');
      return;
    }
    setError('');
    setLoading(true);
    try {
      await authService.resetPassword(email, otp, newPassword);
      setSuccess(true);
    } catch (err) {
      setError(err.response?.data?.message || 'Failed to reset password.');
    } finally {
      setLoading(false);
    }
  };

  if (success) {
    return (
      <AuthLayout>
        <div className="bg-white rounded-xl border border-gray-200 p-8 text-center">
          <div className="w-16 h-16 bg-green-100 rounded-full flex items-center justify-center mx-auto mb-4">
            <svg className="w-8 h-8 text-green-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
            </svg>
          </div>
          <h2 className="text-2xl font-bold text-gray-900 mb-2">Password Reset Complete</h2>
          <p className="text-gray-600 mb-6">
            Your password has been successfully reset. You can now sign in with your new password.
          </p>
          <Link to="/login" className="inline-block px-6 py-2.5 bg-blue-600 text-white rounded-lg font-medium hover:bg-blue-700">
            Back to Sign In
          </Link>
        </div>
      </AuthLayout>
    );
  }

  return (
    <AuthLayout>
      <div className="bg-white rounded-xl border border-gray-200 p-8">
        <h2 className="text-xl font-semibold text-gray-900 mb-6">
          {step === 1 ? 'Reset your password' : 'Create new password'}
        </h2>

        {step === 1 ? (
          <form onSubmit={handleEmailSubmit} className="space-y-5">
            {error && (
              <div className="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded-lg text-sm">
                {error}
              </div>
            )}

            <p className="text-gray-600 text-sm">
              Enter your email address and we'll send you an OTP to reset your password.
            </p>

            <Input
              label="Email"
              type="email"
              required
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              placeholder="you@example.com"
            />

            <Button type="submit" loading={loading} className="w-full">
              Send Reset Email
            </Button>

            <div className="text-center">
              <Link to="/login" className="text-sm text-blue-600 hover:underline">
                Back to Sign In
              </Link>
            </div>
          </form>
        ) : (
          <form onSubmit={handleResetSubmit} className="space-y-5">
            {error && (
              <div className="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded-lg text-sm">
                {error}
              </div>
            )}

            <p className="text-gray-600 text-sm">
              Enter the OTP sent to <strong>{email}</strong> and create a new password.
            </p>

            <Input
              label="OTP"
              type="text"
              required
              maxLength={6}
              value={otp}
              onChange={(e) => setOtp(e.target.value.replace(/\D/g, ''))}
              placeholder="000000"
            />

            <Input
              label="New Password"
              type="password"
              required
              value={newPassword}
              onChange={(e) => setNewPassword(e.target.value)}
              placeholder="Min. 8 characters"
            />

            <Input
              label="Confirm New Password"
              type="password"
              required
              value={confirmPassword}
              onChange={(e) => setConfirmPassword(e.target.value)}
              placeholder="Repeat password"
            />

            <Button type="submit" loading={loading} className="w-full">
              Reset Password
            </Button>

            <div className="text-center">
              <Link to="/login" className="text-sm text-blue-600 hover:underline">
                Back to Sign In
              </Link>
            </div>
          </form>
        )}
      </div>
    </AuthLayout>
  );
}
