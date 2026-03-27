import { BrowserRouter, Routes, Route, Navigate, Outlet, useLocation } from 'react-router-dom';
import { ThemeProvider } from './contexts/ThemeContext';
import { ToastProvider } from './contexts/ToastContext';
import { AuthProvider } from './contexts/AuthContext';
import useAuth from './hooks/useAuth';
import { ROLE_REDIRECT } from './utils/constants';
import Loader from './components/ui/Loader';

import Login from './pages/auth/Login';
import Register from './pages/auth/Register';
import ForgotPassword from './pages/auth/ForgotPassword';
import ResetPassword from './pages/auth/ResetPassword';
import VerifyEmail from './pages/auth/VerifyEmail';
import CertificateVerify from './pages/auth/CertificateVerify';
import MagicLinkHandler from './pages/auth/MagicLinkHandler';

import Home from './pages/landing/Home';
import About from './pages/landing/About';
import Features from './pages/landing/Features';
import Pricing from './pages/landing/Pricing';

import SuperAdminDashboard from './pages/dashboards/SuperAdminDashboard';
import SuperAdminLayout from './pages/superadmin/SuperAdminLayout';
import AdminPublicDashboard from './pages/dashboards/AdminPublicDashboard';
import AdminCollegeDashboard from './pages/dashboards/AdminCollegeDashboard';
import TeacherDashboard from './pages/dashboards/TeacherDashboard';
import StudentDashboard from './pages/dashboards/StudentDashboard';
import SupportDashboard from './pages/dashboards/SupportDashboard';

import TakeExam from './pages/exam/TakeExam';
import ExamList from './pages/exams/ExamList';
import ExamCreate from './pages/exams/ExamCreate';
import ExamDetail from './pages/exams/ExamDetail';
import ExamMarketplace from './pages/exams/ExamMarketplace';

import ResultList from './pages/results/ResultList';
import ResultDetail from './pages/results/ResultDetail';
import QuestionList from './pages/questions/QuestionList';
import QuestionCreate from './pages/questions/QuestionCreate';
import Profile from './pages/Profile';
import NotFound from './pages/NotFound';

import Institutes from './pages/superadmin/Institutes';
import Plans from './pages/superadmin/Plans';
import Payments from './pages/superadmin/Payments';
import AuditLogs from './pages/superadmin/AuditLogs';
import Settings from './pages/superadmin/Settings';
import PlatformAnalytics from './pages/superadmin/PlatformAnalytics';
import Exams from './pages/superadmin/Exams';

import ExamManagement from './pages/admin/ExamManagement';
import QuestionBank from './pages/admin/QuestionBank';
import PDFUpload from './pages/admin/PDFUpload';
import EbookManagement from './pages/admin/EbookManagement';
import Students from './pages/admin/Students';
import Teachers from './pages/admin/Teachers';
import InstituteSettings from './pages/admin/InstituteSettings';
import Users from './pages/admin/Users';

import CreateExam from './pages/teacher/CreateExam';
import TeacherExamList from './pages/teacher/ExamList';
import StudentUpload from './pages/teacher/StudentUpload';
import LiveMonitor from './pages/teacher/LiveMonitor';
import ResultsView from './pages/teacher/ResultsView';

import AvailableExams from './pages/student/AvailableExams';
import Marketplace from './pages/student/Marketplace';
import MyAttempts from './pages/student/MyAttempts';
import EbookLibrary from './pages/student/EbookLibrary';
import AIRecommendations from './pages/student/AIRecommendations';
import Certificates from './pages/student/Certificates';
import Wallet from './pages/student/Wallet';

import TicketList from './pages/support/TicketList';
import TicketDetail from './pages/support/TicketDetail';

import PublicCertificateVerify from './pages/public/CertificateVerify';

function ProtectedRoute({ allowedRoles }) {
  const { user, isAuthenticated, isLoading } = useAuth();
  const location = useLocation();

  if (isLoading) {
    return <Loader fullPage text="Loading..." />;
  }

  if (!isAuthenticated) {
    return <Navigate to={`/login?redirect=${encodeURIComponent(location.pathname)}`} replace />;
  }

  if (allowedRoles && !allowedRoles.includes(user?.role)) {
    const redirectPath = ROLE_REDIRECT[user?.role] || '/login';
    return <Navigate to={redirectPath} replace />;
  }

  return <Outlet />;
}

function DashboardRoute() {
  const { user, isAuthenticated, isLoading } = useAuth();

  if (isLoading) {
    return <Loader fullPage text="Loading..." />;
  }

  if (!isAuthenticated) {
    return <Home />;
  }

  const redirectPath = ROLE_REDIRECT[user?.role] || '/login';
  return <Navigate to={redirectPath} replace />;
}

