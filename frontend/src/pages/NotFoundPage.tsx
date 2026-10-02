import { AlertTriangle, Home } from 'lucide-react';
import { Link } from 'react-router-dom';

export default function NotFoundPage() {
  return (
    <div className="flex min-h-screen flex-col items-center justify-center bg-background p-4 text-foreground text-center">
      <div className="rounded-full bg-muted p-4">
        <AlertTriangle className="h-12 w-12 text-muted-foreground" />
      </div>
      <h1 className="mt-6 text-4xl font-bold tracking-tight">404 - Page Not Found</h1>
      <p className="mt-4 max-w-md text-muted-foreground">
        Oops! The page you are looking for doesn't exist or has been moved.
      </p>
      
      <Link to="/" className="mt-8">
        <button className="inline-flex h-10 items-center justify-center gap-2 rounded-md bg-primary px-6 py-2 text-sm font-medium text-primary-foreground transition-colors hover:bg-primary/90">
          <Home className="h-4 w-4" />
          Back to Dashboard
        </button>
      </Link>
    </div>
  );
}
