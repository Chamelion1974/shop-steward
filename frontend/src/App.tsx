/**
 * Main App component with routing.
 */
import { useEffect } from 'react';
import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { useAuthStore } from './stores/authStore';
import { UserRole } from './types';

// Pages
import LoginPage from './pages/LoginPage';
import ForgotPasswordPage from './pages/ForgotPasswordPage';
import ResetPasswordPage from './pages/ResetPasswordPage';
import HubMasterDashboard from './pages/HubMasterDashboard';
import HubCapsDashboard from './pages/HubCapsDashboard';
import JobsPage from './pages/JobsPage';
import TasksPage from './pages/TasksPage';
import ModulesPage from './pages/ModulesPage';
import UsersPage from './pages/UsersPage';
import SettingsPage from './pages/SettingsPage';

// Create React Query client
const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      refetchOnWindowFocus: false,
      retry: 1,
    },
  },
});

// Protected route component
interface ProtectedRouteProps {
  children: React.ReactNode;
  allowedRoles?: UserRole[];
}

function ProtectedRoute({ children, allowedRoles }: ProtectedRouteProps) {
  const { isAuthenticated, user, isLoading } = useAuthStore();

  if (isLoading) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-hub-primary"></div>
      </div>
    );
  }

  if (!isAuthenticated) {
    return <Navigate to="/login" replace />;
  }

  if (allowedRoles && user && !allowedRoles.includes(user.role)) {
    return <Navigate to="/" replace />;
  }

  return <>{children}</>;
}

function App() {
  const { loadUser, isAuthenticated, user } = useAuthStore();

  useEffect(() => {
    loadUser();
  }, []);

  return (
    <QueryClientProvider client={queryClient}>
      <BrowserRouter>
        <Routes>
          {/* Public routes */}
          <Route path="/login" element={<LoginPage />} />
          <Route path="/forgot-password" element={<ForgotPasswordPage />} />
          <Route path="/reset-password" element={<ResetPasswordPage />} />

          {/* Protected routes */}
          <Route
            path="/"
            element={
              <ProtectedRoute>
                {user?.role === UserRole.HUB_MASTER ? (
                  <Navigate to="/hub-master" replace />
                ) : (
                  <Navigate to="/hub-caps" replace />
                )}
              </ProtectedRoute>
            }
          />

          <Route
            path="/hub-master"
            element={
              <ProtectedRoute allowedRoles={[UserRole.HUB_MASTER]}>
                <HubMasterDashboard />
              </ProtectedRoute>
            }
          />

          <Route
            path="/hub-caps"
            element={
              <ProtectedRoute allowedRoles={[UserRole.HUB_CAP]}>
                <HubCapsDashboard />
              </ProtectedRoute>
            }
          />

          <Route
            path="/jobs"
            element={
              <ProtectedRoute>
                <JobsPage />
              </ProtectedRoute>
            }
          />

          <Route
            path="/tasks"
            element={
              <ProtectedRoute>
                <TasksPage />
              </ProtectedRoute>
            }
          />

          <Route
            path="/modules"
            element={
              <ProtectedRoute allowedRoles={[UserRole.HUB_MASTER]}>
                <ModulesPage />
              </ProtectedRoute>
            }
          />

          <Route
            path="/users"
            element={
              <ProtectedRoute allowedRoles={[UserRole.HUB_MASTER]}>
                <UsersPage />
              </ProtectedRoute>
            }
          />

          <Route
            path="/settings"
            element={
              <ProtectedRoute>
                <SettingsPage />
              </ProtectedRoute>
            }
          />

          {/* Catch all */}
          <Route path="*" element={<Navigate to="/" replace />} />
        </Routes>
      </BrowserRouter>
    </QueryClientProvider>
  );
}

export default App;
