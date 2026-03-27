import api from './api';

export const authService = {
  async login(email, password) {
    try {
      const response = await api.post('/auth/login', { email, password });
      return response.data;
    } catch (error) {
      throw error.response?.data || error;
    }
  },

  async register(data) {
    try {
      const response = await api.post('/auth/register', data);
      return response.data;
    } catch (error) {
      throw error.response?.data || error;
    }
  },

  async verifyEmail(email, otp) {
    try {
      const response = await api.post('/auth/verify-email', { email, otp });
      return response.data;
    } catch (error) {
      throw error.response?.data || error;
    }
  },

  async googleLogin(idToken) {
    try {
      const response = await api.post('/auth/google', { id_token: idToken });
      return response.data;
    } catch (error) {
      throw error.response?.data || error;
    }
  },

  async logout() {
    try {
      const response = await api.post('/auth/logout');
      return response.data;
    } catch (error) {
      throw error.response?.data || error;
    }
  },

  async refreshToken() {
    try {
      const response = await api.post('/auth/refresh');
      return response.data;
    } catch (error) {
      throw error.response?.data || error;
    }
  },

  async forgotPassword(email) {
    try {
      const response = await api.post('/auth/forgot-password', { email });
      return response.data;
    } catch (error) {
      throw error.response?.data || error;
    }
  },

  async resetPassword(email, otp, newPassword) {
    try {
      const response = await api.post('/auth/reset-password', { email, otp, new_password: newPassword });
      return response.data;
    } catch (error) {
      throw error.response?.data || error;
    }
  },

  async getMe() {
    try {
      const response = await api.get('/auth/me');
      return response.data;
    } catch (error) {
      throw error.response?.data || error;
    }
  },

  async updateMe(data) {
    try {
      const response = await api.patch('/auth/me', data);
      return response.data;
    } catch (error) {
      throw error.response?.data || error;
    }
  },

  async verifyMagicLink(token) {
    try {
      const response = await api.post('/auth/magic-link/verify', { token });
      return response.data;
    } catch (error) {
      throw error.response?.data || error;
    }
  },

  async resendOTP(email, purpose) {
    try {
      const response = await api.post('/auth/resend-otp', { email, purpose });
      return response.data;
    } catch (error) {
      throw error.response?.data || error;
    }
  },
};
