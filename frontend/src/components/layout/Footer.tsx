export function Footer() {
  return (
    <footer className="border-t border-white/10 bg-transparent py-6">
      <div className="container mx-auto flex flex-col items-center justify-center gap-4 px-4 text-center">
        <p className="text-sm text-white/70">
          &copy; {new Date().getFullYear()} Customer 360 AI Platform. All rights reserved.
        </p>
      </div>
    </footer>
  );
}
