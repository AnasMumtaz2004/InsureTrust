import { Navigate, Outlet } from 'react-router-dom';
import { useAuth } from './AuthContext';

/**
 * Route guard component that wraps route groups.
 * - `allowedRoles`: array of roles allowed to access these routes
 * - Unauthenticated users → redirect to login
 * - Wrong role → redirect to their appropriate dashboard
 */
export const RouteGuard = ({ allowedRoles }) => {
  const { isAuthenticated, role } = useAuth();

  if (!isAuthenticated) {
    return <Navigate to="/login" replace />;
  }

  if (!allowedRoles.includes(role)) {
    // Redirect to appropriate dashboard based on role
    if (role === 'customer') {
      return <Navigate to="/dashboard" replace />;
    }
    if (role === 'staff' || role === 'admin') {
      return <Navigate to="/ops/queue" replace />;
    }
    return <Navigate to="/" replace />;
  }

  return <Outlet />;
};

/**
 * Guard that redirects authenticated users away from public pages (login)
 */
export const PublicOnlyGuard = () => {
  const { isAuthenticated, role } = useAuth();

  if (isAuthenticated) {
    if (role === 'customer') {
      return <Navigate to="/dashboard" replace />;
    }
    return <Navigate to="/ops/queue" replace />;
  }

  return <Outlet />;
};

export default RouteGuard;
