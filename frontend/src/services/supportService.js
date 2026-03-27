import api from './api';

export const supportService = {
  async getTickets(params = {}) {
    try {
      const response = await api.get('/support/tickets', { params: { ...params, per_page: params.per_page || 20 } });
      return response.data.data;
    } catch (error) {
      throw error.response?.data || error;
    }
  },

  async getTicket(id) {
    try {
      const response = await api.get(`/support/tickets/${id}`);
      return response.data.data;
    } catch (error) {
      throw error.response?.data || error;
    }
  },

  async createTicket(data) {
    try {
      const response = await api.post('/support/tickets', data);
      return response.data.data;
    } catch (error) {
      throw error.response?.data || error;
    }
  },

  async replyTicket(id, message, attachments) {
    try {
      const formData = new FormData();
      formData.append('message', message);
      if (attachments && attachments.length > 0) {
        attachments.forEach((file) => {
          formData.append('attachments', file);
        });
      }
      const response = await api.post(`/support/tickets/${id}/messages`, formData, {
        headers: { 'Content-Type': 'multipart/form-data' },
      });
      return response.data.data;
    } catch (error) {
      throw error.response?.data || error;
    }
  },

  async closeTicket(id) {
    try {
      const response = await api.post(`/support/tickets/${id}/close`);
      return response.data.data;
    } catch (error) {
      throw error.response?.data || error;
    }
  },

  async updateTicketStatus(id, data) {
    try {
      const response = await api.patch(`/support/tickets/${id}`, data);
      return response.data.data;
    } catch (error) {
      throw error.response?.data || error;
    }
  },

  async getTicketMessages(id) {
    try {
      const response = await api.get(`/support/tickets/${id}/messages`);
      return response.data.data;
    } catch (error) {
      throw error.response?.data || error;
    }
  },
};
