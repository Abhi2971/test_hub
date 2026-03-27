import api from './api';

export const examService = {
  async createExam(data) {
    try {
      const response = await api.post('/exams', data);
      return response.data;
    } catch (error) {
      throw error.response?.data || error;
    }
  },

  async getExams(filters = {}) {
    try {
      const response = await api.get('/exams', { params: filters });
      return response.data;
    } catch (error) {
      throw error.response?.data || error;
    }
  },

  async getExam(id) {
    try {
      const response = await api.get(`/exams/${id}`);
      return response.data;
    } catch (error) {
      throw error.response?.data || error;
    }
  },

  async updateExam(id, data) {
    try {
      const response = await api.patch(`/exams/${id}`, data);
      return response.data;
    } catch (error) {
      throw error.response?.data || error;
    }
  },

  async deleteExam(id) {
    try {
      const response = await api.delete(`/exams/${id}`);
      return response.data;
    } catch (error) {
      throw error.response?.data || error;
    }
  },

  async publishExam(id) {
    try {
      const response = await api.post(`/exams/${id}/publish`);
      return response.data;
    } catch (error) {
      throw error.response?.data || error;
    }
  },

  async closeExam(id) {
    try {
      const response = await api.post(`/exams/${id}/close`);
      return response.data;
    } catch (error) {
      throw error.response?.data || error;
    }
  },

  async approveExam(id) {
    try {
      const response = await api.post(`/exams/${id}/approve`);
      return response.data;
    } catch (error) {
      throw error.response?.data || error;
    }
  },

  async rejectExam(id) {
    try {
      const response = await api.post(`/exams/${id}/reject`);
      return response.data;
    } catch (error) {
      throw error.response?.data || error;
    }
  },

  async generateMagicLink(id) {
    try {
      const response = await api.post(`/exams/${id}/magic-link`);
      return response.data;
    } catch (error) {
      throw error.response?.data || error;
    }
  },

  async getMarketplace(filters = {}) {
    try {
      const response = await api.get('/exams/marketplace', { params: filters });
      return response.data;
    } catch (error) {
      throw error.response?.data || error;
    }
  },

  async assignStudents(examId, studentIds) {
    try {
      const response = await api.post(`/exams/${examId}/students`, { student_ids: studentIds });
      return response.data;
    } catch (error) {
      throw error.response?.data || error;
    }
  },

  async removeStudents(examId, studentIds) {
    try {
      const response = await api.delete(`/exams/${examId}/students`, { data: { student_ids: studentIds } });
      return response.data;
    } catch (error) {
      throw error.response?.data || error;
    }
  },

  async uploadPDF(examId, file, topic) {
    try {
      const formData = new FormData();
      formData.append('file', file);
      formData.append('topic', topic);
      const response = await api.post(`/exams/${examId}/upload-pdf`, formData, {
        headers: { 'Content-Type': 'multipart/form-data' },
      });
      return response.data;
    } catch (error) {
      throw error.response?.data || error;
    }
  },

  async getExamAnalytics(id) {
    try {
      const response = await api.get(`/exams/${id}/analytics`);
      return response.data;
    } catch (error) {
      throw error.response?.data || error;
    }
  },

  async getExamResults(id) {
    try {
      const response = await api.get(`/exams/${id}/results`);
      return response.data;
    } catch (error) {
      throw error.response?.data || error;
    }
  },
};
