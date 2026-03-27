export const ROLE_REDIRECT = {
  super_admin: '/dashboard/superadmin',
  admin_public: '/dashboard/admin-public',
  admin_college: '/dashboard/admin-college',
  teacher: '/dashboard/teacher',
  student_registered: '/dashboard/student',
  student_assigned: '/dashboard/student',
  support_agent: '/dashboard/support',
};

export const ROLE_LABELS = {
  super_admin: 'Super Admin',
  admin_public: 'Public Admin',
  admin_college: 'College Admin',
  teacher: 'Teacher',
  student_registered: 'Registered Student',
  student_assigned: 'Assigned Student',
  support_agent: 'Support Agent',
};

export const STATUS_COLORS = {
  exam: {
    draft: { bg: 'bg-gray-100', text: 'text-gray-700' },
    published: { bg: 'bg-blue-100', text: 'text-blue-700' },
    active: { bg: 'bg-green-100', text: 'text-green-700' },
    closed: { bg: 'bg-red-100', text: 'text-red-700' },
    cancelled: { bg: 'bg-yellow-100', text: 'text-yellow-700' },
  },
  attempt: {
    not_started: { bg: 'bg-gray-100', text: 'text-gray-700' },
    in_progress: { bg: 'bg-blue-100', text: 'text-blue-700' },
    submitted: { bg: 'bg-green-100', text: 'text-green-700' },
    auto_submitted: { bg: 'bg-orange-100', text: 'text-orange-700' },
    expired: { bg: 'bg-red-100', text: 'text-red-700' },
  },
  payment: {
    pending: { bg: 'bg-yellow-100', text: 'text-yellow-700' },
    captured: { bg: 'bg-green-100', text: 'text-green-700' },
    failed: { bg: 'bg-red-100', text: 'text-red-700' },
    refunded: { bg: 'bg-purple-100', text: 'text-purple-700' },
  },
};

export const GRADE_COLORS = {
  'A+': { bg: 'bg-green-100', text: 'text-green-700' },
  'A': { bg: 'bg-green-50', text: 'text-green-600' },
  'A-': { bg: 'bg-green-50', text: 'text-green-600' },
  'B+': { bg: 'bg-blue-100', text: 'text-blue-700' },
  'B': { bg: 'bg-blue-50', text: 'text-blue-600' },
  'B-': { bg: 'bg-blue-50', text: 'text-blue-600' },
  'C+': { bg: 'bg-yellow-100', text: 'text-yellow-700' },
  'C': { bg: 'bg-yellow-50', text: 'text-yellow-600' },
  'C-': { bg: 'bg-yellow-50', text: 'text-yellow-600' },
  'D': { bg: 'bg-orange-100', text: 'text-orange-700' },
  'F': { bg: 'bg-red-100', text: 'text-red-700' },
};

export const API_ROUTES = {
  AUTH: {
    LOGIN: '/auth/login',
    REGISTER: '/auth/register',
    REFRESH: '/auth/refresh',
    LOGOUT: '/auth/logout',
    ME: '/auth/me',
    FORGOT_PASSWORD: '/auth/forgot-password',
    RESET_PASSWORD: '/auth/reset-password',
    VERIFY_EMAIL: '/auth/verify-email',
    GOOGLE: '/auth/google',
    MAGIC_LINK_VERIFY: '/auth/magic-link/verify',
    RESEND_OTP: '/auth/resend-otp',
  },
  EXAMS: '/exams',
  EXAMS_MARKETPLACE: '/exams/marketplace',
  ATTEMPTS: '/attempts',
  RESULTS: '/results',
  PAYMENTS: '/payments',
  WALLET: '/wallet',
  USERS: '/users',
  INSTITUTES: '/institutes',
  SUBSCRIPTIONS: '/subscriptions',
  PLANS: '/plans',
  TICKETS: '/tickets',
};

export const EXAM_STATUS_LABELS = {
  draft: 'Draft',
  published: 'Published',
  active: 'Active',
  closed: 'Closed',
  cancelled: 'Cancelled',
};

export const ATTEMPT_STATUS_LABELS = {
  not_started: 'Not Started',
  in_progress: 'In Progress',
  submitted: 'Submitted',
  auto_submitted: 'Auto Submitted',
  expired: 'Expired',
};

export const PAYMENT_STATUS_LABELS = {
  pending: 'Pending',
  captured: 'Captured',
  failed: 'Failed',
  refunded: 'Refunded',
};
