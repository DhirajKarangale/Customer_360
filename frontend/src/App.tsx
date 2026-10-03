import { BrowserRouter, Routes, Route } from 'react-router-dom';
import { AppLayout } from './components/layout/AppLayout';
import { ProtectedRoute } from './components/auth/ProtectedRoute';
import Customer360Page from './pages/Customer360Page';
import PoliciesPage from './pages/PoliciesPage';
import CustomersPage from './pages/CustomersPage';
import AboutPage from './pages/AboutPage';
import ProfilePage from './pages/ProfilePage';
import LoginPage from './pages/LoginPage';
import NotFoundPage from './pages/NotFoundPage';
import MaintenancePage from './pages/MaintenancePage';
import { GlobalLoader } from './components/ui/GlobalLoader';
import { GlobalToast } from './components/ui/GlobalToast';
import { PublicLayout } from './components/layout/PublicLayout';
import PrivacyPage from './pages/PrivacyPage';
import TermsPage from './pages/TermsPage';
import CookiesPage from './pages/CookiesPage';
import SetBG from './backgrounds/SetBG';

function App() {
  return (
    <>
      <GlobalLoader />
      <GlobalToast />
      
      <BrowserRouter>
        <SetBG />
        <Routes>
          {/* Standalone Public Pages */}
          <Route path="/login" element={<LoginPage />} />
          <Route path="/maintenance" element={<MaintenancePage />} />

          {/* Public Layout Pages */}
          <Route element={<PublicLayout />}>
            <Route path="/privacy" element={<PrivacyPage />} />
            <Route path="/terms" element={<TermsPage />} />
            <Route path="/cookies" element={<CookiesPage />} />
          </Route>
          
          {/* Protected Routes (Require JWT) */}
          <Route element={<ProtectedRoute />}>
            <Route path="/" element={<AppLayout />}>
              <Route index element={<Customer360Page />} />
              <Route path="policies" element={<PoliciesPage />} />
              <Route path="customers" element={<CustomersPage />} />
              <Route path="about" element={<AboutPage />} />
              <Route path="profile" element={<ProfilePage />} />
            </Route>
          </Route>

          {/* Catch-all 404 Page */}
          <Route path="*" element={<NotFoundPage />} />
        </Routes>
      </BrowserRouter>
    </>
  );
}

export default App;
