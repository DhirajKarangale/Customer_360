import type { ReactNode } from 'react';
import { PageWrapper } from './PageWrapper';

interface PolicyLayoutProps {
  title: string;
  effectiveDate?: string;
  children: ReactNode;
}

export function PolicyLayout({ title, effectiveDate, children }: PolicyLayoutProps) {
  const date = effectiveDate || new Date().toLocaleDateString();

  return (
    <PageWrapper className="min-h-screen pb-24 pt-12">
      <div className="container mx-auto px-4 sm:px-6 lg:px-8 max-w-4xl">
        <div className="pb-10 mb-12 border-b border-white/10">
          <h1 className="text-4xl md:text-5xl font-bold tracking-tight text-white mb-4">
            {title}
          </h1>
          <p className="text-lg text-white/50 font-medium">
            Effective Date: {date}
          </p>
        </div>
        <div className="prose prose-invert prose-lg max-w-none prose-headings:text-white prose-headings:font-semibold prose-p:text-white/70 prose-strong:text-white prose-a:text-indigo-400 hover:prose-a:text-indigo-300">
          {children}
        </div>
      </div>
    </PageWrapper>
  );
}
