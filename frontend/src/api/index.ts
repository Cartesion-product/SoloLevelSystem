import api from './client'

// Auth
export const authApi = {
  register: (data: { username: string; email: string; password: string }) =>
    api.post('/auth/register', data),
  login: (data: { email: string; password: string }) =>
    api.post('/auth/login', data),
  updateSettings: (data: Record<string, any>) =>
    api.put('/users/settings', data),
}

// Resumes
export const resumeApi = {
  upload: (formData: FormData) =>
    api.post('/resumes', formData, {
      headers: { 'Content-Type': 'multipart/form-data' },
      timeout: 120000,
    }),
  list: () => api.get('/resumes'),
  get: (id: string) => api.get(`/resumes/${id}`),
  update: (id: string, data: Record<string, any>) => api.put(`/resumes/${id}`, data),
  delete: (id: string) => api.delete(`/resumes/${id}`),
  setDefault: (id: string) => api.post(`/resumes/${id}/set-default`),
}

// Jobs
export const jobApi = {
  create: (data: { company_name?: string; position_name: string; jd_text: string }) =>
    api.post('/jobs', data),
  list: () => api.get('/jobs'),
  get: (id: string) => api.get(`/jobs/${id}`),
  update: (id: string, data: Record<string, any>) => api.put(`/jobs/${id}`, data),
  delete: (id: string) => api.delete(`/jobs/${id}`),
  setDefault: (id: string) => api.post(`/jobs/${id}/set-default`),
}

// Interviews
export const interviewApi = {
  start: (data: { resume_id?: string; job_id?: string; max_questions?: number }) =>
    api.post('/interviews/start', data, { timeout: 120000 }),
  end: (id: string) => api.post(`/interviews/${id}/end`),
  getReport: (id: string) => api.get(`/interviews/${id}/report`),
}

// Skills
export const skillApi = {
  getTree: () => api.get('/skills/tree'),
  rebuild: (resumeId: string) => api.post('/skills/rebuild', { resume_id: resumeId }, { timeout: 120000 }),
}

// Quests
export const questApi = {
  list: (status?: string) => api.get('/quests', { params: status ? { status } : {} }),
  updateStatus: (id: string, status: string) => api.put(`/quests/${id}/status`, { status }),
}

// Knowledge
export const knowledgeApi = {
  upload: (formData: FormData) =>
    api.post('/knowledge/upload', formData, { headers: { 'Content-Type': 'multipart/form-data' } }),
  list: () => api.get('/knowledge/documents'),
  delete: (id: string) => api.delete(`/knowledge/documents/${id}`),
}

// Growth
export const growthApi = {
  getDashboard: () => api.get('/growth/dashboard'),
}
