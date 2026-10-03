import { memo, useEffect, useRef, useState } from 'react';
import { ChevronLeft, Send, ArrowUp, ArrowDown, Trash2 } from 'lucide-react';
import { useAIChatStore } from '../../store/useAIChatStore';
import { useAuthStore } from '../../store/useAuthStore';
import { useGenerateChatMutation, clearChatsApi } from '../../api/chat';
import { getRandomMessage } from '../../utils/messages';

export const ChatPanel = memo(function ChatPanel() {
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
  const [isClearing, setIsClearing] = useState(false);

  const scrollRef = useRef<HTMLDivElement>(null);


  useEffect(() => {
    if (isOpen) {
      document.body.style.overflow = 'hidden';

      if (hasUnread) setHasUnread(false);


      setTimeout(scrollToBottom, 100);
    } else {
      document.body.style.overflow = 'unset';
    }
    return () => {
      document.body.style.overflow = 'unset';
    };
  }, [isOpen, hasUnread, setHasUnread]);


  useEffect(() => {
    const interval = setInterval(() => {
      const now = Date.now();
      messages.forEach((msg) => {
        if (msg.status === 'processing') {

          if (now - msg.sendTime > 300000) {
            markAsFailed(msg.job_id);
          }
        }
      });
    }, 10000); 

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


    const jobId = `aichat_${crypto.randomUUID()}`;
    const userQuery = draftInput.trim();


    addMessage(jobId, userQuery, activeCustomerId || undefined, activePolicyId || undefined);
    setDraftInput(''); 

    setTimeout(scrollToBottom, 100);


    generateMutation.mutate({
      job_id: jobId,
      query: userQuery,
      insurance_agents_id: agent.id,
      policies_id: activePolicyId || undefined,
      customers_id: activeCustomerId || undefined,
    }, {
      onError: () => {
        markAsFailed(jobId);
      }
    });
  };

  return (
    <>

      <div 
        className={`fixed inset-0 z-40 bg-transparent/60 backdrop-blur-sm transition-opacity duration-300 ${isOpen ? 'opacity-100' : 'opacity-0 pointer-events-none'}`} 
        onClick={() => setIsOpen(false)}
      />


      <div 
        className={`fixed right-0 top-0 z-50 flex h-screen w-full max-w-md flex-col border-l border-white/5 bg-black/40 backdrop-blur-xl border border-white/10 shadow-2xl transform-gpu will-change-transform transition-transform duration-500 ease-[cubic-bezier(0.32,0.72,0,1)] ${isOpen ? 'translate-x-0' : 'translate-x-full'}`}
      >

        <button
          onClick={togglePanel}
          className={`absolute left-0 top-1/2 flex h-20 w-8 -translate-x-full -translate-y-1/2 items-center justify-center rounded-l-xl border-y border-l border-white/5 bg-black/40 backdrop-blur-xl border border-white/10 shadow-2xl text-white shadow-lg transition-colors duration-300 hover:bg-white/5 text-white ${isOpen ? 'bg-primary border-primary text-primary-foreground hover:bg-primary/90' : ''}`}
          aria-label="Toggle Chat"
        >

          {!isOpen && hasUnread && (
            <span className="absolute -top-1 -left-1 flex h-3 w-3">
              <span className="absolute inline-flex h-full w-full animate-ping rounded-full bg-destructive opacity-75"></span>
              <span className="relative inline-flex h-3 w-3 rounded-full bg-destructive border border-background"></span>
            </span>
          )}


          <span 
            className={`flex items-center justify-center transform-gpu will-change-transform transition-transform duration-500 ease-[cubic-bezier(0.32,0.72,0,1)] ${isOpen ? 'rotate-180' : 'rotate-0'}`}
          >
            <ChevronLeft className="h-6 w-6" />
          </span>
        </button>


        <div className="flex items-center justify-between border-b border-white/5 p-4 bg-transparent/50 backdrop-blur-md">
          <h2 className="text-sm font-semibold text-white flex items-center gap-2">
            {activePolicyNumber ? `Asking about ${activePolicyNumber}` : activeCustomerName ? `Asking about ${activeCustomerName}` : 'AI Assistant'}
          </h2>
          <div className="flex items-center gap-3">
            {(activePolicyNumber || activeCustomerName) && (
              <button 
                onClick={() => {
                  setActivePolicy(null, null);
                  setActiveCustomer(null, null);
                }}
                className="text-xs text-white/70 hover:text-white transition-colors"
              >
                Clear Context
              </button>
            )}
            {(() => {
              const displayMessages = activeCustomerId ? messages.filter(m => m.customer_id === activeCustomerId) : messages;
              return displayMessages.length > 0 && (
                isClearing ? (
                  <div className="flex items-center gap-2 text-xs text-white/70">
                    <span className="flex items-center gap-1">
                      <span className="h-1.5 w-1.5 rounded-full bg-white/70 animate-bounce" style={{ animationDelay: '0ms' }} />
                      <span className="h-1.5 w-1.5 rounded-full bg-white/70 animate-bounce" style={{ animationDelay: '150ms' }} />
                      <span className="h-1.5 w-1.5 rounded-full bg-white/70 animate-bounce" style={{ animationDelay: '300ms' }} />
                    </span>
                    Clearing chat...
                  </div>
                ) : (
                  <button
                    onClick={async () => {
                      try {
                        setIsClearing(true);
                        await clearChatsApi();
                        clearMessages(undefined, true);
                      } catch (e) {
                        console.error("Failed to clear chats", e);
                      } finally {
                        setIsClearing(false);
                      }
                    }}
                    className="text-white/70 hover:text-destructive transition-colors"
                    title="Clear Chat History"
                  >
                    <Trash2 className="h-4 w-4" />
                  </button>
                )
              );
            })()}
          </div>
        </div>


        <div className="relative flex-1 overflow-hidden bg-transparent/20">


          <div className="absolute right-4 top-1/2 -translate-y-1/2 z-10 flex flex-col gap-3">
             <button onClick={scrollToTop} className="rounded-full border border-white/5 bg-black/40 backdrop-blur-xl border border-white/10 shadow-2xl/80 p-2 text-white/70 shadow-sm backdrop-blur-md transition-colors hover:bg-white/5 text-white hover:text-white">
               <ArrowUp className="h-4 w-4" />
             </button>
             <button onClick={scrollToBottom} className="rounded-full border border-white/5 bg-black/40 backdrop-blur-xl border border-white/10 shadow-2xl/80 p-2 text-white/70 shadow-sm backdrop-blur-md transition-colors hover:bg-white/5 text-white hover:text-white">
               <ArrowDown className="h-4 w-4" />
             </button>
          </div>

          <div ref={scrollRef} className="h-full overflow-y-auto p-4 space-y-6 pb-20">
            {(() => {
              const displayMessages = activeCustomerId ? messages.filter(m => m.customer_id === activeCustomerId) : messages;
              return (
                <>
                  {displayMessages.length === 0 && (
                    <div className="flex h-full items-center justify-center text-center text-sm text-white/70 px-4 whitespace-pre-wrap">
                      {getRandomMessage('chatGreeting')}
                    </div>
                  )}
                  {displayMessages.map((msg) => (
              <div key={msg.job_id} className="space-y-6">

                <div className="flex justify-end">
                  <div className="max-w-[85%] whitespace-pre-wrap rounded-2xl px-4 py-3 text-sm shadow-sm bg-primary text-primary-foreground rounded-br-none">
                    {msg.query}
                  </div>
                </div>


                <div className="flex justify-start">
                  <div className={`max-w-[90%] rounded-2xl px-3 py-2.5 text-sm shadow-sm border rounded-bl-none ${msg.status === 'failed' ? 'bg-destructive/10 border-destructive/50 text-destructive' : 'bg-muted border-white/5 text-white'}`}>
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


        <div className="border-t border-white/5 bg-transparent p-4 shadow-[0_-10px_20px_-10px_rgba(0,0,0,0.5)]">
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
              className="max-h-32 min-h-[52px] w-full resize-none rounded-xl border border-input bg-black/40 backdrop-blur-xl border border-white/10 shadow-2xl px-4 py-3 text-sm ring-offset-background placeholder:text-white/70 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring disabled:cursor-not-allowed disabled:opacity-50"
              rows={1}
            />
            <button
              type="submit"
              disabled={!draftInput.trim()}
              className="flex h-[52px] w-[52px] shrink-0 items-center justify-center rounded-xl bg-primary text-primary-foreground transition-all hover:bg-primary/90 hover:scale-105 active:scale-95 disabled:opacity-50 disabled:hover:scale-100"
            >
              <Send className="h-5 w-5" />
            </button>
          </form>
        </div>
      </div>
    </>
  );
});
