import { useEffect, useState } from 'react';
import { useUIStore } from '../../store/useUIStore';
import { motion, AnimatePresence } from 'framer-motion';

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

  return (
    <AnimatePresence>
      {isLoaderVisible && (
        <motion.div 
          initial={{ opacity: 0, backdropFilter: "blur(0px)" }}
          animate={{ opacity: 1, backdropFilter: "blur(12px)" }}
          exit={{ opacity: 0, backdropFilter: "blur(0px)" }}
          transition={{ duration: 0.4 }}
          className="fixed inset-0 z-[100] flex flex-col items-center justify-center bg-black/40"
        >
          <motion.div 
            initial={{ scale: 0.9, opacity: 0, y: 20 }}
            animate={{ scale: 1, opacity: 1, y: 0 }}
            exit={{ scale: 0.9, opacity: 0, y: 20 }}
            transition={{ type: "spring", damping: 25, stiffness: 300, delay: 0.1 }}
            className="flex flex-col items-center justify-center gap-8 rounded-3xl bg-black/40 backdrop-blur-2xl border border-white/10 p-12 shadow-[0_0_80px_rgba(100,50,255,0.15)] relative overflow-hidden"
          >
            {/* Ambient Background Glow inside the modal */}
            <div className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 h-40 w-40 bg-indigo-500/20 blur-3xl rounded-full" />
            
            {/* Custom Spinner */}
            <div className="relative flex h-20 w-20 items-center justify-center z-10">
              <motion.div 
                animate={{ rotate: 360 }}
                transition={{ duration: 2, repeat: Infinity, ease: "linear" }}
                className="absolute inset-0 rounded-full border-t-2 border-l-2 border-indigo-400"
              />
              <motion.div 
                animate={{ rotate: -360 }}
                transition={{ duration: 3, repeat: Infinity, ease: "linear" }}
                className="absolute inset-3 rounded-full border-b-2 border-r-2 border-purple-400 opacity-70"
              />
              <motion.div 
                animate={{ scale: [1, 1.2, 1], opacity: [0.7, 1, 0.7] }}
                transition={{ duration: 1.5, repeat: Infinity, ease: "easeInOut" }}
                className="h-5 w-5 rounded-full bg-gradient-to-tr from-indigo-500 to-purple-500 shadow-[0_0_15px_rgba(99,102,241,0.6)]"
              />
            </div>
            
            {/* Funny Message */}
            <motion.p 
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              transition={{ delay: 0.3 }}
              className="text-base font-medium text-white/90 z-10 tracking-wide"
            >
              {message}
            </motion.p>
          </motion.div>
        </motion.div>
      )}
    </AnimatePresence>
  );
}
