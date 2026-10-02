import { ServerCrash } from 'lucide-react';

export default function MaintenancePage() {
  return (
    <div className="flex min-h-screen flex-col items-center justify-center bg-background p-4 text-foreground text-center">
      <div className="rounded-full bg-destructive/20 p-4">
        <ServerCrash className="h-12 w-12 text-destructive" />
      </div>
      <h1 className="mt-6 text-4xl font-bold tracking-tight">System Under Maintenance</h1>
      <p className="mt-4 max-w-md text-muted-foreground">
        We are currently experiencing server issues or performing scheduled upgrades. Our engineers are on it.
      </p>
      <p className="mt-2 text-sm font-medium text-primary">
        Please check back soon.
      </p>
    </div>
  );
}
