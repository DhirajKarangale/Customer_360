import { useQuery } from '@tanstack/react-query';
import { apiClient } from './axios';
import { API_ENDPOINTS } from './endpoints';

export interface SuggestionsResponse {
  status: 'success' | 'pending';
  message: string;
  action_text?: string;
  job_id?: string;
  last_updated?: string;
}

export function useSuggestionsQuery(agentId: string, enabled: boolean = true) {
  return useQuery({
    queryKey: ['suggestions', agentId],
    queryFn: async () => {
      const { data } = await apiClient.get<SuggestionsResponse>(API_ENDPOINTS.agents.suggestions(agentId));
      return data;
    },
    enabled: !!agentId && enabled,
  });
}
