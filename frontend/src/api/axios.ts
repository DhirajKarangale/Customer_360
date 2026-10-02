import axios from 'axios';
import { TokenService } from './tokenService';

export const apiClient = axios.create({
  headers: {
    'Content-Type': 'application/json',
  },
});

// Add a request interceptor to automatically attach JWT token
apiClient.interceptors.request.use((config) => {
  const token = TokenService.getToken();
  if (token && config.headers) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
}, (error) => Promise.reject(error));
