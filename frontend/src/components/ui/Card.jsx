import React from 'react';

const Card = ({
  children,
  className = '',
  header,
  footer,
  loading = false,
  onClick,
}) => {
  const isClickable = !!onClick;

  return (
    <div
      onClick={onClick}
      className={`
        bg-white rounded-xl border border-gray-200 shadow-sm
        ${isClickable ? 'cursor-pointer hover:shadow-md transition-shadow duration-200' : ''}
        ${className}
      `}
    >
      {loading && (
        <div className="absolute inset-0 bg-white/80 backdrop-blur-sm z-10 rounded-xl flex items-center justify-center">
          <div className="flex flex-col items-center gap-2">
            <div className="h-2 w-32 bg-gray-200 rounded animate-pulse" />
            <div className="h-2 w-24 bg-gray-200 rounded animate-pulse" />
            <div className="h-2 w-28 bg-gray-200 rounded animate-pulse" />
          </div>
        </div>
      )}
      {header && (
        <div className="px-6 py-4 border-b border-gray-200">
          {typeof header === 'string' ? (
            <h3 className="text-lg font-semibold text-gray-900">{header}</h3>
          ) : (
            header
          )}
        </div>
      )}
      <div className={loading ? 'opacity-50' : ''}>
        {children}
      </div>
      {footer && (
        <div className="px-6 py-4 border-t border-gray-200 bg-gray-50 rounded-b-xl">
          {typeof footer === 'string' ? (
            <p className="text-sm text-gray-600">{footer}</p>
          ) : (
            footer
          )}
        </div>
      )}
    </div>
  );
};

export default Card;