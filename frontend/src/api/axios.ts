import axios from 'axios';
import { TokenService } from './tokenService';

export let globalAbortController = new AbortController();

export const abortAllRequests = () => {
  globalAbortController.abort("User logged out or signed out");
  globalAbortController = new AbortController();
};

export const apiClient = axios.create({
  headers: {
    'Content-Type': 'application/json',
  },
});

apiClient.interceptors.request.use((config) => {
  const token = TokenService.getToken();
  if (token && config.headers) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  if (!config.signal) {
    config.signal = globalAbortController.signal;
  }
  return config;
}, (error) => Promise.reject(error));
