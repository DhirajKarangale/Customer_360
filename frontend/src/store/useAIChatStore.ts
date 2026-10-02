import { create } from 'zustand';
import { persist } from 'zustand/middleware';

export interface ChatMessage {
  job_id: string;
  query: string;
  message: string | null;
  status: 'processing' | 'completed' | 'failed';
  sendTime: number;
}

interface AIChatState {
  isOpen: boolean;
  setIsOpen: (isOpen: boolean) => void;
  hasUnread: boolean;
  setHasUnread: (hasUnread: boolean) => void;
  draftInput: string;
  setDraftInput: (val: string) => void;
  messages: ChatMessage[];
  addMessage: (job_id: string, query: string) => void;
  updateMessage: (job_id: string, message: string) => void;
  markAsFailed: (job_id: string) => void;
  clearMessages: () => void;
}

export const useAIChatStore = create<AIChatState>()(
  persist(
    (set) => ({
      isOpen: false,
      setIsOpen: (isOpen) => set({ isOpen }),
      hasUnread: false,
      setHasUnread: (hasUnread) => set({ hasUnread }),
      draftInput: '',
      setDraftInput: (draftInput) => set({ draftInput }),
      messages: [],
      addMessage: (job_id, query) => 
        set((state) => ({
          messages: [...state.messages, { 
            job_id, 
            query, 
            message: null, 
            status: 'processing',
            sendTime: Date.now()
          }]
        })),
      updateMessage: (job_id, message) => 
        set((state) => ({
          messages: state.messages.map((msg) => 
            msg.job_id === job_id ? { ...msg, message, status: 'completed' } : msg
          )
        })),
      markAsFailed: (job_id) =>
        set((state) => ({
          messages: state.messages.map((msg) =>
            msg.job_id === job_id ? { ...msg, status: 'failed', message: 'Request failed: No response received after 5 minutes.' } : msg
          )
        })),
      clearMessages: () => set({ messages: [], draftInput: '' })
    }),
    {
      name: 'ai-chat-storage',
      // We only want to persist the chat history and the current typed input
      // We don't want to persist the panel being open/closed across reloads
      partialize: (state) => ({ 
        messages: state.messages, 
        draftInput: state.draftInput 
      }),
    }
  )
);
