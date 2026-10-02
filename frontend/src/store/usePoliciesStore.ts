import { create } from 'zustand';
import type { Policy } from '../api/policies';

interface PoliciesState {
  policiesMap: Record<string, Policy>;
  mergePolicies: (policies: Policy[]) => void;
  getAllPolicies: () => Policy[];
}

export const usePoliciesStore = create<PoliciesState>((set, get) => ({
  policiesMap: {},
  mergePolicies: (policies) => set((state) => {
    const newMap = { ...state.policiesMap };
    policies.forEach(p => {
      newMap[p.id] = p;
    });
    return { policiesMap: newMap };
  }),
  getAllPolicies: () => Object.values(get().policiesMap),
}));
