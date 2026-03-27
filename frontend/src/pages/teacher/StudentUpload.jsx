import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { useAuth } from '../../contexts/AuthContext'
import { useToast } from '../../contexts/ToastContext'
import api from '../../services/api'
import Button from '../../components/ui/Button'
import Card from '../../components/ui/Card'
import Loader from '../../components/ui/Loader'
import { Upload, Download, Check, X, AlertCircle } from 'lucide-react'

export default function StudentUpload() {
  const navigate = useNavigate()
  const { user } = useAuth()
  const { showToast } = useToast()
  const [file, setFile] = useState(null)
  const [preview, setPreview] = useState([])
  const [errors, setErrors] = useState([])
  const [loading, setLoading] = useState(false)
  const [uploading, setUploading] = useState(false)

  if (user?.role !== 'teacher') {
    navigate('/dashboard')
    return null
  }

  const handleDownloadTemplate = async () => {
    try {
      const response = await api.get('/students/template', { responseType: 'blob' })
      const url = window.URL.createObjectURL(new Blob([response.data]))
      const link = document.createElement('a')
      link.href = url
      link.setAttribute('download', 'student_template.xlsx')
      document.body.appendChild(link)
      link.click()
      link.remove()
      showToast('Template downloaded', 'success')
    } catch (error) {
      showToast('Failed to download template', 'error')
    }
  }

  const handleFileChange = (e) => {
    const selectedFile = e.target.files?.[0]
    if (selectedFile) {
      if (!selectedFile.name.match(/\.(xlsx|xls)$/)) {
        showToast('Please upload an Excel file', 'error')
        return
      }
      setFile(selectedFile)
      simulateParse(selectedFile)
    }
  }

  const simulateParse = async (file) => {
    setLoading(true)
    setPreview([])
    setErrors([])
    await new Promise(resolve => setTimeout(resolve, 1000))

    const mockData = [
      { name: 'John Doe', email: 'john@example.com', batch: '2024', section: 'A', year: '3rd', valid: true },
      { name: 'Jane Smith', email: 'jane@example.com', batch: '2024', section: 'A', year: '3rd', valid: true },
      { name: '', email: 'invalid@example.com', batch: '2024', section: 'A', year: '3rd', valid: false, error: 'Name is required' },
      { name: 'Bob Wilson', email: 'bob@example.com', batch: '2024', section: 'B', year: '3rd', valid: true },
      { name: 'Alice Brown', email: 'alice@example.com', batch: '2024', section: 'B', year: '3rd', valid: true },
    ]

    setPreview(mockData)
    setErrors(mockData.filter(r => !r.valid))
    setLoading(false)
  }

  const handleUpload = async () => {
    const validRows = preview.filter(r => r.valid)
    if (validRows.length === 0) {
      showToast('No valid rows to upload', 'error')
      return
    }

    setUploading(true)
    try {
      const formData = new FormData()
      formData.append('file', file)
      await api.post('/students/bulk-upload', formData, {
        headers: { 'Content-Type': 'multipart/form-data' }
      })
      showToast(`${validRows.length} students uploaded successfully`, 'success')
      setFile(null)
      setPreview([])
      setErrors([])
    } catch (error) {
      showToast(error.response?.data?.message || 'Failed to upload', 'error')
    } finally {
      setUploading(false)
    }
  }

  const validCount = preview.filter(r => r.valid).length
  const invalidCount = preview.filter(r => !r.valid).length

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">Upload Students</h1>
          <p className="text-gray-500 mt-1">Bulk upload students via Excel</p>
        </div>
        <Button variant="secondary" leftIcon={<Download size={18} />} onClick={handleDownloadTemplate}>
          Download Template
        </Button>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        <div className="lg:col-span-2">
          <Card>
            <div className="p-6">
              <div className={`border-2 border-dashed rounded-xl p-8 text-center transition-colors ${
                file ? 'border-blue-400 bg-blue-50' : 'border-gray-300 hover:border-blue-400'
              }`}>
                <input
                  type="file"
                  accept=".xlsx,.xls"
                  onChange={handleFileChange}
                  className="hidden"
                  id="student-file"
                />
                <label htmlFor="student-file" className="cursor-pointer">
                  <Upload className="mx-auto text-gray-400 mb-2" size={32} />
                  <p className="text-gray-700 font-medium">
                    {file ? file.name : 'Click to upload Excel file'}
                  </p>
                  <p className="text-sm text-gray-400 mt-1">.xlsx or .xls files only</p>
                </label>
              </div>

              {loading && (
                <div className="mt-6 text-center">
                  <Loader text="Parsing file..." />
                </div>
              )}

              {preview.length > 0 && !loading && (
                <div className="mt-6">
                  <div className="flex items-center justify-between mb-4">
                    <h3 className="font-semibold text-gray-900">Preview</h3>
                    <div className="flex items-center gap-4 text-sm">
                      <span className="flex items-center gap-1 text-green-600">
                        <Check size={14} /> {validCount} valid
                      </span>
                      {invalidCount > 0 && (
                        <span className="flex items-center gap-1 text-red-600">
                          <X size={14} /> {invalidCount} invalid
                        </span>
                      )}
                    </div>
                  </div>

                  <div className="overflow-x-auto border border-gray-200 rounded-lg">
                    <table className="w-full text-sm">
                      <thead className="bg-gray-50 border-b border-gray-200">
                        <tr>
                          <th className="px-4 py-2 text-left text-xs font-medium text-gray-500">Name</th>
                          <th className="px-4 py-2 text-left text-xs font-medium text-gray-500">Email</th>
                          <th className="px-4 py-2 text-left text-xs font-medium text-gray-500">Batch</th>
                          <th className="px-4 py-2 text-left text-xs font-medium text-gray-500">Section</th>
                          <th className="px-4 py-2 text-left text-xs font-medium text-gray-500">Year</th>
                          <th className="px-4 py-2 text-left text-xs font-medium text-gray-500">Status</th>
                        </tr>
                      </thead>
                      <tbody className="divide-y divide-gray-100">
                        {preview.map((row, idx) => (
                          <tr key={idx} className={!row.valid ? 'bg-red-50' : ''}>
                            <td className="px-4 py-2">{row.name || '-'}</td>
                            <td className="px-4 py-2">{row.email || '-'}</td>
                            <td className="px-4 py-2">{row.batch || '-'}</td>
                            <td className="px-4 py-2">{row.section || '-'}</td>
                            <td className="px-4 py-2">{row.year || '-'}</td>
                            <td className="px-4 py-2">
                              {row.valid ? (
                                <span className="flex items-center gap-1 text-green-600">
                                  <Check size={14} /> Valid
                                </span>
                              ) : (
                                <span className="flex items-center gap-1 text-red-600">
                                  <AlertCircle size={14} /> {row.error}
                                </span>
                              )}
                            </td>
                          </tr>
                        ))}
                      </tbody>
                    </table>
                  </div>

                  <div className="flex justify-end gap-3 mt-6">
                    <Button
                      variant="secondary"
                      onClick={() => { setFile(null); setPreview([]); setErrors([]) }}
                    >
                      Cancel
                    </Button>
                    <Button
                      onClick={handleUpload}
                      loading={uploading}
                      disabled={validCount === 0}
                    >
                      Upload {validCount} Students
                    </Button>
                  </div>
                </div>
              )}
            </div>
          </Card>
        </div>

        <div>
          <Card header="Instructions">
            <div className="p-4 space-y-4 text-sm text-gray-600">
              <div>
                <h4 className="font-medium text-gray-900 mb-1">1. Download Template</h4>
                <p>Get the Excel template with the required columns.</p>
              </div>
              <div>
                <h4 className="font-medium text-gray-900 mb-1">2. Fill Data</h4>
                <p>Enter student details in the template. Required: Name, Email.</p>
              </div>
              <div>
                <h4 className="font-medium text-gray-900 mb-1">3. Upload</h4>
                <p>Upload the filled Excel file. Invalid rows will be highlighted.</p>
              </div>
              <div>
                <h4 className="font-medium text-gray-900 mb-1">4. Review</h4>
                <p>Preview the data and confirm to upload.</p>
              </div>
            </div>
          </Card>

          <Card header="Format" className="mt-4">
            <div className="p-4">
              <table className="w-full text-sm">
                <tbody className="divide-y divide-gray-100">
                  <tr>
                    <td className="py-1 text-gray-600">Name</td>
                    <td className="py-1 text-red-500">* Required</td>
                  </tr>
                  <tr>
                    <td className="py-1 text-gray-600">Email</td>
                    <td className="py-1 text-red-500">* Required</td>
                  </tr>
                  <tr>
                    <td className="py-1 text-gray-600">Batch</td>
                    <td className="py-1 text-gray-400">Optional</td>
                  </tr>
                  <tr>
                    <td className="py-1 text-gray-600">Section</td>
                    <td className="py-1 text-gray-400">Optional</td>
                  </tr>
                  <tr>
                    <td className="py-1 text-gray-600">Year</td>
                    <td className="py-1 text-gray-400">Optional</td>
                  </tr>
                </tbody>
              </table>
            </div>
          </Card>
        </div>
      </div>
    </div>
  )
}