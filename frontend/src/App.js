import React from 'react';
import { BrowserRouter, Routes, Route, Navigate, useLocation } from 'react-router-dom';
import { AuthProvider, useAuth } from './context/AuthContext';
import { Toaster } from './components/ui/sonner';
import LoginPage from './pages/LoginPage';
import ServiceOrdersPage from './pages/ServiceOrdersPage';
import InventoryPage from './pages/InventoryPage';
import FinancialPage from './pages/FinancialPage';
import RoutesPage from './pages/RoutesPage';
import ManuaisPage from './pages/ManuaisPage';
import WhatsAppConfigPage from './pages/WhatsAppConfigPage';
import UsersPage from './pages/UsersPage';
import WebhooksAdminPage from './pages/WebhooksAdminPage';
import PublicTrackingPage from './pages/PublicTrackingPage';
import OSQrRedirectPage from './pages/OSQrRedirectPage';
import OSPublicViewPage from './pages/OSPublicViewPage';
import ProductPublicViewPage from './pages/ProductPublicViewPage';
import LabelTemplatesPage from './pages/LabelTemplatesPage';
import PublicSignPage from './pages/PublicSignPage';
import './App.css';

const ProtectedRoute = ({ children, adminOnly = false, allowedRoles = null }) => {
  const { user, loading } = useAuth();

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-gray-50">
        <div className="w-8 h-8 border-2 border-gray-900 border-t-transparent rounded-full animate-spin" />
      </div>
    );
  }

  if (!user) {
    return <Navigate to="/login" replace />;
  }

  // Invisacook role has its own landing page (/service-orders) — never
  // exposed to any other authenticated route. This is enforced regardless of
  // adminOnly / allowedRoles so a URL-typed path can't leak features.
  if (user.role === 'invisacook') {
    if (allowedRoles && allowedRoles.includes('invisacook')) {
      return children;
    }
    return <Navigate to="/service-orders" replace />;
  }

  // Technicians may only access /routes and /manuais
  if (adminOnly && user.role !== 'admin') {
    return <Navigate to="/routes" replace />;
  }

  return children;
};

const PublicRoute = ({ children }) => {
  const { user, loading } = useAuth();
  const location = useLocation();

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-gray-50">
        <div className="w-8 h-8 border-2 border-gray-900 border-t-transparent rounded-full animate-spin" />
      </div>
    );
  }

  if (user) {
    // Honor ?redirect=/path that the OS QR redirect (or other deep-links) may
    // have set when forcing the user through /login. Only relative paths are
    // accepted to prevent open-redirect to external hosts.
    const params = new URLSearchParams(location.search);
    const redirect = params.get('redirect');
    if (redirect && redirect.startsWith('/')) {
      return <Navigate to={redirect} replace />;
    }
    const dest = user.role === 'technician' ? '/routes' : '/service-orders';
    return <Navigate to={dest} replace />;
  }

  return children;
};

function AppRoutes() {
  const { user } = useAuth();
  const defaultDest = user?.role === 'technician' ? '/routes' : '/service-orders';
  return (
    <Routes>
      <Route 
        path="/login" 
        element={
          <PublicRoute>
            <LoginPage />
          </PublicRoute>
        } 
      />
      <Route path="/track/:token" element={<PublicTrackingPage />} />
      <Route path="/sign/:token" element={<PublicSignPage />} />
      <Route path="/os/:osNumber" element={<OSQrRedirectPage />} />
      {/* Short QR route — encoded as alphanumeric in thermal-label QR codes
          so the QR is Version 2 (25×25) instead of Version 3 (29×29).
          ~30% bigger modules at the same physical 22mm → much more legible
          when scanning the printed adesivo with a phone camera. */}
      <Route path="/o/:osNumber" element={<OSQrRedirectPage />} />
      <Route path="/os-view/:osNumber" element={<OSPublicViewPage />} />
      {/* Public product view — opened from inventory QR labels.
          Short path /p/:code is used in the QR (alphanumeric, smaller). */}
      <Route path="/p/:code" element={<ProductPublicViewPage />} />
      <Route path="/produto/:code" element={<ProductPublicViewPage />} />
      <Route 
        path="/service-orders" 
        element={
          <ProtectedRoute adminOnly allowedRoles={['admin', 'invisacook']}>
            <ServiceOrdersPage />
          </ProtectedRoute>
        } 
      />
      <Route 
        path="/inventory" 
        element={
          <ProtectedRoute adminOnly>
            <InventoryPage />
          </ProtectedRoute>
        } 
      />
      <Route 
        path="/financial" 
        element={
          <ProtectedRoute adminOnly>
            <FinancialPage />
          </ProtectedRoute>
        } 
      />
      <Route 
        path="/routes" 
        element={
          <ProtectedRoute>
            <RoutesPage />
          </ProtectedRoute>
        } 
      />
      <Route 
        path="/manuais" 
        element={
          <ProtectedRoute>
            <ManuaisPage />
          </ProtectedRoute>
        } 
      />
      <Route 
        path="/whatsapp" 
        element={
          <ProtectedRoute adminOnly>
            <WhatsAppConfigPage />
          </ProtectedRoute>
        } 
      />
      <Route 
        path="/users" 
        element={
          <ProtectedRoute adminOnly>
            <UsersPage />
          </ProtectedRoute>
        } 
      />
      <Route 
        path="/admin/webhooks" 
        element={
          <ProtectedRoute adminOnly>
            <WebhooksAdminPage />
          </ProtectedRoute>
        } 
      />
      <Route 
        path="/admin/labels" 
        element={
          <ProtectedRoute adminOnly>
            <LabelTemplatesPage />
          </ProtectedRoute>
        } 
      />
      <Route path="/" element={<Navigate to={defaultDest} replace />} />
      <Route path="*" element={<Navigate to={defaultDest} replace />} />
    </Routes>
  );
}

function App() {
  return (
    <BrowserRouter>
      <AuthProvider>
        <AppRoutes />
        <Toaster position="top-right" richColors />
      </AuthProvider>
    </BrowserRouter>
  );
}

export default App;
