import React from 'react';
import { Loader2 } from 'lucide-react';

interface LoadingStateProps {
  message: string;
  className?: string;
}

export function LoadingState({ message, className = "p-12" }: LoadingStateProps) {
  return (
    <div className={`flex flex-col items-center justify-center text-white/70 ${className}`}>
      <Loader2 className="h-8 w-8 animate-spin text-primary mb-4" />
      <p>{message}</p>
    </div>
  );
}

interface EmptyStateProps {
  icon: React.ElementType;
  title: string;
  description?: string;
  className?: string;
}

export function EmptyState({ icon: Icon, title, description, className = "p-12" }: EmptyStateProps) {
  return (
    <div className={`flex flex-col items-center justify-center text-white/70 ${className}`}>
      <Icon className="h-12 w-12 text-white/40 mb-4 opacity-50" />
      <p className="text-lg font-medium text-white">{title}</p>
      {description && <p className="text-sm">{description}</p>}
    </div>
  );
}
