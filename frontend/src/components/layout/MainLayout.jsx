import { Outlet, useLocation } from 'react-router-dom'
import Sidebar from './Sidebar'
import Header from './Header'
import { useEffect, useState } from 'react'

const pageTitles = {
  '/dashboard': 'Dashboard',
  '/exams': 'Exams',
  '/exams/create': 'Create Exam',
  '/questions': 'Question Bank',
  '/questions/create': 'Create Question',
  '/results': 'Results',
  '/profile': 'My Profile',
  '/admin/users': 'User Management',
}

export default function MainLayout() {
  const location = useLocation()
  const [title, setTitle] = useState('Dashboard')

  useEffect(() => {
    const path = '/' + location.pathname.split('/').filter(Boolean).join('/')
    const match = Object.keys(pageTitles).find((key) => path === key || (key.endsWith('/') && path.startsWith(key)))
    setTitle(match ? pageTitles[match] : 'ExamSaaS')
  }, [location.pathname])

  return (
    <div className="flex h-screen bg-gray-50">
      <Sidebar />
      <div className="flex-1 flex flex-col overflow-hidden">
        <Header title={title} />
        <main className="flex-1 overflow-y-auto p-6">
          <Outlet />
        </main>
      </div>
    </div>
  )
}
