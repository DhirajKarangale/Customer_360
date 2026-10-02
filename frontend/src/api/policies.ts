import { useQuery } from '@tanstack/react-query';
import { apiClient } from './axios';
import { API_ENDPOINTS } from './endpoints';

export interface Policy {
  id: string;
  policy_number: string;
  customer_id: string;
  agent_id: string;
  policy_type: string;
  status: string;
  start_date: string;
  end_date: string;
  premium_amount: number;
  coverage_amount: number;
}

export interface PoliciesResponse {
  total_items: number;
  total_pages: number;
  current_page: number;
  count: number;
  items: Policy[];
}

export interface PoliciesParams {
  insurance_agent_id: string;
  search_term?: string;
  status?: string;
  policy_type?: string;
  page?: number;
  page_size?: number;
}

export function usePoliciesQuery(params: PoliciesParams, enabled: boolean = true) {
  // Remove undefined or empty string params to clean up URL
  const cleanParams = Object.fromEntries(
    Object.entries(params).filter(([_, v]) => v !== undefined && v !== '')
  );

  return useQuery({
    queryKey: ['policies', cleanParams],
    queryFn: async () => {
      const { data } = await apiClient.get<PoliciesResponse>(API_ENDPOINTS.policies.list, { params: cleanParams });
      return data;
    },
    enabled,
    staleTime: 60 * 1000,
  });
}
