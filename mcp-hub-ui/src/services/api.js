import axios from 'axios';

// Create axios instance
const api = axios.create({
  baseURL: process.env.REACT_APP_API_URL || 'http://localhost:8000',
  headers: {
    'Content-Type': 'application/json',
  },
  timeout: 30000, // 30 seconds
});

// Request interceptor
api.interceptors.request.use(
  (config) => {
    // Add auth token if available
    const token = localStorage.getItem('auth_token');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// Response interceptor
api.interceptors.response.use(
  (response) => {
    return response.data;
  },
  (error) => {
    if (error.response?.status === 401) {
      // Handle unauthorized
      localStorage.removeItem('auth_token');
      window.location.href = '/login';
    }
    return Promise.reject(error);
  }
);

// Health and Status
export const health = {
  check: () => api.get('/api/health'),
  getStatus: () => api.get('/api/status'),
};

// Tools API
export const tools = {
  getTools: () => api.get('/api/tools'),
  getTool: (toolName) => api.get(`/api/tools/${toolName}`),
  executeTool: (toolName, toolArguments) => 
    api.post(`/api/tools/${toolName}/execute`, toolArguments),
  getServers: () => api.get('/api/tools/servers'),
  toggleServer: (serverName, enabled) => 
    api.post(`/api/tools/servers/${serverName}/toggle`, { enabled }),
};

// Chat API
export const chat = {
  sendMessage: (data) => api.post('/api/chat/', data),
  getHistory: () => api.get('/api/chat/history'),
  clearHistory: () => api.delete('/api/chat/history'),
};

// Resources API
export const resources = {
  getResources: () => api.get('/api/resources/'),
  getResource: (resourceName) => api.get(`/api/resources/${resourceName}`),
  createResource: (resourceData) => api.post('/api/resources/', resourceData),
  updateResource: (resourceName, resourceData) => api.put(`/api/resources/${resourceName}`, resourceData),
  deleteResource: (resourceName) => api.delete(`/api/resources/${resourceName}`),
  getServers: () => api.get('/api/resources/servers/'),
  createServer: (serverData) => api.post('/api/resources/servers/', serverData),
  deleteServer: (serverName) => api.delete(`/api/resources/servers/${serverName}`),
};

// Auth API
export const auth = {
  login: (credentials) => api.post('/api/auth/login', credentials),
  logout: () => api.post('/api/auth/logout'),
  getProfile: () => api.get('/api/auth/profile'),
};

// Named and default exports
export { api };
export default api;
