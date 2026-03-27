import api from './api';

export const superadminService = {
  async getPlatformAnalytics() {
    try {
      const response = await api.get('/superadmin/analytics/platform');
      return response.data;
    } catch (error) {
      throw error.response?.data || error;
    }
  },

  async getAuditLogs(params = {}) {
    try {
      const response = await api.get('/superadmin/audit-logs', { params });
      return response.data;
    } catch (error) {
      throw error.response?.data || error;
    }
  },

  async getInstitutes(params = {}) {
    try {
      const response = await api.get('/institutes', { params });
      return response.data;
    } catch (error) {
      throw error.response?.data || error;
    }
  },

  async getInstitute(id) {
    try {
      const response = await api.get(`/institutes/${id}`);
      return response.data;
    } catch (error) {
      throw error.response?.data || error;
    }
  },

  async createInstitute(data) {
    try {
      const response = await api.post('/institutes/create-with-admin', data);
      return response.data;
    } catch (error) {
      const errorData = error.response?.data;
      if (errorData?.message) {
        const err = new Error(errorData.message);
        err.data = errorData;
        throw err;
      }
      throw error;
    }
  },

  async updateInstitute(id, data) {
    try {
      const response = await api.patch(`/institutes/${id}`, data);
      return response.data;
    } catch (error) {
      throw error.response?.data || error;
    }
  },

  async suspendInstitute(id) {
    try {
      const response = await api.post(`/institutes/${id}/suspend`);
      return response.data;
    } catch (error) {
      throw error.response?.data || error;
    }
  },

  async restoreInstitute(id) {
    try {
      const response = await api.post(`/institutes/${id}/restore`);
      return response.data;
    } catch (error) {
      throw error.response?.data || error;
    }
  },

  async impersonateInstitute(id) {
    try {
      const response = await api.post(`/institutes/${id}/impersonate`);
      return response.data;
    } catch (error) {
      throw error.response?.data || error;
    }
  },

  async getUsers(params = {}) {
    try {
      const response = await api.get('/users', { params });
      return response.data;
    } catch (error) {
      throw error.response?.data || error;
    }
  },

  async getPlans(params = {}) {
    try {
      const response = await api.get('/plans', { params });
      return response.data;
    } catch (error) {
      throw error.response?.data || error;
    }
  },

  async createPlan(data) {
    try {
      const response = await api.post('/plans', data);
      return response.data;
    } catch (error) {
      throw error.response?.data || error;
    }
  },

  async updatePlan(id, data) {
    try {
      const response = await api.patch(`/plans/${id}`, data);
      return response.data;
    } catch (error) {
      throw error.response?.data || error;
    }
  },

  async deletePlan(id) {
    try {
      const response = await api.delete(`/plans/${id}`);
      return response.data;
    } catch (error) {
      throw error.response?.data || error;
    }
  },

  async getPayments(params = {}) {
    try {
      const response = await api.get('/payments', { params });
      return response.data;
    } catch (error) {
      throw error.response?.data || error;
    }
  },

  async getPayment(id) {
    try {
      const response = await api.get(`/payments/${id}`);
      return response.data;
    } catch (error) {
      throw error.response?.data || error;
    }
  },

  async getSubscriptions(params = {}) {
    try {
      const response = await api.get('/superadmin/subscriptions', { params });
      return response.data;
    } catch (error) {
      throw error.response?.data || error;
    }
  },

  async getExams(params = {}) {
    try {
      const response = await api.get('/superadmin/exams', { params });
      return response.data;
    } catch (error) {
      throw error.response?.data || error;
    }
  },

  async getExamAnalytics(examId) {
    try {
      const response = await api.get(`/exam/${examId}/analytics`);
      return response.data;
    } catch (error) {
      throw error.response?.data || error;
    }
  },
};
