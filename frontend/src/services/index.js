import api from './api'

export const farmService = {
  list:   ()      => api.get('/api/farms'),
  get:    (id)    => api.get(`/api/farms/${id}`),
  create: (data)  => api.post('/api/farms', data),
  update: (id, d) => api.put(`/api/farms/${id}`, d),
  delete: (id)    => api.delete(`/api/farms/${id}`),
  stats:  (id)    => api.get(`/api/farms/${id}/stats`),
}

export const plotService = {
  list:   (farmId) => api.get('/api/plots', { params: { farmId } }),
  get:    (id)     => api.get(`/api/plots/${id}`),
  create: (data)   => api.post('/api/plots', data),
  update: (id, d)  => api.put(`/api/plots/${id}`, d),
  delete: (id)     => api.delete(`/api/plots/${id}`),
}

export const cropService = {
  list:   (plotId, status) => api.get('/api/crops', { params: { plotId, status } }),
  get:    (id)    => api.get(`/api/crops/${id}`),
  create: (data)  => api.post('/api/crops', data),
  update: (id, d) => api.put(`/api/crops/${id}`, d),
  delete: (id)    => api.delete(`/api/crops/${id}`),
}

export const activityService = {
  list:   (p)     => api.get('/api/activities', { params: p }),
  today:  ()      => api.get('/api/activities/today'),
  get:    (id)    => api.get(`/api/activities/${id}`),
  create: (data)  => api.post('/api/activities', data),
  update: (id, d) => api.put(`/api/activities/${id}`, d),
  delete: (id)    => api.delete(`/api/activities/${id}`),
}

export const workerService = {
  list:   (farmId) => api.get('/api/workers', { params: { farmId } }),
  get:    (id)     => api.get(`/api/workers/${id}`),
  create: (data)   => api.post('/api/workers', data),
  update: (id, d)  => api.put(`/api/workers/${id}`, d),
  delete: (id)     => api.delete(`/api/workers/${id}`),
  history:(id)     => api.get(`/api/workers/${id}/history`),
}

export const expenseService = {
  list:    (p)    => api.get('/api/expenses', { params: p }),
  summary: (farmId) => api.get('/api/expenses/summary', { params: { farmId } }),
  create:  (data) => api.post('/api/expenses', data),
  update:  (id,d) => api.put(`/api/expenses/${id}`, d),
  delete:  (id)   => api.delete(`/api/expenses/${id}`),
}

export const inventoryService = {
  list:   (p)    => api.get('/api/inventory', { params: p }),
  alerts: ()     => api.get('/api/inventory/alerts'),
  create: (data) => api.post('/api/inventory', data),
  update: (id,d) => api.put(`/api/inventory/${id}`, d),
  delete: (id)   => api.delete(`/api/inventory/${id}`),
}

export const diseaseService = {
  predict: (formData) => api.post('/api/disease/predict', formData, {
    headers: { 'Content-Type': 'multipart/form-data' }
  }),
  history: () => api.get('/api/disease/history'),
}

export const riskService = {
  assess:  (data) => api.post('/api/risk/assess', data),
  history: (plotId) => api.get('/api/risk/history', { params: { plotId } }),
  summary: () => api.get('/api/risk/summary'),
}

export const recommendationService = {
  crop:      (data) => api.post('/api/recommendation/crop', data),
  irrigation:(data) => api.post('/api/irrigation/advise', data),
}

export const weatherService = {
  current:  (p) => api.get('/api/weather/current', { params: p }),
  forecast: (p) => api.get('/api/weather/forecast', { params: p }),
}

export const anomalyService = {
  analyze: (farmId) => api.get(`/api/anomaly/analyze/${farmId}`),
  history: (farmId) => api.get(`/api/anomaly/history/${farmId}`),
}

export const healthScoreService = {
  compute:  (data)   => api.post('/api/farm-health/score', data),
  history:  (farmId) => api.get(`/api/farm-health/${farmId}/history`),
  latest:   (farmId) => api.get(`/api/farm-health/${farmId}/latest`),
}

export const sustainabilityService = {
  score:   (data)   => api.post('/api/sustainability/score', data),
  history: (farmId) => api.get(`/api/sustainability/${farmId}/history`),
}

export const intelligenceService = {
  recommendations: (farmId) => api.get(`/api/intelligence/recommendations/${farmId}`),
}

export const advisorService = {
  run:     (data)   => api.post('/api/advisor/run', data),
  history: (farmId) => api.get(`/api/advisor/history/${farmId}`),
}

export const assistantService = {
  chat:    (data) => api.post('/api/assistant/chat', data),
  history: (sid)  => api.get('/api/assistant/history', { params: { sessionId: sid } }),
}

export const alertService = {
  list:       (p)     => api.get('/api/alerts', { params: p }),
  summary:    ()      => api.get('/api/alerts/summary'),
  create:     (data)  => api.post('/api/alerts', data),
  markRead:   (id)    => api.patch(`/api/alerts/${id}/read`),
  markAllRead:()      => api.patch('/api/alerts/mark-all-read'),
  delete:     (id)    => api.delete(`/api/alerts/${id}`),
  generate:   (farmId)=> api.post(`/api/alerts/generate/${farmId}`),
}
