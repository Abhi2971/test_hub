import { Outlet } from 'react-router-dom'

export default function AuthLayout() {
  return (
    <div className="min-h-screen bg-gray-50 flex items-center justify-center p-4">
      <div className="w-full max-w-md">
        <div className="text-center mb-8">
          <h1 className="text-2xl font-bold text-gray-900">ExamSaaS</h1>
          <p className="text-gray-500 mt-1">Assessment Platform</p>
        </div>
        <Outlet />
      </div>
    </div>
  )
}