import React from 'react';

const ChevronLeftIcon = () => (
  <svg className="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 19l-7-7 7-7" />
  </svg>
);

const ChevronRightIcon = () => (
  <svg className="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5l7 7-7 7" />
  </svg>
);

const Pagination = ({
  page = 1,
  totalPages = 1,
  onPageChange,
  perPage = 10,
  onPerPageChange,
  total,
}) => {
  const start = (page - 1) * perPage + 1;
  const end = Math.min(page * perPage, total || 0);

  const getPageNumbers = () => {
    const pages = [];
    const maxVisible = 5;
    let startPage = Math.max(1, page - Math.floor(maxVisible / 2));
    let endPage = Math.min(totalPages, startPage + maxVisible - 1);
    
    if (endPage - startPage + 1 < maxVisible) {
      startPage = Math.max(1, endPage - maxVisible + 1);
    }

    for (let i = startPage; i <= endPage; i++) {
      pages.push(i);
    }
    return pages;
  };

  const pageNumbers = getPageNumbers();

  return (
    <div className="flex flex-col sm:flex-row items-center justify-between gap-4">
      <div className="text-sm text-gray-600">
        Showing {total ? start : 0}-{end} of {total || 0}
      </div>
      
      <div className="flex items-center gap-2">
        <button
          onClick={() => onPageChange?.(page - 1)}
          disabled={page <= 1}
          className={`
            p-2 rounded-lg border transition-colors
            ${page <= 1 
              ? 'text-gray-300 cursor-not-allowed border-gray-200' 
              : 'text-gray-600 hover:bg-gray-50 border-gray-300'
            }
          `}
          aria-label="Previous page"
        >
          <ChevronLeftIcon />
        </button>

        {pageNumbers.map((num) => (
          <button
            key={num}
            onClick={() => onPageChange?.(num)}
            className={`
              min-w-[36px] h-9 px-3 rounded-lg text-sm font-medium transition-colors
              ${num === page 
                ? 'bg-blue-600 text-white' 
                : 'text-gray-600 hover:bg-gray-50 border border-gray-200'
              }
            `}
          >
            {num}
          </button>
        ))}

        <button
          onClick={() => onPageChange?.(page + 1)}
          disabled={page >= totalPages}
          className={`
            p-2 rounded-lg border transition-colors
            ${page >= totalPages 
              ? 'text-gray-300 cursor-not-allowed border-gray-200' 
              : 'text-gray-600 hover:bg-gray-50 border-gray-300'
            }
          `}
          aria-label="Next page"
        >
          <ChevronRightIcon />
        </button>
      </div>

      <div className="flex items-center gap-2">
        <span className="text-sm text-gray-600">Per page:</span>
        <select
          value={perPage}
          onChange={(e) => onPerPageChange?.(Number(e.target.value))}
          className="border border-gray-300 rounded-lg px-2 py-1.5 text-sm text-gray-700 focus:outline-none focus:ring-2 focus:ring-blue-200"
        >
          <option value={10}>10</option>
          <option value={20}>20</option>
          <option value={50}>50</option>
          <option value={100}>100</option>
        </select>
      </div>
    </div>
  );
};

export default Pagination;