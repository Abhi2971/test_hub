import React from 'react';

const variants = {
  primary: 'bg-blue-600 text-white hover:bg-blue-700',
  secondary: 'bg-white border border-gray-300 text-gray-700 hover:bg-gray-50',
  danger: 'bg-red-600 text-white hover:bg-red-700',
  ghost: 'bg-transparent text-gray-600 hover:bg-gray-100',
  success: 'bg-green-600 text-white hover:bg-green-700',
  warning: 'bg-amber-100 text-amber-700 border border-amber-300 hover:bg-amber-200',
};

const sizes = {
  sm: 'px-3 py-1.5 text-sm',
  md: 'px-4 py-2 text-sm',
  lg: 'px-6 py-2.5 text-base',
};

const Spinner = () => (
  <svg className="animate-spin h-4 w-4" viewBox="0 0 24 24">
    <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" fill="none" />
    <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z" />
  </svg>
);

const Button = React.forwardRef(({
  variant = 'primary',
  size = 'md',
  loading = false,
  disabled = false,
  leftIcon,
  rightIcon,
  onClick,
  type = 'button',
  className = '',
  children,
}, ref) => {
  const isDisabled = disabled || loading;

  return (
    <button
      ref={ref}
      type={type}
      onClick={onClick}
      disabled={isDisabled}
      className={`
        inline-flex items-center justify-center font-medium rounded-lg
        transition-colors duration-200 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500
        ${variants[variant]}
        ${sizes[size]}
        ${isDisabled ? 'opacity-60 cursor-not-allowed' : ''}
        ${className}
      `}
    >
      {loading && (
        <span className="mr-2">
          <Spinner />
        </span>
      )}
      {leftIcon && !loading && (
        <span className="mr-2">{leftIcon}</span>
      )}
      {children}
      {rightIcon && (
        <span className="ml-2">{rightIcon}</span>
      )}
    </button>
  );
});

Button.displayName = 'Button';

export default Button;