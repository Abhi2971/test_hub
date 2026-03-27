export const formatCurrency = (paise) => {
  if (paise == null || isNaN(paise)) return '₹0.00';
  const rupees = paise / 100;
  return `₹${rupees.toLocaleString('en-IN', { minimumFractionDigits: 2, maximumFractionDigits: 2 })}`;
};

export const formatDate = (dateStr, format) => {
  if (!dateStr) return '';
  const date = new Date(dateStr);
  if (isNaN(date.getTime())) return '';

  if (format) {
    const options = {};
    if (format.includes('YYYY')) options.year = 'numeric';
    if (format.includes('MM')) options.month = '2-digit';
    if (format.includes('DD')) options.day = '2-digit';
    if (format.includes('HH')) options.hour = '2-digit';
    if (format.includes('mm')) options.minute = '2-digit';
    
    let formatted = format;
    const parts = date.toLocaleDateString('en-IN', { year: 'numeric', month: '2-digit', day: '2-digit' }).split('/');
    formatted = formatted.replace('YYYY', parts[2]);
    formatted = formatted.replace('MM', parts[1]);
    formatted = formatted.replace('DD', parts[0]);
    return formatted;
  }

  return date.toLocaleDateString('en-IN', { month: 'short', day: 'numeric', year: 'numeric' });
};

export const formatDateTime = (dateStr) => {
  if (!dateStr) return '';
  const date = new Date(dateStr);
  if (isNaN(date.getTime())) return '';

  const formattedDate = date.toLocaleDateString('en-IN', { month: 'short', day: 'numeric', year: 'numeric' });
  const formattedTime = date.toLocaleTimeString('en-IN', { hour: 'numeric', minute: '2-digit', hour12: true });
  
  return `${formattedDate} at ${formattedTime}`;
};

export const formatRelative = (dateStr) => {
  if (!dateStr) return '';
  const date = new Date(dateStr);
  if (isNaN(date.getTime())) return '';

  const now = new Date();
  const diffMs = now - date;
  const diffSec = Math.floor(diffMs / 1000);
  const diffMin = Math.floor(diffSec / 60);
  const diffHour = Math.floor(diffMin / 60);
  const diffDay = Math.floor(diffHour / 24);
  const diffWeek = Math.floor(diffDay / 7);
  const diffMonth = Math.floor(diffDay / 30);

  if (diffSec < 60) return 'just now';
  if (diffMin < 60) return `${diffMin} minute${diffMin > 1 ? 's' : ''} ago`;
  if (diffHour < 24) return `${diffHour} hour${diffHour > 1 ? 's' : ''} ago`;
  if (diffDay < 7) return `${diffDay} day${diffDay > 1 ? 's' : ''} ago`;
  if (diffWeek < 4) return `${diffWeek} week${diffWeek > 1 ? 's' : ''} ago`;
  if (diffMonth < 12) return `${diffMonth} month${diffMonth > 1 ? 's' : ''} ago`;
  
  return formatDate(dateStr);
};

export const formatPercentage = (value) => {
  if (value == null || isNaN(value)) return '0%';
  return `${Number(value).toFixed(1)}%`;
};

export const formatDuration = (minutes) => {
  if (minutes == null || isNaN(minutes)) return '0m';
  
  const hours = Math.floor(minutes / 60);
  const mins = minutes % 60;
  
  if (hours > 0) {
    return `${hours}h ${mins}m`;
  }
  return `${mins}m`;
};

export const formatGrade = (grade) => {
  const gradeMap = {
    'A+': 'Excellent',
    'A': 'Outstanding',
    'A-': 'Excellent',
    'B+': 'Very Good',
    'B': 'Good',
    'B-': 'Good',
    'C+': 'Above Average',
    'C': 'Average',
    'C-': 'Average',
    'D': 'Below Average',
    'F': 'Failed',
  };
  return gradeMap[grade?.toUpperCase()] || grade;
};

export const formatPhone = (phone) => {
  if (!phone) return '';
  const cleaned = phone.replace(/\D/g, '');
  if (cleaned.length === 10) {
    return `+91 ${cleaned.slice(0, 5)} ${cleaned.slice(5)}`;
  }
  if (cleaned.length === 12 && cleaned.startsWith('91')) {
    const num = cleaned.slice(2);
    return `+91 ${num.slice(0, 5)} ${num.slice(5)}`;
  }
  return phone;
};

export const paiseToRupees = (paise) => {
  if (paise == null || isNaN(paise)) return 0;
  return paise / 100;
};

export const rupeesToPaise = (rupees) => {
  if (rupees == null || isNaN(rupees)) return 0;
  return Math.round(rupees * 100);
};
