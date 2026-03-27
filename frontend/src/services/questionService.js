import api from './api'

export const questionService = {
  async getQuestions(params = {}) {
    const response = await api.get('/questions', { params })
    return response.data
  },

  async getQuestion(id) {
    const response = await api.get(`/questions/${id}`)
    return response.data
  },

  async createQuestion(data) {
    const response = await api.post('/questions', data)
    return response.data
  },

  async updateQuestion(id, data) {
    const response = await api.put(`/questions/${id}`, data)
    return response.data
  },

  async deleteQuestion(id) {
    const response = await api.delete(`/questions/${id}`)
    return response.data
  },

  async bulkCreateQuestions(examId, questions) {
    const response = await api.post(`/questions/bulk`, { exam_id: examId, questions })
    return response.data
  },

  async reviewQuestion(id, action) {
    const response = await api.post(`/questions/${id}/review`, { action })
    return response.data
  },

  async generateWithAI(examId, topic, count, difficulty) {
    const response = await api.post('/questions/generate-ai', {
      exam_id: examId,
      topic,
      count,
      difficulty,
    })
    return response.data
  },
}
