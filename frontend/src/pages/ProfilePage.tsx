import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuthStore } from '../store/useAuthStore';
import { TokenService } from '../api/tokenService';
import { useUIStore } from '../store/useUIStore';
import { LogOut, User, Mail, Phone, Building2, FileCheck, Hash } from 'lucide-react';
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

  const handleSignOut = () => {
    abortAllRequests();
    TokenService.removeToken();
    setAgent(null);
    useAIChatStore.getState().clearMessages(undefined, true);
    queryClient.clear(); // Clear all cached API queries
    showToast('Signed out successfully.', 'text-green-500');
    navigate('/login');
  };

  if (!agent) {
    return null; // or loading
  }

  return (
    <div className="space-y-6">
      {/* Page Header */}
      <div className="flex flex-col gap-4 rounded-xl border border-border bg-card p-4 shadow-sm md:flex-row md:items-center md:justify-between">
        <div className="flex items-center gap-2">
          <div className="rounded-lg bg-primary/10 p-2 text-primary">
            <User className="h-6 w-6" />
          </div>
          <h1 className="text-xl font-semibold tracking-tight">Agent Profile</h1>
        </div>
        
        <button
          onClick={handleSignOut}
          className="inline-flex h-10 items-center justify-center gap-2 rounded-md bg-destructive/10 px-4 py-2 text-sm font-medium text-destructive transition-colors hover:bg-destructive hover:text-white focus-visible:outline-none focus-visible:ring-1 focus-visible:ring-destructive"
        >
          <LogOut className="h-4 w-4" />
          Sign Out
        </button>
      </div>

      {/* Main Content Area */}
      <div className="rounded-xl border border-border bg-card shadow-sm p-8">
        <div className="flex flex-col md:flex-row items-center gap-8 mb-10">
          {!imgError && agent.profile_image_url ? (
            <img 
              src={agent.profile_image_url} 
              alt={agent.name} 
              className="h-32 w-32 rounded-full object-contain bg-white border-4 border-background shadow-lg"
              onError={() => setImgError(true)}
            />
          ) : (
            <div className="flex h-32 w-32 items-center justify-center rounded-full bg-primary/10 border-4 border-background shadow-lg">
              <User className="h-16 w-16 text-primary/50" />
            </div>
          )}
          
          <div className="text-center md:text-left space-y-1">
            <h2 className="text-3xl font-bold tracking-tight text-foreground">{agent.name}</h2>
            <p className="text-sm font-medium text-muted-foreground truncate" title={agent.id}>
              ID: {agent.id}
            </p>
          </div>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          <div className="flex items-center gap-4 rounded-xl border border-border/50 bg-muted/30 p-5 transition-colors hover:bg-muted/50">
            <div className="rounded-full bg-primary/10 p-3 text-primary">
              <Mail className="h-6 w-6" />
            </div>
            <div>
              <p className="text-sm text-muted-foreground font-medium">Email Address</p>
              <p className="text-base font-semibold text-foreground mt-0.5">{agent.email}</p>
            </div>
          </div>
          
          <div className="flex items-center gap-4 rounded-xl border border-border/50 bg-muted/30 p-5 transition-colors hover:bg-muted/50">
            <div className="rounded-full bg-primary/10 p-3 text-primary">
              <Phone className="h-6 w-6" />
            </div>
            <div>
              <p className="text-sm text-muted-foreground font-medium">Phone Number</p>
              <p className="text-base font-semibold text-foreground mt-0.5">{agent.phone_number}</p>
            </div>
          </div>

          <div className="flex items-center gap-4 rounded-xl border border-border/50 bg-muted/30 p-5 transition-colors hover:bg-muted/50">
            <div className="rounded-full bg-primary/10 p-3 text-primary">
              <Building2 className="h-6 w-6" />
            </div>
            <div>
              <p className="text-sm text-muted-foreground font-medium">Agency Name</p>
              <p className="text-base font-semibold text-foreground mt-0.5">{agent.agency_name}</p>
            </div>
          </div>

          <div className="flex items-center gap-4 rounded-xl border border-border/50 bg-muted/30 p-5 transition-colors hover:bg-muted/50">
            <div className="rounded-full bg-primary/10 p-3 text-primary">
              <FileCheck className="h-6 w-6" />
            </div>
            <div>
              <p className="text-sm text-muted-foreground font-medium">License Number</p>
              <p className="text-base font-semibold text-foreground mt-0.5">{agent.license_number}</p>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
