import { Suspense, lazy } from 'react';
import { BrowserRouter, Routes, Route } from 'react-router-dom';
import { AppLayout } from './components/layout/AppLayout';
import { ProtectedRoute } from './components/auth/ProtectedRoute';
import { PublicLayout } from './components/layout/PublicLayout';
import { GlobalLoader } from './components/ui/GlobalLoader';
import { GlobalToast } from './components/ui/GlobalToast';
import { LoadingState } from './components/ui/StateFeedback';
import SetBG from './backgrounds/SetBG';


const Customer360Page = lazy(() => import('./pages/Customer360Page'));
const PoliciesPage = lazy(() => import('./pages/PoliciesPage'));
const CustomersPage = lazy(() => import('./pages/CustomersPage'));
const AboutPage = lazy(() => import('./pages/AboutPage'));
const ProfilePage = lazy(() => import('./pages/ProfilePage'));
const LoginPage = lazy(() => import('./pages/LoginPage'));
const NotFoundPage = lazy(() => import('./pages/NotFoundPage'));
const MaintenancePage = lazy(() => import('./pages/MaintenancePage'));
const PrivacyPage = lazy(() => import('./pages/PrivacyPage'));
const TermsPage = lazy(() => import('./pages/TermsPage'));
const CookiesPage = lazy(() => import('./pages/CookiesPage'));


const PageFallback = () => (
  <div className="flex h-screen w-screen items-center justify-center bg-black">
    <LoadingState message="Loading page..." />
  </div>
);


function App() {
  return (
    <>
      <GlobalLoader />
      <GlobalToast />

      <BrowserRouter>
        <SetBG />
        <Routes>
          <Route path="/login" element={
            <Suspense fallback={<PageFallback />}>
              <LoginPage />
            </Suspense>
          } />
          <Route path="/maintenance" element={
            <Suspense fallback={<PageFallback />}>
              <MaintenancePage />
            </Suspense>
          } />

          <Route element={<PublicLayout />}>
            <Route path="/privacy" element={
              <Suspense fallback={<PageFallback />}>
                <PrivacyPage />
              </Suspense>
            } />
            <Route path="/terms" element={
              <Suspense fallback={<PageFallback />}>
                <TermsPage />
              </Suspense>
            } />
            <Route path="/cookies" element={
              <Suspense fallback={<PageFallback />}>
                <CookiesPage />
              </Suspense>
            } />
          </Route>

          <Route element={<ProtectedRoute />}>
            <Route path="/" element={<AppLayout />}>
              <Route index element={<Customer360Page />} />
              <Route path="policies" element={<PoliciesPage />} />
              <Route path="customers" element={<CustomersPage />} />
              <Route path="about" element={<AboutPage />} />
              <Route path="profile" element={<ProfilePage />} />
            </Route>
          </Route>

          <Route path="*" element={
            <Suspense fallback={<PageFallback />}>
              <NotFoundPage />
            </Suspense>
          } />
        </Routes>
      </BrowserRouter>
    </>
  );
}

export default App;
