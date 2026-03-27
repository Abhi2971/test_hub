import api from './api';

export const resultService = {
  async getResults(params = {}) {
    try {
      const response = await api.get('/results', { params });
      return response.data;
    } catch (error) {
      throw error.response?.data || error;
    }
  },

  async getResult(id) {
    try {
      const response = await api.get(`/results/${id}`);
      return response.data;
    } catch (error) {
      throw error.response?.data || error;
    }
  },

  async getExamResults(examId) {
    try {
      const response = await api.get(`/results/exam/${examId}`);
      return response.data;
    } catch (error) {
      throw error.response?.data || error;
    }
  },

  async getLeaderboard(examId) {
    try {
      const response = await api.get(`/results/exam/${examId}/leaderboard`);
      return response.data;
    } catch (error) {
      throw error.response?.data || error;
    }
  },

  async getAIRecommendation(resultId) {
    try {
      const response = await api.get(`/results/${resultId}/ai-recommendation`);
      return response.data;
    } catch (error) {
      throw error.response?.data || error;
    }
  },

  async downloadCertificate(resultId) {
    try {
      const response = await api.get(`/results/${resultId}/certificate`);
      return response.data;
    } catch (error) {
      throw error.response?.data || error;
    }
  },
};
