import { useState, useRef, useEffect } from 'react'
import { Link, useLocation } from 'react-router-dom'
import { useAuth } from '../../contexts/AuthContext'
import { useTheme } from '../../contexts/ThemeContext'
import { ROLE_LABELS } from '../../utils/constants'

export default function Topbar({ onMenuClick, isSidebarOpen }) {
  const { user, logout } = useAuth()
  const { isDark, toggleTheme } = useTheme()
  const location = useLocation()
  const [dropdownOpen, setDropdownOpen] = useState(false)
  const dropdownRef = useRef(null)

    const getPageTitle = () => {
    const path = location.pathname
    const titles = {
      '/dashboard/superadmin': 'Super Admin Dashboard',
      '/superadmin/institutes': 'Institutes',
      '/superadmin/users': 'All Users',
      '/superadmin/plans': 'Plans & Billing',
      '/superadmin/payments': 'Payments',
      '/superadmin/audit-logs': 'Audit Logs',
      '/superadmin/analytics': 'Platform Analytics',
      '/support/tickets': 'Support Tickets',
      '/superadmin/settings': 'Settings',
      '/dashboard/admin-public': 'Public Admin Dashboard',
      '/dashboard/admin-college': 'College Admin Dashboard',
      '/dashboard/teacher': 'Teacher Dashboard',
      '/dashboard/student': 'Student Dashboard',
      '/dashboard/support': 'Support Dashboard',
      '/exams': 'Exams',
      '/questions': 'Questions',
      '/results': 'Results',
      '/profile': 'Profile',
      '/tickets': 'Tickets',
      '/certificates': 'Certificates',
      '/wallet': 'Wallet',
      '/admin/users': 'Users',
      '/dashboard/subscription': 'Subscription',
      '/dashboard/plans': 'Plans',
      '/dashboard/institutes': 'Institutes',
      '/dashboard/analytics': 'Analytics',
    }
    return titles[path] || 'Dashboard'
  }

  useEffect(() => {
    const handleClickOutside = (event) => {
      if (dropdownRef.current && !dropdownRef.current.contains(event.target)) {
        setDropdownOpen(false)
      }
    }
    document.addEventListener('mousedown', handleClickOutside)
    return () => document.removeEventListener('mousedown', handleClickOutside)
  }, [])

  return (
    <header className="fixed top-0 left-0 right-0 h-16 bg-white dark:bg-gray-800 border-b border-gray-200 dark:border-gray-700 z-40 flex items-center justify-between px-4">
      <div className="flex items-center gap-4">
        <button
          onClick={onMenuClick}
          className="lg:hidden p-2 rounded-lg hover:bg-gray-100 dark:hover:bg-gray-700"
        >
          <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            {isSidebarOpen ? (
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
            ) : (
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 6h16M4 12h16M4 18h16" />
            )}
          </svg>
        </button>
        <h2 className="text-lg font-semibold text-gray-800 dark:text-white">
          {getPageTitle()}
        </h2>
      </div>

      <div className="flex items-center gap-4">
        <button
          onClick={toggleTheme}
          className="p-2 rounded-lg hover:bg-gray-100 dark:hover:bg-gray-700"
        >
          {isDark ? (
            <svg className="w-5 h-5 text-yellow-500" fill="currentColor" viewBox="0 0 20 20">
              <path fillRule="evenodd" d="M10 2a1 1 0 011 1v1a1 1 0 11-2 0V3a1 1 0 011-1zm4 8a4 4 0 11-8 0 4 4 0 018 0zm-.464 4.95l.707.707a1 1 0 001.414-1.414l-.707-.707a1 1 0 00-1.414 1.414zm2.12-10.607a1 1 0 010 1.414l-.706.707a1 1 0 11-1.414-1.414l.707-.707a1 1 0 011.414 0zM17 11a1 1 0 100-2h-1a1 1 0 100 2h1zm-7 4a1 1 0 011 1v1a1 1 0 11-2 0v-1a1 1 0 011-1zM5.05 6.464A1 1 0 106.465 5.05l-.708-.707a1 1 0 00-1.414 1.414l.707.707zm1.414 8.486l-.707.707a1 1 0 01-1.414-1.414l.707-.707a1 1 0 011.414 1.414zM4 11a1 1 0 100-2H3a1 1 0 000 2h1z" clipRule="evenodd" />
            </svg>
          ) : (
            <svg className="w-5 h-5 text-gray-600" fill="currentColor" viewBox="0 0 20 20">
              <path d="M17.293 13.293A8 8 0 016.707 2.707a8.001 8.001 0 1010.586 10.586z" />
            </svg>
          )}
        </button>

        <button className="relative p-2 rounded-lg hover:bg-gray-100 dark:hover:bg-gray-700">
          <svg className="w-5 h-5 text-gray-600 dark:text-gray-300" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 17h5l-1.405-1.405A2.032 2.032 0 0118 14.158V11a6.002 6.002 0 00-4-5.659V5a2 2 0 10-4 0v.341C7.67 6.165 6 8.388 6 11v3.159c0 .538-.214 1.055-.595 1.436L4 17h5m6 0v1a3 3 0 11-6 0v-1m6 0H9" />
          </svg>
          <span className="absolute top-1 right-1 w-2 h-2 bg-red-500 rounded-full"></span>
        </button>

        <div className="relative" ref={dropdownRef}>
          <button
            onClick={() => setDropdownOpen(!dropdownOpen)}
            className="flex items-center gap-2 p-1 rounded-lg hover:bg-gray-100 dark:hover:bg-gray-700"
          >
            <div className="w-8 h-8 rounded-full bg-primary flex items-center justify-center text-white text-sm font-medium">
              {user?.full_name?.charAt(0).toUpperCase() || 'U'}
            </div>
            <svg className="w-4 h-4 text-gray-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 9l-7 7-7-7" />
            </svg>
          </button>

          {dropdownOpen && (
            <div className="absolute right-0 mt-2 w-64 bg-white dark:bg-gray-800 shadow-lg rounded-lg border border-gray-200 dark:border-gray-700 py-2">
              <div className="px-4 py-3 border-b border-gray-200 dark:border-gray-700">
                <p className="font-medium text-gray-900 dark:text-white">{user?.full_name || 'User'}</p>
                <p className="text-sm text-gray-500">{user?.email || 'email@example.com'}</p>
                <span className="inline-block mt-2 px-2 py-1 text-xs font-medium rounded bg-primary text-white">
                  {ROLE_LABELS[user?.role] || user?.role || 'User'}
                </span>
              </div>
              <Link
                to="/profile"
                className="block px-4 py-2 text-gray-700 dark:text-gray-300 hover:bg-gray-100 dark:hover:bg-gray-700"
                onClick={() => setDropdownOpen(false)}
              >
                Profile Settings
              </Link>
              <button
                onClick={() => {
                  setDropdownOpen(false)
                  logout()
                }}
                className="w-full text-left px-4 py-2 text-red-600 hover:bg-gray-100 dark:hover:bg-gray-700"
              >
                Logout
              </button>
            </div>
          )}
        </div>
      </div>
    </header>
  )
}