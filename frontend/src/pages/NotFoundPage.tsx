import { AlertTriangle, Home, Sparkles } from 'lucide-react';
import { Link } from 'react-router-dom';

export default function NotFoundPage() {
  return (
    <div className="relative flex min-h-screen flex-col items-center justify-center overflow-hidden bg-transparent p-4 text-center">


      <div className="absolute top-1/4 left-1/4 h-[500px] w-[500px] rounded-full bg-amber-600/20 blur-[120px] pointer-events-none mix-blend-screen animate-pulse" />
      <div className="absolute bottom-1/4 right-1/4 h-[400px] w-[400px] rounded-full bg-red-600/20 blur-[100px] pointer-events-none mix-blend-screen" />

      <div className="relative z-10 flex flex-col items-center animate-in fade-in zoom-in-95 duration-700">
        <div className="relative group mb-8">
          <div className="absolute -inset-4 rounded-full bg-gradient-to-r from-amber-500 to-red-500 opacity-30 blur-xl transition duration-500 group-hover:opacity-60"></div>
          <div className="relative flex h-24 w-24 items-center justify-center rounded-full bg-black/50 border border-amber-500/30 backdrop-blur-md shadow-2xl">
            <AlertTriangle className="h-12 w-12 text-amber-400" />
          </div>
        </div>

        <h1 className="text-6xl md:text-8xl font-extrabold tracking-tight text-transparent bg-clip-text bg-gradient-to-b from-white to-gray-500 drop-shadow-sm mb-4">
          404
        </h1>
        <h2 className="text-2xl md:text-3xl font-bold tracking-tight text-gray-200 mb-6">
          Page Not Found
        </h2>

        <p className="max-w-md text-lg text-gray-400 mb-10 leading-relaxed">
          Oops! The page you are looking for doesn't exist, has been moved, or is temporarily unavailable.
        </p>

        <Link to="/">
          <button className="group relative inline-flex h-14 items-center justify-center gap-3 rounded-xl bg-white px-8 py-3 text-base font-bold text-black transition-all hover:bg-gray-200 hover:scale-105 hover:shadow-[0_0_30px_rgba(255,255,255,0.3)]">
            <Home className="h-5 w-5 transition-transform group-hover:-translate-y-0.5" />
            Back to Dashboard
            <Sparkles className="absolute right-3 top-3 h-3 w-3 opacity-0 group-hover:opacity-100 transition-opacity text-amber-500" />
          </button>
        </Link>
      </div>
    </div>
  );
}
