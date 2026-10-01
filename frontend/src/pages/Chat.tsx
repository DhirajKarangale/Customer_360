import React from 'react';
import ChatAgent from '@/components/ChatAgent';
import { ArrowLeft } from 'lucide-react';
import { useNavigate } from 'react-router-dom';
import { Button } from '@/components/ui/button';

export default function Chat() {
  const navigate = useNavigate();

  return (
    <div className="flex flex-col h-full flex-1 max-w-5xl mx-auto w-full p-4 md:p-6">
      <div className="flex items-center gap-4 mb-6">
        <Button variant="ghost" size="icon" onClick={() => navigate(-1)}>
          <ArrowLeft className="h-5 w-5" />
        </Button>
        <div>
          <h1 className="text-2xl font-bold tracking-tight">Cortex AI Assistant</h1>
          <p className="text-muted-foreground">Chat with the agent to analyze customer data</p>
        </div>
      </div>
      <div className="flex-1 min-h-[600px]">
        <ChatAgent />
      </div>
    </div>
  );
}
