import { Outlet, NavLink, useNavigate } from 'react-router-dom';
import Logo from '../assets/Logo';
import { Button } from '../components/shared';
import { useAuth } from '../auth/useAuth';

const navLinks = [
  { to: '/', label: 'Home' },
  { to: '/login', label: 'Customer Login' },
  { to: '/staff-login', label: 'Staff Login' },
];

const PublicLayout = () => {
  const navigate = useNavigate();
  const { isAuthenticated, role } = useAuth();

  const handleGetStarted = () => {
    if (isAuthenticated) {
      navigate(role === 'customer' ? '/dashboard' : '/ops/queue');
    } else {
      navigate('/login');
    }
  };

  return (
    <div className="min-h-screen bg-background">
      {/* Top Navigation */}
      <header className="bg-white border-b border-border sticky top-0 z-40">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex items-center justify-between h-16">
            {/* Logo */}
            <NavLink to="/">
              <Logo size="md" />
            </NavLink>

            {/* Nav links - hidden on mobile */}
            <nav className="hidden md:flex items-center gap-8">
              {navLinks.map((link) => (
                <NavLink
                  key={link.to}
                  to={link.to}
                  className={({ isActive }) =>
                    `text-sm font-medium transition-colors duration-150 ${
                      isActive ? 'text-primary' : 'text-secondary hover:text-primary'
                    }`
                  }
                >
                  {link.label}
                </NavLink>
              ))}
            </nav>

            {/* CTA */}
            <Button variant="primary" size="md" onClick={handleGetStarted}>
              Get Started
            </Button>
          </div>
        </div>
      </header>

      {/* Page content */}
      <main>
        <Outlet />
      </main>
    </div>
  );
};

export default PublicLayout;
