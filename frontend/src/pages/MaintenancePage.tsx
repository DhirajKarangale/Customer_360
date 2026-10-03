import { ServerCrash, Wrench, Sparkles } from 'lucide-react';

export default function MaintenancePage() {
  return (
    <div className="relative flex min-h-screen flex-col items-center justify-center overflow-hidden bg-transparent p-4 text-center">
      
      {/* Background ambient glows */}
      <div className="absolute top-0 right-0 h-[600px] w-[600px] rounded-full bg-indigo-600/20 blur-[130px] pointer-events-none mix-blend-screen" />
      <div className="absolute bottom-0 left-0 h-[500px] w-[500px] rounded-full bg-blue-600/20 blur-[100px] pointer-events-none mix-blend-screen animate-pulse" />
      
      <div className="relative z-10 flex flex-col items-center animate-in fade-in slide-in-from-bottom-10 duration-1000">
        
        <div className="relative mb-10">
          <div className="absolute -inset-8 rounded-full bg-gradient-to-r from-blue-500 via-indigo-500 to-purple-500 opacity-20 blur-2xl animate-spin-slow"></div>
          <div className="relative flex h-32 w-32 items-center justify-center rounded-3xl bg-white/5 shadow-[0_8px_32px_0_rgba(0,0,0,0.36)] border border-white/5 backdrop-blur-xl shadow-2xl rotate-3 transition-transform hover:rotate-0 duration-500">
            <ServerCrash className="h-16 w-16 text-indigo-400" />
            <Wrench className="absolute -bottom-4 -right-4 h-12 w-12 text-blue-400 bg-black rounded-full p-2 border border-white/5" />
          </div>
        </div>
        
        <h1 className="text-4xl md:text-5xl font-extrabold tracking-tight text-transparent bg-clip-text bg-gradient-to-r from-blue-200 via-indigo-200 to-purple-200 drop-shadow-lg mb-6">
          System Under Maintenance
        </h1>
        
        <div className="max-w-lg rounded-2xl bg-black/20 border border-white/5 p-6 backdrop-blur-md shadow-xl">
          <p className="text-lg text-gray-300 leading-relaxed mb-4">
            We are currently experiencing server issues or performing scheduled upgrades to improve your experience. 
          </p>
          <div className="inline-flex items-center gap-2 bg-indigo-500/20 px-4 py-2 rounded-full border border-indigo-500/30">
            <Sparkles className="h-4 w-4 text-indigo-400 animate-pulse" />
            <p className="text-sm font-medium text-indigo-200">
              Our engineers are on it. Please check back soon.
            </p>
          </div>
        </div>
        
      </div>
    </div>
  );
}
