import { useMutation } from '@tanstack/react-query';
import { apiClient } from './axios';
import { API_ENDPOINTS } from './endpoints';

export async function fetchChats() {
  const response = await apiClient.get(API_ENDPOINTS.chats.list);
  return response.data;
}

export async function clearChatsApi(customerId?: string) {
  const response = await apiClient.delete(API_ENDPOINTS.chats.list, {
    params: customerId ? { customer_id: customerId } : undefined
  });
  return response.data;
}

interface GenerateChatPayload {
  job_id: string;
  query: string;
  insurance_agents_id: string;
  policies_id?: string;
  policy_number?: string;
  customers_id?: string;
}

export function useGenerateChatMutation() {
  return useMutation({
    mutationFn: async (payload: GenerateChatPayload) => {
      const response = await apiClient.post(API_ENDPOINTS.llm.generate, payload);
      return response.data;
    }
  });
}
