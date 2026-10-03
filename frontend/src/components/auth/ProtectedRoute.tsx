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

    if (isLoading) {
      showLoader();
    } else {
      hideLoader();
    }


    return () => hideLoader();
  }, [isLoading, showLoader, hideLoader]);


  useEffect(() => {
    if (data) {
      setAgent(data);
    }
  }, [data, setAgent]);


  if (!token) {
    return <Navigate to="/login" replace />;
  }


  if (isError) {
    abortAllRequests();
    TokenService.removeToken();
    setAgent(null);
    return <Navigate to="/login" replace />;
  }


  if (isLoading) {
    return null;
  }


  if (data) {
    return <Outlet />;
  }

  return null;
}
