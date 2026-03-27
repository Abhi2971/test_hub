import React from 'react';
import Button from './Button';

const EmptyState = ({
  icon: Icon,
  title,
  message,
  actionLabel,
  onAction,
}) => {
  return (
    <div className="flex flex-col items-center justify-center py-12 px-6 bg-gray-50 rounded-xl">
      {Icon && (
        <div className="text-gray-300 mb-4">
          <Icon className="w-12 h-12" />
        </div>
      )}
      {title && (
        <h3 className="text-lg font-semibold text-gray-900 mb-2">
          {title}
        </h3>
      )}
      {message && (
        <p className="text-sm text-gray-500 text-center max-w-sm mb-6">
          {message}
        </p>
      )}
      {actionLabel && onAction && (
        <Button onClick={onAction}>
          {actionLabel}
        </Button>
      )}
    </div>
  );
};

export default EmptyState;