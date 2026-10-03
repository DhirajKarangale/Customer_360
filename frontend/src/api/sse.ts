import { fetchEventSource } from '@microsoft/fetch-event-source';
import { useAIChatStore } from '../store/useAIChatStore';
import { useUIStore } from '../store/useUIStore';
import { queryClient } from '../main';
import { useAuthStore } from '../store/useAuthStore';

export function connectSSE(token: string) {
  const baseUrl = import.meta.env.VITE_API_BASE_URL;
  const url = `${baseUrl}/stream/`;

  const ctrl = new AbortController();

  fetchEventSource(url, {
    method: 'GET',
    headers: {
      Authorization: `Bearer ${token}`,
      Accept: 'text/event-stream',
    },
    signal: ctrl.signal,
    openWhenHidden: true, // IMPORTANT: Keeps connection alive even if tab is in background
    onopen(response) {
      if (response.ok && response.headers.get('content-type')?.includes('text/event-stream')) {
        console.log('SSE connection opened securely');
        return Promise.resolve();
      } else {
        return Promise.reject(new Error(`Failed to establish SSE: ${response.status}`));
      }
    },
    onmessage(event) {
      try {
        if (!event.data) return;

        const data = JSON.parse(event.data);
        console.log('Received SSE Event from backend:', data);

        const jobId = data.job_id || data.id;
        const textResult = data.result || data.message || data.content || JSON.stringify(data);

        // Handle AI Chat events
        if (jobId && typeof jobId === 'string' && jobId.startsWith('aichat_')) {
          const store = useAIChatStore.getState();
          const existingMessage = store.messages.find(m => m.job_id === jobId);

          if (existingMessage) {
            store.updateMessage(jobId, textResult);

            if (!store.isOpen) {
              store.setHasUnread(true);
              useUIStore.getState().showToast('New message from AI Assistant!', 'text-primary', 5000);
            }
          }
        }
        // Handle AI Suggestions events
        else if (data.job_type === 'suggestions_generation' || (jobId && typeof jobId === 'string' && jobId.startsWith('suggestion_'))) {
          // Update React Query Cache directly so it loads instantly when navigating back
          const agentId = useAuthStore.getState().agent?.id;
          if (agentId) {
            queryClient.setQueryData(['suggestions', agentId], {
              status: 'success',
              message: textResult,
              job_id: jobId
            });
          }

          // Dispatch a custom event that the Dashboard page can listen to
          const event = new CustomEvent('agent_suggestions_updated', {
            detail: {
              jobId,
              content: textResult
            }
          });
          window.dispatchEvent(event);
          useUIStore.getState().showToast('New AI suggestions available!', 'text-emerald-500', 5000);
        }
      } catch (e) {
        console.error('Error parsing SSE event:', e);
      }
    },
    onerror(err) {
      console.error('SSE connection error:', err);
    },
    onclose() {
      console.log('SSE stream closed by server');
    }
  });

  return ctrl;
}
