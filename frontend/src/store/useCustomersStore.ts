import { create } from 'zustand';
import type { Customer } from '../api/customers';

interface CustomersState {
  customersMap: Record<string, Customer>;
  mergeCustomers: (customers: Customer[]) => void;
  getAllCustomers: () => Customer[];
}

export const useCustomersStore = create<CustomersState>((set, get) => ({
  customersMap: {},
  mergeCustomers: (customers) => set((state) => {
    const newMap = { ...state.customersMap };
    customers.forEach(c => {
      newMap[c.id] = c;
    });
    return { customersMap: newMap };
  }),
  getAllCustomers: () => Object.values(get().customersMap),
}));
