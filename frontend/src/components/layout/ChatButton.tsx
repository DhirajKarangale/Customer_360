import { MessageSquare } from 'lucide-react';

export function ChatButton() {
  return (
    <button
      className="fixed right-4 top-1/2 flex h-14 w-14 -translate-y-1/2 items-center justify-center rounded-full bg-primary text-primary-foreground shadow-lg transition-transform hover:scale-105 active:scale-95 z-50"
      aria-label="Open AI Chat"
    >
      <MessageSquare className="h-6 w-6" />
    </button>
  );
}
