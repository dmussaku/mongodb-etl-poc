import axios from 'axios';

// API base URL - this will be configurable
const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000/api/v1';

// Create axios instance
const api = axios.create({
  baseURL: API_BASE_URL,
  timeout: 10000,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Response interceptor for error handling
api.interceptors.response.use(
  (response) => response,
  (error) => {
    console.error('API Error:', error);
    throw error;
  }
);

export const apiService = {
  // Health endpoints
  getHealth: () => api.get('/health/detailed'),
  
  // ETL Jobs endpoints
  getJobs: (skip = 0, limit = 100) => api.get(`/jobs?skip=${skip}&limit=${limit}`),
  getJob: (jobId: number) => api.get(`/jobs/${jobId}`),
  getJobRuns: (jobId: number, skip = 0, limit = 50) => 
    api.get(`/jobs/${jobId}/runs?skip=${skip}&limit=${limit}`),
  triggerJobRun: (jobId: number) => api.post(`/jobs/${jobId}/run`),
  
  // Connections endpoints
  getConnections: (skip = 0, limit = 100) => api.get(`/connections?skip=${skip}&limit=${limit}`),
  
  // Test endpoints
  testCelery: () => api.post('/test-celery'),
};

export default api;