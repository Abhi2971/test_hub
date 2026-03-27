import React, { useState, useRef } from 'react';

const UploadIcon = () => (
  <svg className="h-8 w-8 text-gray-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M7 16a4 4 0 01-.88-7.903A5 5 0 1115.9 6L16 6a5 5 0 011 9.9M15 10l4-4m0 0l-4-4m4 4V-4" />
  </svg>
);

const FileIcon = () => (
  <svg className="h-5 w-5 text-gray-500" fill="none" viewBox="0 0 24 24" stroke="currentColor">
    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
  </svg>
);

const CloseIcon = () => (
  <svg className="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
  </svg>
);

const FileUpload = ({
  label,
  accept,
  maxSize = 5,
  onUpload,
  error,
  multiple = false,
  className = '',
}) => {
  const [files, setFiles] = useState([]);
  const [uploading, setUploading] = useState(false);
  const [progress, setProgress] = useState(0);
  const [dragActive, setDragActive] = useState(false);
  const inputRef = useRef(null);

  const validateFile = (file) => {
    if (accept && !accept.split(',').some(type => {
      const trimmed = type.trim();
      if (trimmed.startsWith('.')) {
        return file.name.toLowerCase().endsWith(trimmed);
      }
      const mimeType = file.type.toLowerCase();
      return mimeType === trimmed.toLowerCase() || mimeType === `${trimmed.toLowerCase()}/*`;
    })) {
      return `File type not accepted`;
    }
    if (maxSize && file.size > maxSize * 1024 * 1024) {
      return `File size exceeds ${maxSize}MB limit`;
    }
    return null;
  };

  const handleFiles = async (selectedFiles) => {
    const fileList = Array.from(selectedFiles);
    const validFiles = [];
    let validationError = null;

    for (const file of fileList) {
      const err = validateFile(file);
      if (err) {
        validationError = err;
        break;
      }
      validFiles.push(file);
    }

    if (validationError) {
      return;
    }

    if (multiple) {
      setFiles(prev => [...prev, ...validFiles]);
    } else {
      setFiles(validFiles);
    }

    if (onUpload && validFiles.length > 0) {
      setUploading(true);
      setProgress(0);
      
      try {
        const result = await onUpload(multiple ? (multiple ? validFiles : validFiles[0]) : validFiles[0]);
        setProgress(100);
      } catch (err) {
        setFiles([]);
      } finally {
        setUploading(false);
      }
    }
  };

  const handleDrop = (e) => {
    e.preventDefault();
    setDragActive(false);
    if (e.dataTransfer.files?.length) {
      handleFiles(e.dataTransfer.files);
    }
  };

  const handleDragOver = (e) => {
    e.preventDefault();
    setDragActive(true);
  };

  const handleDragLeave = () => {
    setDragActive(false);
  };

  const removeFile = (index) => {
    setFiles(prev => prev.filter((_, i) => i !== index));
  };

  return (
    <div className={`w-full ${className}`}>
      {label && (
        <label className="block text-sm font-medium text-gray-700 mb-2">
          {label}
        </label>
      )}
      
      <div
        onClick={() => inputRef.current?.click()}
        onDrop={handleDrop}
        onDragOver={handleDragOver}
        onDragLeave={handleDragLeave}
        className={`
          relative border-2 border-dashed rounded-lg p-6
          flex flex-col items-center justify-center cursor-pointer
          transition-colors duration-200
          ${dragActive ? 'border-blue-400 bg-blue-50' : 'border-gray-300 hover:border-gray-400'}
          ${error ? 'border-red-500 bg-red-50' : ''}
        `}
      >
        <input
          ref={inputRef}
          type="file"
          accept={accept}
          multiple={multiple}
          onChange={(e) => e.target.files && handleFiles(e.target.files)}
          className="hidden"
        />
        
        <UploadIcon />
        <p className="mt-2 text-sm text-gray-600">
          Drag and drop or <span className="text-blue-600 font-medium">browse</span>
        </p>
        {maxSize && (
          <p className="mt-1 text-xs text-gray-400">
            Maximum file size: {maxSize}MB
          </p>
        )}
      </div>

      {uploading && (
        <div className="mt-3">
          <div className="h-2 bg-gray-200 rounded-full overflow-hidden">
            <div 
              className="h-full bg-blue-600 transition-all duration-300"
              style={{ width: `${progress}%` }}
            />
          </div>
          <p className="mt-1 text-xs text-gray-500">Uploading...</p>
        </div>
      )}

      {files.length > 0 && (
        <div className="mt-3 space-y-2">
          {files.map((file, index) => (
            <div 
              key={index}
              className="flex items-center justify-between p-2 bg-gray-50 rounded-lg border border-gray-200"
            >
              <div className="flex items-center gap-2 min-w-0">
                <FileIcon />
                <span className="text-sm text-gray-700 truncate">{file.name}</span>
                <span className="text-xs text-gray-400">
                  ({(file.size / 1024).toFixed(1)} KB)
                </span>
              </div>
              <button
                onClick={(e) => {
                  e.stopPropagation();
                  removeFile(index);
                }}
                className="text-gray-400 hover:text-gray-600 p-1"
              >
                <CloseIcon />
              </button>
            </div>
          ))}
        </div>
      )}

      {error && (
        <p className="mt-2 text-sm text-red-600">{error}</p>
      )}
    </div>
  );
};

export default FileUpload;