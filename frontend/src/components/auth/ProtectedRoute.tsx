import { useEffect } from 'react';
import { Navigate, Outlet } from 'react-router-dom';
import { TokenService } from '../../api/tokenService';
import { useVerifyTokenQuery } from '../../api/auth';
import { useUIStore } from '../../store/useUIStore';
import { useAuthStore } from '../../store/useAuthStore';
import { abortAllRequests } from '../../api/axios';

export function ProtectedRoute() {
  const token = TokenService.getToken();
  const { data, isLoading, isError } = useVerifyTokenQuery();
  const { showLoader, hideLoader } = useUIStore();
  const setAgent = useAuthStore((state) => state.setAgent);

  useEffect(() => {
    // Show loader while verifying token
    if (isLoading) {
      showLoader();
    } else {
      hideLoader();
    }
    
    // Cleanup on unmount
    return () => hideLoader();
  }, [isLoading, showLoader, hideLoader]);

  // Sync agent data to store when verification succeeds
  useEffect(() => {
    if (data) {
      setAgent(data);
    }
  }, [data, setAgent]);

  // 1. If no token exists at all, instantly redirect to login
  if (!token) {
    return <Navigate to="/login" replace />;
  }

  // 2. If verification fails (e.g. expired or invalid), clear the dead token and redirect
  if (isError) {
    abortAllRequests();
    TokenService.removeToken();
    setAgent(null);
    return <Navigate to="/login" replace />;
  }

  // 3. If currently loading, render nothing (GlobalLoader will cover the screen and block clicks)
  if (isLoading) {
    return null;
  }

  // 4. If we have verified data, render the protected children
  if (data) {
    return <Outlet />;
  }

  return null;
}
