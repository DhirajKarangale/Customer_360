import { useEffect, useRef } from 'react';
import { ChevronLeft, Send, ArrowUp, ArrowDown, Trash2 } from 'lucide-react';
import { useAIChatStore } from '../../store/useAIChatStore';
import { useAuthStore } from '../../store/useAuthStore';
import { useGenerateChatMutation, clearChatsApi } from '../../api/chat';

export function ChatPanel() {
  const { 
    messages, 
    addMessage, 
    isOpen, 
    setIsOpen, 
    hasUnread, 
    setHasUnread,
    draftInput,
    setDraftInput,
    markAsFailed,
    activePolicyId,
    activePolicyNumber,
    setActivePolicy,
    activeCustomerId,
    activeCustomerName,
    setActiveCustomer,
    clearMessages
  } = useAIChatStore();
  
  const agent = useAuthStore((state) => state.agent);
  const generateMutation = useGenerateChatMutation();

  const scrollRef = useRef<HTMLDivElement>(null);

  // Stop background scroll when open
  useEffect(() => {
    if (isOpen) {
      document.body.style.overflow = 'hidden';
      // Clear unread badge when opening
      if (hasUnread) setHasUnread(false);
      
      // Auto scroll to bottom when opened
      setTimeout(scrollToBottom, 100);
    } else {
      document.body.style.overflow = 'unset';
    }
    return () => {
      document.body.style.overflow = 'unset';
    };
  }, [isOpen, hasUnread, setHasUnread]);

  // Timeout checker: marks messages as failed if > 5 minutes
  useEffect(() => {
    const interval = setInterval(() => {
      const now = Date.now();
      messages.forEach((msg) => {
        if (msg.status === 'processing') {
          // 5 minutes = 300,000 milliseconds
          if (now - msg.sendTime > 300000) {
            markAsFailed(msg.job_id);
          }
        }
      });
    }, 10000); // check every 10 seconds

    return () => clearInterval(interval);
  }, [messages, markAsFailed]);

  const togglePanel = () => {
    if (!isOpen) {
      setActivePolicy(null, null);
      setActiveCustomer(null, null);
    }
    setIsOpen(!isOpen);
  };

  const scrollToTop = () => {
    scrollRef.current?.scrollTo({ top: 0, behavior: 'smooth' });
  };

  const scrollToBottom = () => {
    scrollRef.current?.scrollTo({ top: scrollRef.current.scrollHeight, behavior: 'smooth' });
  };

  const handleSend = (e: React.FormEvent) => {
    e.preventDefault();
    if (!draftInput.trim() || !agent) return;
    
    // New job ID format
    const jobId = `aichat_${crypto.randomUUID()}`;
    const userQuery = draftInput.trim();
    
    // Add to zustand immediately (message = null, status = processing)
    addMessage(jobId, userQuery, activeCustomerId || undefined, activePolicyId || undefined);
    setDraftInput(''); // Clear the draft input

    setTimeout(scrollToBottom, 100);

    // Call the API
    generateMutation.mutate({
      job_id: jobId,
      query: userQuery,
      insurance_agents_id: agent.id,
      policies_id: activePolicyId || undefined,
      policy_number: activePolicyNumber || undefined,
      customers_id: activeCustomerId || undefined,
    }, {
      onError: () => {
        markAsFailed(jobId);
      }
    });
  };

  return (
    <>
      {/* Backdrop overlay (blocks background clicks) */}
      <div 
        className={`fixed inset-0 z-40 bg-background/60 backdrop-blur-sm transition-opacity duration-300 ${isOpen ? 'opacity-100' : 'opacity-0 pointer-events-none'}`} 
        onClick={() => setIsOpen(false)}
      />

      {/* The Chat Panel */}
      <div 
        className={`fixed right-0 top-0 z-50 flex h-screen w-full max-w-md flex-col border-l border-border bg-card shadow-2xl transition-transform duration-500 ease-[cubic-bezier(0.32,0.72,0,1)] ${isOpen ? 'translate-x-0' : 'translate-x-full'}`}
      >
        {/* Sticky Toggle Button */}
        <button
          onClick={togglePanel}
          className={`absolute left-0 top-1/2 flex h-20 w-8 -translate-x-full -translate-y-1/2 items-center justify-center rounded-l-xl border-y border-l border-border bg-card text-foreground shadow-lg transition-colors duration-300 hover:bg-muted ${isOpen ? 'bg-primary border-primary text-primary-foreground hover:bg-primary/90' : ''}`}
          aria-label="Toggle Chat"
        >
          {/* Unread Notification Dot */}
          {!isOpen && hasUnread && (
            <span className="absolute -top-1 -left-1 flex h-3 w-3">
              <span className="absolute inline-flex h-full w-full animate-ping rounded-full bg-destructive opacity-75"></span>
              <span className="relative inline-flex h-3 w-3 rounded-full bg-destructive border border-background"></span>
            </span>
          )}

          {/* Arrow rotates 180 degrees when open */}
          <ChevronLeft className={`h-6 w-6 transition-transform duration-500 ease-[cubic-bezier(0.32,0.72,0,1)] ${isOpen ? 'rotate-180' : 'rotate-0'}`} />
        </button>

        {/* Panel Header */}
        <div className="flex items-center justify-between border-b border-border p-4 bg-background/50 backdrop-blur-md">
          <h2 className="text-sm font-semibold text-foreground flex items-center gap-2">
            {activePolicyNumber ? `Asking about ${activePolicyNumber}` : activeCustomerName ? `Asking about ${activeCustomerName}` : 'AI Assistant'}
          </h2>
          <div className="flex items-center gap-3">
            {(activePolicyNumber || activeCustomerName) && (
              <button 
                onClick={() => {
                  setActivePolicy(null, null);
                  setActiveCustomer(null, null);
                }}
                className="text-xs text-muted-foreground hover:text-foreground transition-colors"
              >
                Clear Context
              </button>
            )}
            {(() => {
              const displayMessages = activeCustomerId ? messages.filter(m => m.customer_id === activeCustomerId) : messages;
              return displayMessages.length > 0 && (
                <button
                  onClick={async () => {
                    try {
                      await clearChatsApi(activeCustomerId || undefined);
                      clearMessages(activeCustomerId || undefined);
                    } catch (e) {
                      console.error("Failed to clear chats", e);
                    }
                  }}
                  className="text-muted-foreground hover:text-destructive transition-colors"
                  title="Clear Chat History"
                >
                  <Trash2 className="h-4 w-4" />
                </button>
              );
            })()}
          </div>
        </div>

        {/* Messages Area (Scrollable) */}
        <div className="relative flex-1 overflow-hidden bg-background/20">
          
          {/* Top/Bottom Scroll Buttons */}
          <div className="absolute right-4 top-1/2 -translate-y-1/2 z-10 flex flex-col gap-3">
             <button onClick={scrollToTop} className="rounded-full border border-border bg-card/80 p-2 text-muted-foreground shadow-sm backdrop-blur-md transition-colors hover:bg-muted hover:text-foreground">
               <ArrowUp className="h-4 w-4" />
             </button>
             <button onClick={scrollToBottom} className="rounded-full border border-border bg-card/80 p-2 text-muted-foreground shadow-sm backdrop-blur-md transition-colors hover:bg-muted hover:text-foreground">
               <ArrowDown className="h-4 w-4" />
             </button>
          </div>
          
          <div ref={scrollRef} className="h-full overflow-y-auto p-4 space-y-6 pb-20">
            {(() => {
              const displayMessages = activeCustomerId ? messages.filter(m => m.customer_id === activeCustomerId) : messages;
              return (
                <>
                  {displayMessages.length === 0 && (
                    <div className="flex h-full items-center justify-center text-center text-sm text-muted-foreground">
                      Hello! I am your AI assistant. <br/> How can I help you today?
                    </div>
                  )}
                  {displayMessages.map((msg) => (
              <div key={msg.job_id} className="space-y-6">
                {/* User Query */}
                <div className="flex justify-end">
                  <div className="max-w-[85%] whitespace-pre-wrap rounded-2xl px-4 py-3 text-sm shadow-sm bg-primary text-primary-foreground rounded-br-none">
                    {msg.query}
                  </div>
                </div>
                
                {/* LLM Response */}
                <div className="flex justify-start">
                  <div className={`max-w-[90%] rounded-2xl px-3 py-2.5 text-sm shadow-sm border rounded-bl-none ${msg.status === 'failed' ? 'bg-destructive/10 border-destructive/50 text-destructive' : 'bg-muted border-border text-foreground'}`}>
                    {msg.status === 'processing' ? (
                      <span className="flex items-center gap-1.5 px-2 py-1">
                        <span className="h-2 w-2 rounded-full bg-primary/60 animate-bounce" style={{ animationDelay: '0ms' }} />
                        <span className="h-2 w-2 rounded-full bg-primary/60 animate-bounce" style={{ animationDelay: '150ms' }} />
                        <span className="h-2 w-2 rounded-full bg-primary/60 animate-bounce" style={{ animationDelay: '300ms' }} />
                      </span>
                    ) : (
                      <div className="text-sm">
                        {/<[a-z][\s\S]*>/i.test(msg.message || '') ? (
                          <div className="llm-content" dangerouslySetInnerHTML={{ __html: msg.message || '' }} />
                        ) : (
                          <div className="whitespace-pre-wrap">{msg.message}</div>
                        )}
                      </div>
                    )}
                  </div>
                </div>
              </div>
            ))}
            </>
           );
          })()}
          </div>
        </div>

        {/* Sticky Input Area */}
        <div className="border-t border-border bg-background p-4 shadow-[0_-10px_20px_-10px_rgba(0,0,0,0.5)]">
          <form onSubmit={handleSend} className="flex items-end gap-3">
            <textarea
              value={draftInput}
              onChange={(e) => setDraftInput(e.target.value)}
              onKeyDown={(e) => {
                if (e.key === 'Enter' && !e.shiftKey) {
                  e.preventDefault();
                  handleSend(e as unknown as React.FormEvent);
                }
              }}
              placeholder="Ask me anything..."
              className="max-h-32 min-h-[52px] w-full resize-none rounded-xl border border-input bg-card px-4 py-3 text-sm ring-offset-background placeholder:text-muted-foreground focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring disabled:cursor-not-allowed disabled:opacity-50"
              rows={1}
            />
            <button
              type="submit"
              disabled={!draftInput.trim()}
              className="flex h-[52px] w-[52px] shrink-0 items-center justify-center rounded-xl bg-primary text-primary-foreground transition-all hover:bg-primary/90 hover:scale-105 active:scale-95 disabled:opacity-50 disabled:pointer-events-none disabled:hover:scale-100"
            >
              <Send className="h-5 w-5" />
            </button>
          </form>
        </div>
      </div>
    </>
  );
}
