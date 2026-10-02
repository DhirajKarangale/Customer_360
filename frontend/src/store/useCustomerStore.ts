import { create } from 'zustand';

// Define the types for the store
export interface Customer {
  id: string;
  name: string;
  status: 'Active' | 'Churn Risk' | 'Inactive';
  engagementScore: number;
  totalValue: number;
}

interface CustomerState {
  // State
  selectedCustomer: Customer | null;
  isLoading: boolean;
  searchQuery: string;

  // Actions
  setSelectedCustomer: (customer: Customer | null) => void;
  setSearchQuery: (query: string) => void;
  setIsLoading: (isLoading: boolean) => void;
}

// Create the store
export const useCustomerStore = create<CustomerState>()((set) => ({
  // Initial state
  selectedCustomer: null,
  isLoading: false,
  searchQuery: '',

  // Actions
  setSelectedCustomer: (customer) => set({ selectedCustomer: customer }),
  setSearchQuery: (query) => set({ searchQuery: query }),
  setIsLoading: (isLoading) => set({ isLoading }),
}));
