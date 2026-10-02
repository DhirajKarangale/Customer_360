import { useEffect, useState } from 'react';
import { Loader2 } from 'lucide-react';
import { useUIStore } from '../../store/useUIStore';

const LOADING_MESSAGES = [
  "Waking up the AI from its nap...",
  "Counting all the snowflakes...",
  "Convincing the neural network to cooperate...",
  "Brewing digital coffee for the agents...",
  "Mining data like it's 1849...",
  "Translating human to machine and back...",
  "Assembling insights out of thin air...",
  "Asking nicely for the database to respond...",
  "Teaching the AI some manners...",
  "Processing 360 degrees of customer..."
];

export function GlobalLoader() {
  const isLoaderVisible = useUIStore((state) => state.isLoaderVisible);
  const [message, setMessage] = useState(LOADING_MESSAGES[0]);

  useEffect(() => {
    if (isLoaderVisible) {
      // Pick a random message every time the loader is shown
      const randomIndex = Math.floor(Math.random() * LOADING_MESSAGES.length);
      setMessage(LOADING_MESSAGES[randomIndex]);
    }
  }, [isLoaderVisible]);

  if (!isLoaderVisible) return null;

  return (
    <div className="fixed inset-0 z-[100] flex flex-col items-center justify-center bg-black/60 backdrop-blur-sm animate-in fade-in duration-300">
      <div className="flex flex-col items-center justify-center gap-6 rounded-2xl bg-card/80 p-8 shadow-2xl border border-border backdrop-blur-md">
        {/* Spinner */}
        <Loader2 className="h-12 w-12 animate-spin text-primary" />
        
        {/* Funny Message */}
        <p className="text-sm font-medium text-foreground animate-pulse">
          {message}
        </p>
      </div>
    </div>
  );
}
