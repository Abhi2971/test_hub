import { useState } from 'react'

export default function useCloudinaryUpload() {
  const [isUploading, setIsUploading] = useState(false)
  const [error, setError] = useState(null)

  const upload = async (file) => {
    setIsUploading(true)
    setError(null)

    try {
      const cloudName = import.meta.env.VITE_CLOUDINARY_CLOUD_NAME
      const uploadPreset = import.meta.env.VITE_CLOUDINARY_UPLOAD_PRESET

      if (!cloudName || !uploadPreset) {
        throw new Error('Cloudinary configuration missing')
      }

      const formData = new FormData()
      formData.append('file', file)
      formData.append('upload_preset', uploadPreset)

      const response = await fetch(
        `https://api.cloudinary.com/v1_1/${cloudName}/image/upload`,
        {
          method: 'POST',
          body: formData,
        }
      )

      if (!response.ok) {
        throw new Error('Upload failed')
      }

      const data = await response.json()
      return { url: data.secure_url, public_id: data.public_id }
    } catch (err) {
      setError(err.message)
      throw err
    } finally {
      setIsUploading(false)
    }
  }

  return { upload, isUploading, error }
}
