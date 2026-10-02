import { Outlet } from 'react-router-dom';
import { Bell } from 'lucide-react';
import { ClientSidebar, MobileTabBar, MobileHeader } from '../components/client';
import { IconButton, Avatar } from '../components/shared';
import { useAuth } from '../auth/useAuth';

const ClientLayout = () => {
  const { user } = useAuth();
  const name = user?.name || 'User';

  return (
    <div className="min-h-screen bg-background">
      {/* Desktop sidebar */}
      <ClientSidebar />

      {/* Mobile header */}
      <MobileHeader />

      {/* Main content */}
      <div className="md:ml-60">
        {/* Desktop top bar */}
        <header className="hidden md:flex items-center justify-between px-6 py-4 bg-white border-b border-border">
          <div>
            <h1 className="text-lg font-semibold text-primary">Welcome Back, {name} 👋</h1>
          </div>
          <div className="flex items-center gap-3">
            <IconButton icon={Bell} badge="2" />
            <Avatar name={name} size="md" />
          </div>
        </header>

        {/* Page content */}
        <main className="p-4 md:p-6 pb-20 md:pb-6">
          <Outlet />
        </main>
      </div>

      {/* Mobile bottom tab bar */}
      <MobileTabBar />
    </div>
  );
};

export default ClientLayout;
