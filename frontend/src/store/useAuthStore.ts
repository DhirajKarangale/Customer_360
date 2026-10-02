import { create } from 'zustand';
import type { AgentData } from '../api/auth';

interface AuthState {
  agent: AgentData | null;
  setAgent: (agent: AgentData | null) => void;
  logout: () => void;
}

export const useAuthStore = create<AuthState>()((set) => ({
  agent: null,
  setAgent: (agent) => set({ agent }),
  logout: () => set({ agent: null }),
}));
