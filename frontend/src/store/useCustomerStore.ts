import { create } from 'zustand';

export interface Customer {
  id: string;
  name: string;
  status: 'Active' | 'Churn Risk' | 'Inactive';
  engagementScore: number;
  totalValue: number;
}

interface CustomerState {

  selectedCustomer: Customer | null;
  isLoading: boolean;
  searchQuery: string;

  setSelectedCustomer: (customer: Customer | null) => void;
  setSearchQuery: (query: string) => void;
  setIsLoading: (isLoading: boolean) => void;
}

export const useCustomerStore = create<CustomerState>()((set) => ({

  selectedCustomer: null,
  isLoading: false,
  searchQuery: '',

  setSelectedCustomer: (customer) => set({ selectedCustomer: customer }),
  setSearchQuery: (query) => set({ searchQuery: query }),
  setIsLoading: (isLoading) => set({ isLoading }),
}));
