import { useMutation, useQuery } from '@tanstack/react-query';
import { apiClient } from './axios';
import { API_ENDPOINTS } from './endpoints';
import { TokenService } from './tokenService';

export interface AgentData {
  id: string;
  name: string;
  email: string;
  phone_number: string;
  agency_name: string;
  license_number: string;
  profile_image_url: string;
}

interface LoginResponse {
  agent_data: AgentData;
  access_token: string;
}

export function useLoginMutation() {
  return useMutation({
    mutationFn: async (credentials: Record<string, string>) => {
      const response = await apiClient.post<LoginResponse>(API_ENDPOINTS.auth.login, credentials);
      return response.data;
    },
    onSuccess: (data) => {
      TokenService.setToken(data.access_token);
    },
  });
}

export function useVerifyTokenQuery() {
  const token = TokenService.getToken();

  return useQuery({
    queryKey: ['auth-verify'],
    queryFn: async () => {
      const response = await apiClient.get<AgentData>(API_ENDPOINTS.auth.verify);
      return response.data;
    },
    enabled: !!token, 
    retry: false, 
    staleTime: 1000 * 60 * 5, 
  });
}
