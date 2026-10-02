import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuthStore } from '../store/useAuthStore';
import { TokenService } from '../api/tokenService';
import { useUIStore } from '../store/useUIStore';
import { LogOut, User, Mail, Phone, Building2, FileCheck } from 'lucide-react';
import { useQueryClient } from '@tanstack/react-query';

export default function ProfilePage() {
  const [imgError, setImgError] = useState(false);
  const agent = useAuthStore((state) => state.agent);
  const setAgent = useAuthStore((state) => state.setAgent);
  const { showToast } = useUIStore();
  const navigate = useNavigate();
  const queryClient = useQueryClient();

  const handleSignOut = () => {
    TokenService.removeToken();
    setAgent(null);
    queryClient.clear(); // Clear all cached API queries
    showToast('Signed out successfully.', 'text-green-500');
    navigate('/login');
  };

  if (!agent) {
    return null; // or loading
  }

  return (
    <div className="flex h-full min-h-[70vh] flex-col items-center py-8 text-foreground">
      <div className="w-full max-w-2xl rounded-2xl border border-border bg-card shadow-lg p-8">
        
        <h1 className="text-3xl font-bold tracking-tight mb-8">Agent Profile</h1>
        
        <div className="flex flex-col md:flex-row items-center gap-8 mb-10">
          {!imgError && agent.profile_image_url ? (
            <img 
              src={agent.profile_image_url} 
              alt={agent.name} 
              className="h-32 w-32 rounded-full object-cover border-4 border-border/50 shadow-md"
              onError={() => setImgError(true)}
            />
          ) : (
            <div className="flex h-32 w-32 items-center justify-center rounded-full bg-muted border-4 border-border/50 shadow-md">
              <User className="h-16 w-16 text-muted-foreground" />
            </div>
          )}
          
          <div className="text-center md:text-left">
            <h2 className="text-2xl font-semibold text-primary">{agent.name}</h2>
            <p className="text-muted-foreground mt-1">Licensed Insurance Agent</p>
          </div>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-6 mb-10">
          <div className="flex items-center gap-3 rounded-lg border border-border/50 bg-background/50 p-4">
            <Mail className="h-5 w-5 text-primary" />
            <div>
              <p className="text-xs text-muted-foreground">Email</p>
              <p className="text-sm font-medium">{agent.email}</p>
            </div>
          </div>
          
          <div className="flex items-center gap-3 rounded-lg border border-border/50 bg-background/50 p-4">
            <Phone className="h-5 w-5 text-primary" />
            <div>
              <p className="text-xs text-muted-foreground">Phone Number</p>
              <p className="text-sm font-medium">{agent.phone_number}</p>
            </div>
          </div>

          <div className="flex items-center gap-3 rounded-lg border border-border/50 bg-background/50 p-4">
            <Building2 className="h-5 w-5 text-primary" />
            <div>
              <p className="text-xs text-muted-foreground">Agency Name</p>
              <p className="text-sm font-medium">{agent.agency_name}</p>
            </div>
          </div>

          <div className="flex items-center gap-3 rounded-lg border border-border/50 bg-background/50 p-4">
            <FileCheck className="h-5 w-5 text-primary" />
            <div>
              <p className="text-xs text-muted-foreground">License Number</p>
              <p className="text-sm font-medium">{agent.license_number}</p>
            </div>
          </div>
        </div>

        <div className="mt-8 border-t border-border pt-8 flex justify-center">
          <button
            onClick={handleSignOut}
            className="flex w-full md:w-auto items-center justify-center gap-2 rounded-md bg-destructive/10 border border-destructive px-8 py-2.5 text-sm font-medium text-destructive transition-colors hover:bg-destructive hover:text-destructive-foreground focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-destructive"
          >
            <LogOut className="h-4 w-4" />
            Sign Out
          </button>
        </div>
      </div>
    </div>
  );
}
