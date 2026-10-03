import { useOutlet, useLocation } from 'react-router-dom';
import { useEffect } from 'react';
import { Navbar } from './Navbar';
import { Footer } from './Footer';
import { ChatPanel } from './ChatPanel';
import { connectSSE } from '../../api/sse';
import { TokenService } from '../../api/tokenService';
import { AnimatePresence, motion } from 'framer-motion';

export function AppLayout() {
  const location = useLocation();
  const currentOutlet = useOutlet();

  useEffect(() => {
    const token = TokenService.getToken();
    if (!token) return;

    const ctrl = connectSSE(token);

    return () => {
      ctrl.abort();
      console.log('SSE connection aborted');
    };
  }, []);

  return (
    <div className="flex min-h-screen flex-col bg-transparent text-white">
      <Navbar />


      <main className="flex-1 container mx-auto px-4 py-8 overflow-hidden">
        <AnimatePresence mode="wait">
          <motion.div
            key={location.pathname}
            initial={{ opacity: 0, y: 20, filter: 'blur(10px)' }}
            animate={{ opacity: 1, y: 0, filter: 'blur(0px)' }}
            exit={{ opacity: 0, y: -20, filter: 'blur(10px)' }}
            transition={{ duration: 0.4, ease: [0.22, 1, 0.36, 1] }}
            className="h-full"
          >
            {currentOutlet}
          </motion.div>
        </AnimatePresence>
      </main>

      <ChatPanel />
      <Footer />
    </div>
  );
}
