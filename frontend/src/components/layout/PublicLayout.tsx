import { useOutlet, useLocation } from 'react-router-dom';
import { Navbar } from './Navbar';
import { Footer } from './Footer';
import { AnimatePresence, motion } from 'framer-motion';

export function PublicLayout() {
  const location = useLocation();
  const currentOutlet = useOutlet();

  return (
    <div className="flex min-h-screen flex-col bg-transparent text-white">
      <Navbar />
      
      {/* Main Content Area */}
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

      <Footer />
    </div>
  );
}
