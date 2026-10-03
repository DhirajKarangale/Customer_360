import { create } from 'zustand';

interface ToastState {
  text: string;
  color: string;
  isVisible: boolean;
}

interface UIState {

  isLoaderVisible: boolean;
  showLoader: () => void;
  hideLoader: () => void;

  toast: ToastState;
  showToast: (text: string, color?: string, timeMs?: number) => void;
  hideToast: () => void;
}

export const useUIStore = create<UIState>()((set) => ({
  isLoaderVisible: false,
  showLoader: () => set({ isLoaderVisible: true }),
  hideLoader: () => set({ isLoaderVisible: false }),

  toast: { text: '', color: 'text-foreground', isVisible: false },
  showToast: (text, color = 'text-foreground', timeMs = 3000) => {
    set({ toast: { text, color, isVisible: true } });

    setTimeout(() => {
      set((state) => ({ toast: { ...state.toast, isVisible: false } }));
    }, timeMs);
  },
  hideToast: () => set((state) => ({ toast: { ...state.toast, isVisible: false } })),
}));
