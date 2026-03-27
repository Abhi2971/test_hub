import api from './api';

export const attemptService = {
  async startAttempt(examId, accessMethod, passcode) {
    try {
      const response = await api.post('/attempts/start', {
        exam_id: examId,
        access_method: accessMethod,
        passcode,
      });
      return response.data;
    } catch (error) {
      throw error.response?.data || error;
    }
  },

  async getAttempt(id) {
    try {
      const response = await api.get(`/attempts/${id}`);
      return response.data;
    } catch (error) {
      throw error.response?.data || error;
    }
  },

  async getAttempts(params = {}) {
    try {
      const response = await api.get('/attempts', { params });
      return response.data;
    } catch (error) {
      throw error.response?.data || error;
    }
  },

  async saveAnswers(id, answers) {
    try {
      const formattedAnswers = Object.entries(answers).map(([questionId, selectedOptionId]) => ({
        question_id: questionId,
        selected_option_id: selectedOptionId,
        flagged: false,
        time_spent_seconds: 0,
      }));
      const response = await api.put(`/attempts/${id}/answers`, { answers: formattedAnswers });
      return response.data;
    } catch (error) {
      throw error.response?.data || error;
    }
  },

  async submitAttempt(id) {
    try {
      const response = await api.post(`/attempts/${id}/submit`);
      return response.data;
    } catch (error) {
      throw error.response?.data || error;
    }
  },

  async logViolation(id, type, screenshotUrl) {
    try {
      const response = await api.post(`/attempts/${id}/violation`, {
        type,
        screenshot_url: screenshotUrl,
      });
      return response.data;
    } catch (error) {
      throw error.response?.data || error;
    }
  },

  async getLiveAttempts(examId) {
    try {
      const response = await api.get(`/attempts/live/${examId}`);
      return response.data;
    } catch (error) {
      throw error.response?.data || error;
    }
  },
};