function App() {
  return (
    <ThemeProvider>
      <ToastProvider>
        <AuthProvider>
          <BrowserRouter>
            <Routes>
              <Route path="/login" element={<Login />} />
              <Route path="/register" element={<Register />} />
              <Route path="/forgot-password" element={<ForgotPassword />} />
              <Route path="/reset-password" element={<ResetPassword />} />
              <Route path="/verify-email" element={<VerifyEmail />} />
              <Route path="/certificates/verify/:code" element={<CertificateVerify />} />
              <Route path="/exam/join/:token" element={<MagicLinkHandler />} />
              <Route path="/verify/:code" element={<PublicCertificateVerify />} />

            <Route element={<ProtectedRoute allowedRoles={['super_admin']} />}>
              <Route element={<SuperAdminLayout />}>
                <Route path="/dashboard/superadmin" element={<SuperAdminDashboard />} />
                <Route path="/superadmin/institutes" element={<Institutes />} />
                <Route path="/superadmin/users" element={<Users />} />
                <Route path="/superadmin/plans" element={<Plans />} />
                <Route path="/superadmin/exams" element={<Exams />} />
                <Route path="/superadmin/payments" element={<Payments />} />
                <Route path="/superadmin/audit-logs" element={<AuditLogs />} />
                <Route path="/superadmin/analytics" element={<PlatformAnalytics />} />
                <Route path="/superadmin/settings" element={<Settings />} />
                <Route path="/support/tickets" element={<TicketList />} />
                <Route path="/support/tickets/:id" element={<TicketDetail />} />
              </Route>
            </Route>

              <Route element={<ProtectedRoute allowedRoles={['admin_public']} />}>
                <Route path="/dashboard/admin-public" element={<AdminPublicDashboard />} />
                <Route path="/admin/exams" element={<ExamManagement />} />
                <Route path="/admin/questions" element={<QuestionBank />} />
                <Route path="/admin/pdf-upload" element={<PDFUpload />} />
                <Route path="/admin/ebooks" element={<EbookManagement />} />
                <Route path="/admin/students" element={<Students />} />
                <Route path="/admin/teachers" element={<Teachers />} />
                <Route path="/admin/settings" element={<InstituteSettings />} />
                <Route path="/admin/users" element={<Users />} />
              </Route>

              <Route element={<ProtectedRoute allowedRoles={['admin_college']} />}>
                <Route path="/dashboard/admin-college" element={<AdminCollegeDashboard />} />
                <Route path="/admin/exams" element={<ExamManagement />} />
                <Route path="/admin/questions" element={<QuestionBank />} />
                <Route path="/admin/pdf-upload" element={<PDFUpload />} />
                <Route path="/admin/ebooks" element={<EbookManagement />} />
                <Route path="/admin/students" element={<Students />} />
                <Route path="/admin/teachers" element={<Teachers />} />
                <Route path="/admin/settings" element={<InstituteSettings />} />
                <Route path="/admin/users" element={<Users />} />
              </Route>

              <Route element={<ProtectedRoute allowedRoles={['teacher']} />}>
                <Route path="/dashboard/teacher" element={<TeacherDashboard />} />
                <Route path="/teacher/exams" element={<TeacherExamList />} />
                <Route path="/teacher/exams/create" element={<CreateExam />} />
                <Route path="/teacher/exams/:id/edit" element={<CreateExam />} />
                <Route path="/teacher/students/upload" element={<StudentUpload />} />
                <Route path="/teacher/exams/:id/monitor" element={<LiveMonitor />} />
                <Route path="/teacher/exams/:id/results" element={<ResultsView />} />
              </Route>

              <Route element={<ProtectedRoute allowedRoles={['student_registered', 'student_assigned']} />}>
                <Route path="/dashboard/student" element={<StudentDashboard />} />
                <Route path="/student/exams" element={<AvailableExams />} />
                <Route path="/student/marketplace" element={<Marketplace />} />
                <Route path="/student/attempts" element={<MyAttempts />} />
                <Route path="/student/ebooks" element={<EbookLibrary />} />
                <Route path="/student/recommendations" element={<AIRecommendations />} />
                <Route path="/student/certificates" element={<Certificates />} />
                <Route path="/student/wallet" element={<Wallet />} />
                <Route path="/exam/:id/take" element={<TakeExam />} />
              </Route>

              <Route element={<ProtectedRoute allowedRoles={['support_agent']} />}>
                <Route path="/dashboard/support" element={<SupportDashboard />} />
              </Route>

              <Route path="/profile" element={<Profile />} />
              <Route path="/exams" element={<ExamList />} />
              <Route path="/exams/create" element={<ExamCreate />} />
              <Route path="/exams/:id" element={<ExamDetail />} />
              <Route path="/exams/marketplace" element={<ExamMarketplace />} />
              <Route path="/results" element={<ResultList />} />
              <Route path="/results/:id" element={<ResultDetail />} />
              <Route path="/questions" element={<QuestionList />} />
              <Route path="/questions/create" element={<QuestionCreate />} />

              {/* Public landing pages */}
              <Route path="/about" element={<About />} />
              <Route path="/features" element={<Features />} />
              <Route path="/pricing" element={<Pricing />} />

              {/* Root: dashboard for authenticated, login for unauthenticated */}
              <Route path="/" element={<DashboardRoute />} />
              <Route path="*" element={<NotFound />} />
            </Routes>
          </BrowserRouter>
        </AuthProvider>
      </ToastProvider>
    </ThemeProvider>
  );
}

export default App;
