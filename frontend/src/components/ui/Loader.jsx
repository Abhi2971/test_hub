import React from 'react';

const sizes = {
  sm: 'h-4 w-4 border-2',
  md: 'h-8 w-8 border-2',
  lg: 'h-12 w-12 border-3',
  xl: 'h-16 w-16 border-4',
};

const Loader = ({
  size = 'md',
  fullPage = false,
  text,
}) => {
  const spinner = (
    <div className={`animate-spin rounded-full border-blue-600 border-t-transparent ${sizes[size]}`} />
  );

  if (fullPage) {
    return (
      <div className="fixed inset-0 flex items-center justify-center bg-white/80 backdrop-blur-sm z-50">
        <div className="flex flex-col items-center gap-3">
          {spinner}
          {text && <span className="text-sm text-gray-600">{text}</span>}
        </div>
      </div>
    );
  }

  if (text) {
    return (
      <div className="flex flex-col items-center gap-3">
        {spinner}
        <span className="text-sm text-gray-600">{text}</span>
      </div>
    );
  }

  return spinner;
};

export default Loader;