import React from 'react';
import Modal from './Modal';
import Button from './Button';

const WarningIcon = () => (
  <svg className="h-6 w-6 text-red-600" fill="none" viewBox="0 0 24 24" stroke="currentColor">
    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />
  </svg>
);

const ConfirmDialog = ({
  isOpen,
  onConfirm,
  onCancel,
  title = 'Confirm Action',
  message,
  confirmLabel = 'Confirm',
  confirmVariant = 'danger',
  isLoading = false,
}) => {
  return (
    <Modal
      isOpen={isOpen}
      onClose={onCancel}
      title={title}
      size="sm"
      footer={
        <div className="flex justify-end gap-3">
          <Button
            variant="secondary"
            onClick={onCancel}
            disabled={isLoading}
          >
            Cancel
          </Button>
          <Button
            variant={confirmVariant}
            onClick={onConfirm}
            loading={isLoading}
          >
            {confirmLabel}
          </Button>
        </div>
      }
    >
      <div className="flex items-start gap-4">
        <div className="flex-shrink-0">
          <WarningIcon />
        </div>
        <p className="text-sm text-gray-600">
          {message}
        </p>
      </div>
    </Modal>
  );
};

export default ConfirmDialog;