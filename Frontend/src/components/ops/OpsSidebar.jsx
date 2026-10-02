import { NavLink, useNavigate } from 'react-router-dom';
import { useState } from 'react';
import {
  AlertTriangle, ChevronLeft, ChevronRight, LogOut
} from 'lucide-react';
import Logo from '../../assets/Logo';
import { useAuth } from '../../auth/useAuth';

const navItems = [
  { to: '/ops/queue', icon: AlertTriangle, label: 'Claims Queue' },
];

const OpsSidebar = () => {
  const [collapsed, setCollapsed] = useState(false);
  const { logout } = useAuth();
  const navigate = useNavigate();

  const handleLogout = () => {
    logout();
    navigate('/');
  };

  return (
    <aside
      className={`hidden md:flex flex-col h-screen bg-white border-r border-border fixed left-0 top-0 z-30 transition-all duration-200 ${
        collapsed ? 'w-16' : 'w-60'
      }`}
    >
      {/* Logo */}
      <div className="px-3 py-5 border-b border-border flex items-center justify-between">
        {!collapsed && <Logo size="md" />}
        <button
          onClick={() => setCollapsed(!collapsed)}
          className="p-1.5 rounded-md hover:bg-background text-secondary cursor-pointer"
        >
          {collapsed ? <ChevronRight size={16} /> : <ChevronLeft size={16} />}
        </button>
      </div>

      {/* Navigation */}
      <nav className="flex-1 px-2 py-4 overflow-y-auto">
        <ul className="space-y-1">
          {navItems.map((item) => (
            <li key={item.to}>
              <NavLink
                to={item.to}
                className={({ isActive }) =>
                  `flex items-center gap-3 px-3 py-2.5 rounded-md text-sm font-medium transition-colors duration-150 ${
                    collapsed ? 'justify-center' : ''
                  } ${
                    isActive
                      ? 'bg-accent/10 text-accent'
                      : 'text-secondary hover:bg-background hover:text-primary'
                  }`
                }
                title={collapsed ? item.label : undefined}
              >
                <item.icon size={18} />
                {!collapsed && item.label}
              </NavLink>
            </li>
          ))}
        </ul>
      </nav>

      {/* Logout */}
      <div className="px-2 py-4 border-t border-border">
        <button
          onClick={handleLogout}
          className={`flex items-center gap-3 px-3 py-2.5 rounded-md text-sm font-medium text-secondary hover:bg-background hover:text-primary w-full cursor-pointer transition-colors duration-150 ${
            collapsed ? 'justify-center' : ''
          }`}
          title={collapsed ? 'Logout' : undefined}
        >
          <LogOut size={18} />
          {!collapsed && 'Logout'}
        </button>
      </div>
    </aside>
  );
};

export default OpsSidebar;
