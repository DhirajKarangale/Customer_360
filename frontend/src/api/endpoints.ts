const BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000/api/v1';

export const API_ENDPOINTS = {
  auth: {
    login: `${BASE_URL}/auth/login`,
    verify: `${BASE_URL}/auth/verify`,
  },
  llm: {
    generate: `${BASE_URL}/llm/generate`,
  },
  policies: {
    list: `${BASE_URL}/policies/`,
  },
  customers: {
    list: `${BASE_URL}/customers/`,
  },
  agents: {
    suggestions: (id: string) => `${BASE_URL}/agents/${id}/suggestions`,
  }
};
