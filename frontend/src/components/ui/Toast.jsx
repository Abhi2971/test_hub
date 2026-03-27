import React from 'react';

const typeStyles = {
  success: 'border-green-500 bg-green-50',
  error: 'border-red-500 bg-red-50',
  warning: 'border-amber-500 bg-amber-50',
  info: 'border-blue-500 bg-blue-50',
};

const typeIcons = {
  success: (
    <svg className="h-5 w-5 text-green-500" fill="none" viewBox="0 0 24 24" stroke="currentColor">
      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
    </svg>
  ),
  error: (
    <svg className="h-5 w-5 text-red-500" fill="none" viewBox="0 0 24 24" stroke="currentColor">
      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
    </svg>
  ),
  warning: (
    <svg className="h-5 w-5 text-amber-500" fill="none" viewBox="0 0 24 24" stroke="currentColor">
      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />
    </svg>
  ),
  info: (
    <svg className="h-5 w-5 text-blue-500" fill="none" viewBox="0 0 24 24" stroke="currentColor">
      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
    </svg>
  ),
};

const CloseIcon = () => (
  <svg className="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
  </svg>
);

const Toast = ({ toast, onDismiss }) => {
  const { id, message, type = 'info', duration } = toast;

  return (
    <div
      className={`
        border-l-4 rounded-lg shadow-lg p-4 pr-10 relative
        ${typeStyles[type]}
      `}
      role="alert"
    >
      <div className="flex items-start gap-3">
        <div className="flex-shrink-0">
          {typeIcons[type]}
        </div>
        <p className="text-sm text-gray-700 flex-1">{message}</p>
      </div>
      <button
        onClick={() => onDismiss(id)}
        className="absolute right-2 top-2 text-gray-400 hover:text-gray-600 transition-colors"
        aria-label="Dismiss"
      >
        <CloseIcon />
      </button>
    </div>
  );
};

export default Toast;