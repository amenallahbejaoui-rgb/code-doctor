import axios from 'axios';

// Cache for repository data
let repoCache = {
  data: null,
  timestamp: null,
  expiryTime: 30000 // 30 seconds cache
};

// Create axios instance with default config
const api = axios.create({
  baseURL: 'http://localhost:5000',
  headers: {
    'Content-Type': 'application/json'
  }
});

// Add request interceptor to add auth token
api.interceptors.request.use(config => {
  const token = localStorage.getItem('token');
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

// Add response interceptor to handle rate limiting
api.interceptors.response.use(
  response => response,
  error => {
    if (error.response?.status === 429) {
      // If rate limited, wait and retry once
      return new Promise(resolve => {
        setTimeout(() => {
          resolve(api(error.config));
        }, 1000); // Wait 1 second before retry
      });
    }
    return Promise.reject(error);
  }
);

export const repoService = {
  async getRepoList() {
    // Check if we have valid cached data
    const now = Date.now();
    if (repoCache.data && repoCache.timestamp && (now - repoCache.timestamp < repoCache.expiryTime)) {
      return repoCache.data;
    }

    try {
      const response = await api.get('/repo/list');
      // Update cache
      repoCache.data = response.data;
      repoCache.timestamp = now;
      return response.data;
    } catch (error) {
      console.error('Error fetching repository list:', error);
      throw error;
    }
  },

  async getRepoById(repoId) {
    try {
      const repos = await this.getRepoList();
      return repos.find(r => String(r.id) === String(repoId)) || null;
    } catch (error) {
      console.error('Error fetching repository by ID:', error);
      throw error;
    }
  },

  clearCache() {
    repoCache.data = null;
    repoCache.timestamp = null;
  }
}; 