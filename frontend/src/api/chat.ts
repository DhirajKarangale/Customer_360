import { useMutation } from '@tanstack/react-query';
import { apiClient } from './axios';
import { API_ENDPOINTS } from './endpoints';

interface GenerateChatPayload {
  job_id: string;
  query: string;
  insurance_agents_id: string;
  policies_id?: string;
  policy_number?: string;
}

export function useGenerateChatMutation() {
  return useMutation({
    mutationFn: async (payload: GenerateChatPayload) => {
      const response = await apiClient.post(API_ENDPOINTS.llm.generate, payload);
      return response.data;
    }
  });
}
