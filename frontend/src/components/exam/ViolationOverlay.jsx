import React from 'react';
import { AlertTriangle, Maximize2, Copy } from 'lucide-react';

function ViolationOverlay({ type, count, limit, onDismiss, onFullscreenReturn }) {
  const isFinalWarning = count >= limit;

  const getIcon = () => {
    switch (type) {
      case 'tab_switch':
        return <AlertTriangle className="w-16 h-16 text-red-500 mx-auto mb-4" />;
      case 'fullscreen_exit':
        return <Maximize2 className="w-16 h-16 text-red-500 mx-auto mb-4" />;
      case 'copy_paste':
        return <Copy className="w-16 h-16 text-red-500 mx-auto mb-4" />;
      default:
        return null;
    }
  };

  const getTitle = () => {
    switch (type) {
      case 'tab_switch':
        return 'Warning: You Left the Exam Window';
      case 'fullscreen_exit':
        return 'Fullscreen Mode Required';
      case 'copy_paste':
        return 'Copy/Paste Disabled';
      default:
        return '';
    }
  };

  const getMessage = () => {
    switch (type) {
      case 'tab_switch':
        return 'You switched away from the exam. This is counted as a violation.';
      case 'fullscreen_exit':
        return 'Please return to fullscreen mode to continue your exam.';
      case 'copy_paste':
        return 'Copy and paste are not allowed during the exam.';
      default:
        return '';
    }
  };

  const getButtonText = () => {
    switch (type) {
      case 'tab_switch':
        return 'Return to Exam';
      case 'fullscreen_exit':
        return 'Return to Fullscreen';
      case 'copy_paste':
        return 'I Understand';
      default:
        return '';
    }
  };

  const getButtonHandler = () => {
    if (type === 'fullscreen_exit' && onFullscreenReturn) {
      return onFullscreenReturn;
    }
    return onDismiss;
  };

  const cardClassName = isFinalWarning 
    ? 'bg-white rounded-xl shadow-2xl p-8 max-w-md mx-auto mt-40 text-center z-50 border-4 border-red-500 bg-red-50' 
    : 'bg-white rounded-xl shadow-2xl p-8 max-w-md mx-auto mt-40 text-center z-50';

  return (
    <div className="fixed inset-0 bg-black/60 z-40 flex items-start justify-center pt-40">
      <div className={cardClassName}>
        {getIcon()}
        <h2 className="text-2xl font-bold text-red-600 mb-4">{getTitle()}</h2>
        <p className="text-gray-700 mb-4">{getMessage()}</p>
        
        {type === 'tab_switch' && (
          <div className="mb-6">
            <p className="text-gray-700 mb-2">Remaining warnings: {limit - count}</p>
            {isFinalWarning && (
              <p className="text-red-600 font-semibold">FINAL WARNING: Next violation will auto-submit your exam.</p>
            )}
          </div>
        )}

        <button
          onClick={getButtonHandler()}
          className="w-full py-3 px-6 rounded-lg font-semibold bg-blue-600 text-white hover:bg-blue-700 transition-colors"
        >
          {getButtonText()}
        </button>
      </div>
    </div>
  );
}

export default ViolationOverlay;