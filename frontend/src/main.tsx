import { createRoot } from 'react-dom/client'
import { QueryClient, QueryClientProvider } from '@tanstack/react-query'
import './styles/index.css'
import App from './App.tsx'

export const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      staleTime: 1000 * 60 * 5, 
      gcTime: 1000 * 60 * 15, 
      refetchOnWindowFocus: false, 
      refetchOnMount: false, 
      refetchOnReconnect: false, 
      retry: 1,
    },
  },
})

import { HelmetProvider } from 'react-helmet-async'

createRoot(document.getElementById('root')!).render(
  <HelmetProvider>
    <QueryClientProvider client={queryClient}>
      <App />
    </QueryClientProvider>
  </HelmetProvider>
)
