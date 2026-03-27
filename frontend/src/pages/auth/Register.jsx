import { useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { authService } from '../../services/authService';
import Input from '../../components/ui/Input';
import Button from '../../components/ui/Button';
import Select from '../../components/ui/Select';

export default function Register() {
  const [formData, setFormData] = useState({
    email: '',
    password: '',
    confirm_password: '',
    first_name: '',
    last_name: '',
    role: 'student_registered',
  });
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);
  const [otpSent, setOtpSent] = useState(false);
  const [otp, setOtp] = useState('');
  const [step, setStep] = useState(1);
  const navigate = useNavigate();

  const roleOptions = [
    { value: 'student_registered', label: 'Student' },
    { value: 'teacher', label: 'Teacher / Educator' },
    { value: 'admin_college', label: 'College Administrator' },
    { value: 'admin_public', label: 'Organization Admin' },
  ];

  const handleChange = (e) => {
    setFormData({ ...formData, [e.target.name]: e.target.value });
  };

  const handleRegister = async (e) => {
    e.preventDefault();
    if (formData.password !== formData.confirm_password) {
      setError('Passwords do not match');
      return;
    }
    setError('');
    setLoading(true);
    try {
      await authService.register(formData);
      setOtpSent(true);
      setStep(2);
    } catch (err) {
      setError(err.response?.data?.message || 'Registration failed. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  const handleVerify = async (e) => {
    e.preventDefault();
    setError('');
    setLoading(true);
    try {
      await authService.verifyEmail(formData.email, otp);
      navigate('/login?registered=true');
    } catch (err) {
      setError(err.response?.data?.message || 'Verification failed. Please check your OTP.');
    } finally {
      setLoading(false);
    }
  };

  const handleResend = async () => {
    try {
      await authService.resendOTP(formData.email, 'verify_email');
    } catch (err) {
      setError(err.response?.data?.message || 'Failed to resend OTP');
    }
  };

  if (step === 2 && otpSent) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center px-4 py-12">
        <div className="w-full max-w-md">
          <div className="flex items-center gap-2 mb-8 justify-center">
            <div className="w-9 h-9 bg-blue-600 rounded-xl flex items-center justify-center">
              <svg className="w-5 h-5 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
              </svg>
            </div>
            <span className="text-xl font-bold text-gray-900">ExamSaaS</span>
          </div>

          <div className="bg-white rounded-2xl border border-gray-200 p-8 shadow-sm">
            <div className="text-center mb-6">
              <div className="w-14 h-14 bg-green-100 rounded-full flex items-center justify-center mx-auto mb-4">
                <svg className="w-7 h-7 text-green-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M3 8l7.89 5.26a2 2 0 002.22 0L21 8M5 19h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v10a2 2 0 002 2z" />
                </svg>
              </div>
              <h2 className="text-xl font-bold text-gray-900">Verify your email</h2>
              <p className="mt-2 text-gray-500 text-sm">
                We have sent a 6-digit OTP to <span className="font-medium text-gray-700">{formData.email}</span>
              </p>
            </div>

            <form onSubmit={handleVerify} className="space-y-5">
              {error && (
                <div className="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded-xl text-sm">
                  {error}
                </div>
              )}

              <Input
                label="Enter OTP"
                type="text"
                required
                maxLength={6}
                value={otp}
                onChange={(e) => setOtp(e.target.value.replace(/\D/g, ''))}
                placeholder="000000"
              />

              <Button type="submit" loading={loading} className="w-full" size="lg">
                Verify & Continue
              </Button>

              <div className="text-center">
                <button type="button" onClick={handleResend} className="text-sm text-blue-600 hover:underline font-medium">
                  Did not receive it? Resend OTP
                </button>
              </div>
            </form>

            <div className="mt-6 pt-6 border-t border-gray-100 text-center">
              <Link to="/login" className="text-sm text-gray-500 hover:text-blue-600 transition">
                &larr; Back to Sign In
              </Link>
            </div>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50 flex">
      {/* Left side - Branding */}
      <div className="hidden lg:flex lg:w-1/2 bg-gradient-to-br from-blue-600 via-blue-700 to-blue-800 relative overflow-hidden">
        <div className="absolute inset-0 bg-[radial-gradient(ellipse_at_bottom_right,_var(--tw-gradient-stops))] from-blue-500/30 via-transparent to-transparent" />
        <div className="relative z-10 flex flex-col justify-between p-12 w-full">
          <Link to="/" className="flex items-center gap-3">
            <div className="w-10 h-10 bg-white/20 backdrop-blur-sm rounded-xl flex items-center justify-center">
              <svg className="w-6 h-6 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
              </svg>
            </div>
            <span className="text-2xl font-bold text-white">ExamSaaS</span>
          </Link>

          <div className="space-y-8">
            <div className="space-y-4">
              {[
                {
                  icon: (
                    <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M9 12l2 2 4-4m5.618-4.016A11.955 11.955 0 0112 2.944a11.955 11.955 0 01-8.618 3.04A12.02 12.02 0 003 9c0 5.591 3.824 10.29 9 11.622 5.176-1.332 9-6.03 9-11.622 0-1.042-.133-2.052-.382-3.016z" />
                    </svg>
                  ),
                  text: 'Secure, proctored online examinations',
                },
                {
                  icon: (
                    <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M13 10V3L4 14h7v7l9-11h-7z" />
                    </svg>
                  ),
                  text: 'Instant results and detailed analytics',
                },
                {
                  icon: (
                    <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M9.663 17h4.673M12 3v1m6.364 1.636l-.707.707M21 12h-1M4 12H3m3.343-5.657l-.707-.707m2.828 9.9a5 5 0 117.072 0l-.548.547A3.374 3.374 0 0014 18.469V19a2 2 0 11-4 0v-.531c0-.895-.356-1.754-.988-2.386l-.548-.547z" />
                    </svg>
                  ),
                  text: 'AI-powered question generation',
                },
                {
                  icon: (
                    <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M12 18h.01M8 21h8a2 2 0 002-2V5a2 2 0 00-2-2H8a2 2 0 00-2 2v14a2 2 0 002 2z" />
                    </svg>
                  ),
                  text: 'Works on any device, anywhere',
                },
              ].map((item, i) => (
                <div key={i} className="flex items-center gap-3">
                  <div className="w-8 h-8 bg-white/20 rounded-lg flex items-center justify-center text-white">
                    {item.icon}
                  </div>
                  <span className="text-white font-medium">{item.text}</span>
                </div>
              ))}
            </div>

            <div className="bg-white/10 backdrop-blur-sm rounded-2xl p-6">
              <p className="text-blue-100 italic leading-relaxed">
                "ExamSaaS transformed how we conduct examinations. What used to take days 
                now takes hours. The AI proctoring gives us complete confidence in results."
              </p>
              <div className="mt-4 flex items-center gap-3">
                <div className="w-8 h-8 bg-blue-400/50 rounded-full flex items-center justify-center text-white text-xs font-semibold">
                  PS
                </div>
                <div>
                  <p className="text-white text-sm font-medium">Dr. Priya Sharma</p>
                  <p className="text-blue-200 text-xs">Director, Delhi University</p>
                </div>
              </div>
            </div>
          </div>

          <p className="text-sm text-blue-200">
            Free to start. No credit card required.
          </p>
        </div>
      </div>

      {/* Right side - Form */}
      <div className="flex-1 flex items-center justify-center px-4 sm:px-6 lg:px-12 py-12">
        <div className="w-full max-w-md">
          {/* Mobile logo */}
          <div className="lg:hidden flex items-center gap-2 mb-8 justify-center">
            <div className="w-9 h-9 bg-blue-600 rounded-xl flex items-center justify-center">
              <svg className="w-5 h-5 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
              </svg>
            </div>
            <span className="text-xl font-bold text-gray-900">ExamSaaS</span>
          </div>

          <div className="text-center lg:text-left mb-8">
            <h2 className="text-2xl font-bold text-gray-900">Create your account</h2>
            <p className="mt-2 text-gray-500">
              Get started free. No credit card required.
            </p>
          </div>

          <form onSubmit={handleRegister} className="space-y-4">
            {error && (
              <div className="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded-xl text-sm">
                {error}
              </div>
            )}

            <div className="grid grid-cols-2 gap-4">
              <Input
                label="First Name"
                name="first_name"
                required
                value={formData.first_name}
                onChange={handleChange}
                placeholder="John"
              />
              <Input
                label="Last Name"
                name="last_name"
                required
                value={formData.last_name}
                onChange={handleChange}
                placeholder="Smith"
              />
            </div>

            <Input
              label="Email address"
              type="email"
              name="email"
              required
              value={formData.email}
              onChange={handleChange}
              placeholder="you@institution.edu.in"
            />

            <Select
              label="I am a..."
              name="role"
              options={roleOptions}
              value={formData.role}
              onChange={(value) => setFormData({ ...formData, role: value })}
            />

            <Input
              label="Password"
              type="password"
              name="password"
              required
              minLength={8}
              value={formData.password}
              onChange={handleChange}
              placeholder="Min. 8 characters"
            />

            <Input
              label="Confirm Password"
              type="password"
              name="confirm_password"
              required
              value={formData.confirm_password}
              onChange={handleChange}
              placeholder="Repeat your password"
            />

            <div className="flex items-start gap-2">
              <input
                id="terms"
                type="checkbox"
                required
                className="mt-1 rounded border-gray-300 text-blue-600 focus:ring-blue-500"
              />
              <label htmlFor="terms" className="text-sm text-gray-500">
                I agree to the{' '}
                <a href="#" className="text-blue-600 hover:underline">Terms of Service</a>{' '}
                and{' '}
                <a href="#" className="text-blue-600 hover:underline">Privacy Policy</a>
              </label>
            </div>

            <Button type="submit" loading={loading} className="w-full" size="lg">
              Create Account
            </Button>
          </form>

          <p className="mt-8 text-center text-sm text-gray-500">
            Already have an account?{' '}
            <Link to="/login" className="text-blue-600 hover:underline font-medium">
              Sign in
            </Link>
          </p>
        </div>
      </div>
    </div>
  );
}
