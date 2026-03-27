import api from './api';

export const adminService = {
  async getUsers(params = {}) {
    try {
      const response = await api.get('/users', { params });
      return response.data;
    } catch (error) {
      throw error.response?.data || error;
    }
  },

  async getUser(id) {
    try {
      const response = await api.get(`/users/${id}`);
      return response.data;
    } catch (error) {
      throw error.response?.data || error;
    }
  },

  async toggleUserActive(id, isActive) {
    try {
      const response = await api.put(`/users/${id}/toggle-active`, { is_active: isActive });
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

  async getSubscription() {
    try {
      const response = await api.get('/subscriptions/my');
      return response.data;
    } catch (error) {
      throw error.response?.data || error;
    }
  },

  async subscribeToPlan(planId, paymentMethod) {
    try {
      const response = await api.post('/subscriptions/subscribe', {
        plan_id: planId,
        payment_method: paymentMethod,
      });
      return response.data;
    } catch (error) {
      throw error.response?.data || error;
    }
  },

  async cancelSubscription() {
    try {
      const response = await api.post('/subscriptions/cancel');
      return response.data;
    } catch (error) {
      throw error.response?.data || error;
    }
  },

  async checkFeature(feature) {
    try {
      const response = await api.get('/subscriptions/check-feature', { params: { feature } });
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

  async getPlan(id) {
    try {
      const response = await api.get(`/plans/${id}`);
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
};
