import React, { forwardRef } from 'react';

const Input = forwardRef(({
  label,
  error,
  helpText,
  leftIcon,
  rightIcon,
  type = 'text',
  className = '',
  containerClassName = '',
  ...props
}, ref) => {
  const hasLeftIcon = !!leftIcon;
  const hasRightIcon = !!rightIcon;

  return (
    <div className={`w-full ${containerClassName}`}>
      {label && (
        <label className="block text-sm font-medium text-gray-700 mb-1">
          {label}
        </label>
      )}
      <div className="relative">
        {hasLeftIcon && (
          <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none text-gray-400">
            {leftIcon}
          </div>
        )}
        <input
          ref={ref}
          type={type}
          className={`
            w-full rounded-lg border bg-white text-gray-900
            placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-blue-200
            transition-colors duration-200
            ${hasLeftIcon ? 'pl-10' : ''}
            ${hasRightIcon ? 'pr-10' : ''}
            ${error 
              ? 'border-red-500 focus:border-red-500 ring-2 ring-red-200' 
              : 'border-gray-300 focus:border-blue-500'
            }
            ${className}
          `}
          {...props}
        />
        {hasRightIcon && (
          <div className="absolute inset-y-0 right-0 pr-3 flex items-center pointer-events-none text-gray-400">
            {rightIcon}
          </div>
        )}
      </div>
      {error && (
        <p className="mt-1 text-sm text-red-600">{error}</p>
      )}
      {helpText && !error && (
        <p className="mt-1 text-sm text-gray-500">{helpText}</p>
      )}
    </div>
  );
});

Input.displayName = 'Input';

export default Input;