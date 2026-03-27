export const validateEmail = (email) => {
  if (!email) {
    return { valid: false, error: 'Email is required' };
  }
  
  const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
  
  if (!emailRegex.test(email)) {
    return { valid: false, error: 'Please enter a valid email address' };
  }
  
  return { valid: true };
};

export const validatePassword = (password) => {
  const errors = [];
  
  if (!password) {
    errors.push('Password is required');
    return { valid: false, errors };
  }
  
  if (password.length < 8) {
    errors.push('Password must be at least 8 characters long');
  }
  
  if (!/[A-Z]/.test(password)) {
    errors.push('Password must contain at least one uppercase letter');
  }
  
  if (!/[a-z]/.test(password)) {
    errors.push('Password must contain at least one lowercase letter');
  }
  
  if (!/[0-9]/.test(password)) {
    errors.push('Password must contain at least one digit');
  }
  
  return {
    valid: errors.length === 0,
    errors,
  };
};

export const validatePhone = (phone) => {
  if (!phone) {
    return { valid: false, error: 'Phone number is required' };
  }
  
  const cleaned = phone.replace(/\D/g, '');
  
  if (cleaned.length !== 10) {
    return { valid: false, error: 'Please enter a valid 10-digit phone number' };
  }
  
  return { valid: true };
};

export const passwordStrength = (password) => {
  if (!password) return 'weak';
  
  let score = 0;
  
  if (password.length >= 8) score++;
  if (password.length >= 12) score++;
  if (/[A-Z]/.test(password)) score++;
  if (/[a-z]/.test(password)) score++;
  if (/[0-9]/.test(password)) score++;
  if (/[^A-Za-z0-9]/.test(password)) score++;
  
  if (score >= 5) return 'strong';
  if (score >= 3) return 'medium';
  return 'weak';
};
