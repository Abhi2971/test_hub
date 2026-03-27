import React, { useState, useRef } from 'react';

const SearchIcon = () => (
  <svg className="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
  </svg>
);

const ChevronIcon = () => (
  <svg className="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 9l-7 7-7-7" />
  </svg>
);

const CheckIcon = () => (
  <svg className="h-4 w-4 text-blue-600" fill="none" viewBox="0 0 24 24" stroke="currentColor">
    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
  </svg>
);

const Select = ({
  label,
  error,
  options = [],
  value,
  onChange,
  placeholder = 'Select an option',
  searchable = false,
  multiSelect = false,
  className = '',
}) => {
  const [isOpen, setIsOpen] = useState(false);
  const [search, setSearch] = useState('');
  const inputRef = useRef(null);

  const filteredOptions = options.filter(opt =>
    opt.label.toLowerCase().includes(search.toLowerCase())
  );

  const getDisplayValue = () => {
    if (multiSelect && Array.isArray(value)) {
      if (value.length === 0) return placeholder;
      if (value.length === 1) {
        return options.find(o => o.value === value[0])?.label || placeholder;
      }
      return `${value.length} selected`;
    }
    if (!value) return placeholder;
    return options.find(o => o.value === value)?.label || placeholder;
  };

  const handleSelect = (optionValue) => {
    if (multiSelect) {
      const newValue = Array.isArray(value) ? value : [];
      const idx = newValue.indexOf(optionValue);
      if (idx > -1) {
        onChange(newValue.filter(v => v !== optionValue));
      } else {
        onChange([...newValue, optionValue]);
      }
    } else {
      onChange(optionValue);
      setIsOpen(false);
      setSearch('');
    }
  };

  const isSelected = (optionValue) => {
    if (multiSelect && Array.isArray(value)) {
      return value.includes(optionValue);
    }
    return value === optionValue;
  };

  return (
    <div className={`w-full ${className}`}>
      {label && (
        <label className="block text-sm font-medium text-gray-700 mb-1">
          {label}
        </label>
      )}
      <div className="relative">
        <div
          onClick={() => setIsOpen(!isOpen)}
          className={`
            w-full rounded-lg border bg-white cursor-pointer
            flex items-center justify-between
            transition-colors duration-200
            ${error 
              ? 'border-red-500 focus-within:ring-2 focus-within:ring-red-200' 
              : 'border-gray-300 focus-within:ring-2 focus-within:ring-blue-200 focus-within:border-blue-500'
            }
          `}
        >
          <span className={`flex-1 px-3 py-2 ${!value ? 'text-gray-400' : 'text-gray-900'}`}>
            {getDisplayValue()}
          </span>
          <div className="px-2 text-gray-400">
            <ChevronIcon />
          </div>
        </div>

        {isOpen && (
          <div className="absolute z-10 w-full mt-1 bg-white rounded-lg shadow-lg border border-gray-200 max-h-60 overflow-auto">
            {searchable && (
              <div className="p-2 border-b border-gray-100">
                <div className="relative">
                  <div className="absolute inset-y-0 left-0 pl-2 flex items-center pointer-events-none text-gray-400">
                    <SearchIcon />
                  </div>
                  <input
                    ref={inputRef}
                    type="text"
                    value={search}
                    onChange={(e) => setSearch(e.target.value)}
                    placeholder="Search..."
                    className="w-full pl-8 pr-3 py-1.5 text-sm border border-gray-200 rounded-md focus:outline-none focus:ring-1 focus:ring-blue-500"
                    onClick={(e) => e.stopPropagation()}
                  />
                </div>
              </div>
            )}
            <div className="py-1">
              {filteredOptions.length === 0 ? (
                <div className="px-3 py-2 text-sm text-gray-500">No options found</div>
              ) : (
                filteredOptions.map((option) => (
                  <div
                    key={option.value}
                    onClick={() => handleSelect(option.value)}
                    className={`
                      px-3 py-2 cursor-pointer flex items-center justify-between
                      hover:bg-gray-50
                      ${isSelected(option.value) ? 'bg-blue-50 text-blue-700' : 'text-gray-700'}
                    `}
                  >
                    <span>{option.label}</span>
                    {multiSelect && isSelected(option.value) && <CheckIcon />}
                  </div>
                ))
              )}
            </div>
          </div>
        )}
      </div>
      {error && (
        <p className="mt-1 text-sm text-red-600">{error}</p>
      )}
    </div>
  );
};

export default Select;