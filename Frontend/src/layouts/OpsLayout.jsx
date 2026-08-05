import { Outlet } from 'react-router-dom';
import { OpsSidebar } from '../components/ops';
import { Avatar } from '../components/shared';
import { useAuth } from '../auth/AuthContext';

const OpsLayout = () => {
  const { user } = useAuth();
  const name = user?.name || 'Admin';

  return (
    <div className="min-h-screen bg-background">
      {/* Sidebar */}
      <OpsSidebar />

      {/* Main content — responsive to sidebar collapse */}
      <div className="md:ml-60 transition-all duration-200">
        {/* Top bar */}
        <header className="flex items-center justify-between px-6 py-4 bg-white border-b border-border">
          <div>
            <h1 className="text-lg font-semibold text-primary">Operations Center</h1>
            <p className="text-sm text-secondary">Welcome, {name}</p>
          </div>
          <div className="flex items-center gap-3">
            <Avatar name={name} size="md" />
          </div>
        </header>

        {/* Page content */}
        <main className="p-4 md:p-6">
          <Outlet />
        </main>
      </div>
    </div>
  );
};

export default OpsLayout;
