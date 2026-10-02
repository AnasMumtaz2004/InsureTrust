import { useState } from 'react';
import { Link, NavLink, Outlet, useLocation, useNavigate } from 'react-router-dom';
import { Menu, X } from 'lucide-react';
import Logo from '../assets/Logo';
import { Button } from '../components/shared';
import { useAuth } from '../auth/useAuth';

const navLinks = [
  { to: '/', label: 'Home' },
  { to: '/login', label: 'Customer Login' },
  { to: '/staff-login', label: 'Staff Login' },
  { to: '/signup', label: 'Sign up' },
];

const PublicLayout = () => {
  const navigate = useNavigate();
  const location = useLocation();
  const [menuState, setMenuState] = useState({ path: '', open: false });
  const menuOpen = menuState.path === location.pathname && menuState.open;
  const { isAuthenticated, role } = useAuth();

  const handleGetStarted = () => {
    if (isAuthenticated) {
      navigate(role === 'customer' ? '/dashboard' : '/ops/queue');
    } else {
      navigate('/signup');
    }
  };

  const closeMenu = () => setMenuState({ path: location.pathname, open: false });

  return (
    <div className="min-h-screen bg-background">
      <header className="bg-white border-b border-border sticky top-0 z-40">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex items-center justify-between h-16">
            <NavLink to="/" onClick={closeMenu} aria-label="InsureTrust home">
              <Logo size="md" />
            </NavLink>

            <nav className="hidden md:flex items-center gap-8">
              {navLinks.map((link) => (
                <NavLink
                  key={link.to}
                  to={link.to}
                  end={link.to === '/'}
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

            <div className="flex items-center gap-2">
              <Button variant="primary" size="md" onClick={handleGetStarted} className="px-3 py-2 text-xs sm:px-5 sm:py-2.5 sm:text-sm">
                Get Started
              </Button>
              <button
                type="button"
                className="md:hidden inline-flex items-center justify-center w-10 h-10 text-primary hover:bg-background rounded-md"
                aria-label={menuOpen ? 'Close navigation menu' : 'Open navigation menu'}
                aria-expanded={menuOpen}
                aria-controls="mobile-public-navigation"
                onClick={() => setMenuState({ path: location.pathname, open: !menuOpen })}
              >
                {menuOpen ? <X size={20} /> : <Menu size={20} />}
              </button>
            </div>
          </div>
        </div>
        {menuOpen && (
          <nav id="mobile-public-navigation" className="md:hidden border-t border-border bg-white px-4 py-2">
            {navLinks.map((link) => (
              <NavLink
                key={link.to}
                to={link.to}
                end={link.to === '/'}
                onClick={closeMenu}
                className={({ isActive }) =>
                  `block py-3 text-sm font-medium ${isActive ? 'text-primary' : 'text-secondary hover:text-primary'}`
                }
              >
                {link.label}
              </NavLink>
            ))}
          </nav>
        )}
      </header>

      <main>
        <Outlet />
      </main>

      <footer className="border-t border-border bg-white">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8 flex flex-col gap-5 sm:flex-row sm:items-center sm:justify-between">
          <Link to="/" aria-label="InsureTrust home">
            <Logo size="sm" />
          </Link>
          <nav aria-label="Footer" className="flex flex-wrap gap-x-5 gap-y-2 text-sm text-secondary">
            {navLinks.map((link) => (
              <NavLink key={link.to} to={link.to} end={link.to === '/'} className="hover:text-primary">
                {link.label}
              </NavLink>
            ))}
          </nav>
          <p className="text-xs text-secondary">© {new Date().getFullYear()} InsureTrust</p>
        </div>
      </footer>
    </div>
  );
};

export default PublicLayout;
