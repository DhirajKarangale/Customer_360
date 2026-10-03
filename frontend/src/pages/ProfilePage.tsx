import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuthStore } from '../store/useAuthStore';
import { TokenService } from '../api/tokenService';
import { useUIStore } from '../store/useUIStore';
import { LogOut, User, Mail, Phone, Building2, FileCheck, Shield } from 'lucide-react';
import { useQueryClient } from '@tanstack/react-query';
import { useAIChatStore } from '../store/useAIChatStore';
import { abortAllRequests } from '../api/axios';

export default function ProfilePage() {
  const [imgError, setImgError] = useState(false);
  const agent = useAuthStore((state) => state.agent);
  const setAgent = useAuthStore((state) => state.setAgent);
  const { showToast } = useUIStore();
  const navigate = useNavigate();
  const queryClient = useQueryClient();

  const handleCopy = (text: string, label: string) => {
    navigator.clipboard.writeText(text);
    showToast(`${label} copied to clipboard!`, 'text-emerald-400', 3000);
  };

  const handleSignOut = () => {
    abortAllRequests();
    TokenService.removeToken();
    setAgent(null);
    useAIChatStore.getState().clearMessages(undefined, true);
    queryClient.clear();
    showToast('Signed out successfully.', 'text-emerald-400');
    navigate('/login');
  };

  if (!agent) {
    return null;
  }

  return (
    <div className="relative min-h-[80vh] w-full overflow-hidden rounded-2xl bg-black/40 backdrop-blur-xl border border-white/10 shadow-2xl p-8 shadow-2xl border border-white/5">


      <div className="absolute top-0 right-1/4 h-[500px] w-[500px] rounded-full bg-blue-600/20 blur-[120px] pointer-events-none mix-blend-screen" />
      <div className="absolute bottom-0 left-1/4 h-[400px] w-[400px] rounded-full bg-purple-600/20 blur-[100px] pointer-events-none mix-blend-screen" />

      <div className="relative z-10 mx-auto max-w-5xl space-y-8">


        <div className="flex flex-col gap-4 rounded-2xl border border-white/5 bg-black/20 p-6 backdrop-blur-md shadow-lg md:flex-row md:items-center md:justify-between transition-all duration-300 hover:bg-white/[0.08]">
          <div className="flex items-center gap-3">
            <div className="rounded-xl bg-blue-500/20 p-3 text-blue-400 border border-blue-500/30">
              <User className="h-6 w-6" />
            </div>
            <div>
              <h1 className="text-2xl font-bold tracking-tight text-white">Agent Profile</h1>
              <p className="text-sm text-blue-200/70">Manage your account settings and details</p>
            </div>
          </div>

          <button
            onClick={handleSignOut}
            className="group relative inline-flex h-11 items-center justify-center gap-2 rounded-xl bg-red-500/10 px-6 py-2 text-sm font-medium text-red-400 transition-all hover:bg-red-500 hover:text-white border border-red-500/20 hover:border-red-500 hover:shadow-[0_0_20px_rgba(239,68,68,0.4)]"
          >
            <LogOut className="h-4 w-4 transition-transform group-hover:-translate-x-1" />
            Sign Out
          </button>
        </div>


        <div className="rounded-2xl border border-white/5 bg-black/20 shadow-xl p-8 backdrop-blur-md">
          <div className="flex flex-col md:flex-row items-center gap-8 mb-12">
            <div className="relative group">
              <div className="absolute -inset-1 rounded-full bg-gradient-to-r from-blue-500 via-purple-500 to-pink-500 opacity-50 blur transition duration-500 group-hover:opacity-100 group-hover:duration-200"></div>
              <div className="relative flex h-32 w-32 items-center justify-center overflow-hidden rounded-full bg-white/5 shadow-[0_8px_32px_0_rgba(0,0,0,0.36)] border-2 border-white/10 p-1 backdrop-blur-md">
                {!imgError && agent.profile_image_url ? (
                  <img 
                    src={agent.profile_image_url} 
                    alt={agent.name} 
                    className="h-full w-full rounded-full object-cover object-top"
                    onError={() => setImgError(true)}
                  />
                ) : (
                  <div className="flex h-full w-full items-center justify-center rounded-full bg-blue-500/10 text-blue-400">
                    <User className="h-14 w-14" />
                  </div>
                )}
              </div>
            </div>

            <div className="text-center md:text-left space-y-2">
              <h2 className="text-4xl font-extrabold tracking-tight text-transparent bg-clip-text bg-gradient-to-r from-blue-300 via-white to-purple-300">
                {agent.name}
              </h2>
              <div className="flex items-center justify-center md:justify-start gap-2 text-sm font-medium text-blue-200/70 bg-blue-500/10 w-fit px-3 py-1.5 rounded-full mx-auto md:mx-0 border border-blue-500/20">
                <Shield className="h-4 w-4 text-blue-400" />
                ID: <span className="font-mono">{agent.id}</span>
              </div>
            </div>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">

            <button 
              onClick={() => handleCopy(agent.email, 'Email Address')}
              className="group flex w-full text-left cursor-pointer items-center gap-5 rounded-2xl border border-white/5 bg-black/20 shadow-[0_8px_32px_0_rgba(0,0,0,0.36)] p-6 transition-all duration-300 hover:bg-white/5 hover:border-white/10 hover:-translate-y-1"
            >
              <div className="rounded-xl bg-blue-500/10 p-3.5 text-blue-400 transition-colors group-hover:bg-blue-500/20 group-hover:text-blue-300">
                <Mail className="h-6 w-6" />
              </div>
              <div>
                <p className="text-sm text-gray-400 font-medium mb-1">Email Address</p>
                <p className="text-lg font-semibold text-gray-100">{agent.email}</p>
              </div>
            </button>

            <button 
              onClick={() => handleCopy(agent.phone_number, 'Phone Number')}
              className="group flex w-full text-left cursor-pointer items-center gap-5 rounded-2xl border border-white/5 bg-black/20 shadow-[0_8px_32px_0_rgba(0,0,0,0.36)] p-6 transition-all duration-300 hover:bg-white/5 hover:border-white/10 hover:-translate-y-1"
            >
              <div className="rounded-xl bg-emerald-500/10 p-3.5 text-emerald-400 transition-colors group-hover:bg-emerald-500/20 group-hover:text-emerald-300">
                <Phone className="h-6 w-6" />
              </div>
              <div>
                <p className="text-sm text-gray-400 font-medium mb-1">Phone Number</p>
                <p className="text-lg font-mono font-semibold text-gray-100">{agent.phone_number}</p>
              </div>
            </button>

            <button 
              onClick={() => handleCopy(agent.agency_name, 'Agency Name')}
              className="group flex w-full text-left cursor-pointer items-center gap-5 rounded-2xl border border-white/5 bg-black/20 shadow-[0_8px_32px_0_rgba(0,0,0,0.36)] p-6 transition-all duration-300 hover:bg-white/5 hover:border-white/10 hover:-translate-y-1"
            >
              <div className="rounded-xl bg-purple-500/10 p-3.5 text-purple-400 transition-colors group-hover:bg-purple-500/20 group-hover:text-purple-300">
                <Building2 className="h-6 w-6" />
              </div>
              <div>
                <p className="text-sm text-gray-400 font-medium mb-1">Agency Name</p>
                <p className="text-lg font-semibold text-gray-100">{agent.agency_name}</p>
              </div>
            </button>

            <button 
              onClick={() => handleCopy(agent.license_number, 'License Number')}
              className="group flex w-full text-left cursor-pointer items-center gap-5 rounded-2xl border border-white/5 bg-black/20 shadow-[0_8px_32px_0_rgba(0,0,0,0.36)] p-6 transition-all duration-300 hover:bg-white/5 hover:border-white/10 hover:-translate-y-1"
            >
              <div className="rounded-xl bg-amber-500/10 p-3.5 text-amber-400 transition-colors group-hover:bg-amber-500/20 group-hover:text-amber-300">
                <FileCheck className="h-6 w-6" />
              </div>
              <div>
                <p className="text-sm text-gray-400 font-medium mb-1">License Number</p>
                <p className="text-lg font-mono font-semibold text-gray-100">{agent.license_number}</p>
              </div>
            </button>

          </div>
        </div>
      </div>
    </div>
  );
}
