import axios from 'axios'

const api = axios.create({
  baseURL: '/api',
  timeout: 30000,
})

// 请求拦截器
api.interceptors.request.use(
  (config) => {
    return config
  },
  (error) => {
    return Promise.reject(error)
  }
)

// 响应拦截器
api.interceptors.response.use(
  (response) => {
    return response.data
  },
  (error) => {
    console.error('API Error:', error)
    return Promise.reject(error)
  }
)

export default api

// API方法
export const targetsAPI = {
  list: (params?: any) => api.get('/targets/', { params }),
  get: (id: number) => api.get(`/targets/${id}`),
  create: (data: any) => api.post('/targets/', data),
  update: (id: number, data: any) => api.put(`/targets/${id}`, data),
  delete: (id: number) => api.delete(`/targets/${id}`),
  batchImport: (data: any) => api.post('/targets/batch', data),
  importExcel: (file: File) => {
    const formData = new FormData()
    formData.append('file', file)
    return api.post('/targets/import-excel', formData, {
      headers: { 'Content-Type': 'multipart/form-data' }
    })
  },
  getStats: () => api.get('/targets/stats/overview')
}

export const templatesAPI = {
  list: (params?: any) => api.get('/templates/', { params }),
  get: (id: number) => api.get(`/templates/${id}`),
  create: (data: any) => api.post('/templates/', data),
  update: (id: number, data: any) => api.put(`/templates/${id}`, data),
  delete: (id: number) => api.delete(`/templates/${id}`),
  preview: (id: number, data: any) => api.post(`/templates/${id}/preview`, data),
  getComparison: () => api.get('/templates/stats/comparison')
}

export const accountsAPI = {
  list: (params?: any) => api.get('/accounts/', { params }),
  get: (id: number) => api.get(`/accounts/${id}`),
  create: (data: any) => api.post('/accounts/', data),
  update: (id: number, data: any) => api.put(`/accounts/${id}`, data),
  delete: (id: number) => api.delete(`/accounts/${id}`),
  getHealth: (id: number) => api.get(`/accounts/${id}/health`),
  getHealthOverview: () => api.get('/accounts/stats/health-overview')
}

export const messagesAPI = {
  list: (params?: any) => api.get('/messages/', { params }),
  get: (id: number) => api.get(`/messages/${id}`),
  updateStatus: (id: number, status: string, data?: any) =>
    api.put(`/messages/${id}/status`, { status, ...data }),
  getStats: (params?: any) => api.get('/messages/stats/overview', { params }),
  getStatsByTime: () => api.get('/messages/stats/by-time'),
  getPendingReplies: () => api.get('/messages/pending-replies')
}

export const tasksAPI = {
  list: (params?: any) => api.get('/tasks/', { params }),
  get: (id: number) => api.get(`/tasks/${id}`),
  create: (data: any) => api.post('/tasks/', data),
  start: (id: number) => api.post(`/tasks/${id}/start`),
  pause: (id: number) => api.post(`/tasks/${id}/pause`),
  resume: (id: number) => api.post(`/tasks/${id}/resume`),
  cancel: (id: number) => api.post(`/tasks/${id}/cancel`),
  getProgress: (id: number) => api.get(`/tasks/${id}/progress`),
  delete: (id: number) => api.delete(`/tasks/${id}`)
}

export const analyticsAPI = {
  getDashboard: () => api.get('/analytics/dashboard'),
  getConversionFunnel: (params?: any) => api.get('/analytics/conversion-funnel', { params }),
  getBestTimeAnalysis: () => api.get('/analytics/best-time-analysis'),
  getTemplatePerformance: () => api.get('/analytics/template-performance'),
  getFollowerAnalysis: () => api.get('/analytics/follower-analysis')
}
