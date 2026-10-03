import { useUIStore } from '../../store/useUIStore';

export function GlobalToast() {
  const { toast } = useUIStore();

  return (
    <div
      className={`fixed bottom-8 left-1/2 z-[100] flex -translate-x-1/2 transform items-center justify-center rounded-full border border-white/10 bg-white/5 shadow-[0_8px_32px_0_rgba(0,0,0,0.36)] backdrop-blur-xl px-6 py-3 shadow-2xl backdrop-blur-md transition-all duration-500 ease-[cubic-bezier(0.23,1,0.32,1)] ${
        toast.isVisible
          ? 'translate-y-0 opacity-100 scale-100'
          : 'translate-y-12 opacity-0 scale-95 pointer-events-none'
      }`}
    >
      <span className={`text-sm font-medium ${toast.color}`}>
        {toast.text}
      </span>
    </div>
  );
}
