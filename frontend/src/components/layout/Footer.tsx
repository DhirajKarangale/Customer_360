export function Footer() {
  return (
    <footer className="border-t border-border bg-background py-6">
      <div className="container mx-auto flex flex-col items-center justify-center gap-4 px-4 text-center">
        <p className="text-sm text-muted-foreground">
          &copy; {new Date().getFullYear()} Customer 360 AI Platform. All rights reserved.
        </p>
      </div>
    </footer>
  );
}
