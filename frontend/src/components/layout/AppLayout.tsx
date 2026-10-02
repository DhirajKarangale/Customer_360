import { Outlet } from 'react-router-dom';
import { useEffect } from 'react';
import { Navbar } from './Navbar';
import { Footer } from './Footer';
import { ChatPanel } from './ChatPanel';
import { connectSSE } from '../../api/sse';
import { TokenService } from '../../api/tokenService';

export function AppLayout() {
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
    <div className="flex min-h-screen flex-col bg-background text-foreground">
      <Navbar />
      
      {/* Main Content Area */}
      <main className="flex-1 container mx-auto px-4 py-8">
        <Outlet />
      </main>

      <ChatPanel />
      <Footer />
    </div>
  );
}
