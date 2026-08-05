import { Routes, Route, Navigate } from 'react-router-dom';
import { RouteGuard, PublicOnlyGuard } from './auth/RouteGuard';
import PublicLayout from './layouts/PublicLayout';
import ClientLayout from './layouts/ClientLayout';
import OpsLayout from './layouts/OpsLayout';

import LandingPage from './pages/LandingPage';
import UserLoginPage from './pages/UserLoginPage';
import StaffLoginPage from './pages/StaffLoginPage';
import DashboardPage from './pages/DashboardPage';
import AiAssistantPage from './pages/AiAssistantPage';
import OpsQueuePage from './pages/OpsQueuePage';
import CaseWorkspacePage from './pages/CaseWorkspacePage';

function App() {
  return (
    <Routes>
      {/* Public Routes */}
      <Route element={<PublicLayout />}>
        <Route path="/" element={<LandingPage />} />
      </Route>

      {/* Public Only Auth Routes (redirect if already logged in) */}
      <Route element={<PublicOnlyGuard />}>
        <Route path="/login" element={<UserLoginPage />} />
        <Route path="/staff-login" element={<StaffLoginPage />} />
      </Route>

      {/* Customer Routes (Guarded: customer role) */}
      <Route element={<RouteGuard allowedRoles={['customer']} />}>
        <Route element={<ClientLayout />}>
          <Route path="/dashboard" element={<DashboardPage />} />
        </Route>

        {/* AI Assistant view (has its own icon rail / layout) */}
        <Route path="/assistant" element={<AiAssistantPage />} />
      </Route>

      {/* Staff Routes (Guarded: staff or admin role) */}
      <Route element={<RouteGuard allowedRoles={['staff', 'admin']} />}>
        <Route element={<OpsLayout />}>
          <Route path="/ops/queue" element={<OpsQueuePage />} />
          <Route path="/ops/case/:id" element={<CaseWorkspacePage />} />
        </Route>
      </Route>

      {/* Catch-all redirect */}
      <Route path="*" element={<Navigate to="/" replace />} />
    </Routes>
  );
}

export default App;
