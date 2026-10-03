import { useQuery } from '@tanstack/react-query';
import { apiClient } from './axios';
import { API_ENDPOINTS } from './endpoints';

export interface Customer {
  id: string;
  name: string;
  email: string;
  phone_number: string;
  date_of_birth: string;
  address: string;
}

export interface CustomersResponse {
  total_items: number;
  total_pages: number;
  current_page: number;
  count: number;
  items: Customer[];
}

export interface CustomersParams {
  insurance_agent_id: string;
  search_term?: string;
  page?: number;
  page_size?: number;
}

export function useCustomersQuery(params: CustomersParams, enabled: boolean = true) {
  // Remove undefined or empty string params to clean up URL
  const cleanParams = Object.fromEntries(
    Object.entries(params).filter(([_, v]) => v !== undefined && v !== '')
  );

  return useQuery({
    queryKey: ['customers', cleanParams],
    queryFn: async () => {
      const { data } = await apiClient.get<CustomersResponse>(API_ENDPOINTS.customers.list, { params: cleanParams });
      return data;
    },
    enabled,
  });
}
