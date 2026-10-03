import { createRoot } from 'react-dom/client'
import { QueryClient, QueryClientProvider } from '@tanstack/react-query'
import './styles/index.css'
import App from './App.tsx'

export const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      staleTime: 1000 * 60 * 5, // 5 minutes (data considered fresh)
      gcTime: 1000 * 60 * 15, // 15 minutes (keep unused data in memory)
      refetchOnWindowFocus: false, // Prevent refetching when switching tabs
      refetchOnMount: false, // Prevent refetching on component remount
      refetchOnReconnect: false, // Prevent refetching on network reconnect
      retry: 1,
    },
  },
})

createRoot(document.getElementById('root')!).render(
  <QueryClientProvider client={queryClient}>
    <App />
  </QueryClientProvider>
)
