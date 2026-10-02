import { useState } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import { Eye, EyeOff } from 'lucide-react';
import Logo from '../assets/Logo';
import { Button, Card } from '../components/shared';
import { useAuth } from '../auth/useAuth';

const UserLoginPage = () => {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [showPassword, setShowPassword] = useState(false);
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);
  const { login } = useAuth();
  const navigate = useNavigate();

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');

    if (!email || !password) {
      setError('Please fill in all fields.');
      return;
    }

    try {
      setLoading(true);
      await login('customer', { email, password });
      navigate('/dashboard');
    } catch (err) {
      setError(err.message || 'Unable to sign in right now.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-background flex items-center justify-center px-4">
      <Card className="w-full max-w-md p-8">
        {/* Logo + tagline */}
        <div className="text-center mb-8">
          <div className="flex justify-center mb-4">
            <Logo size="lg" />
          </div>
          <p className="text-sm text-secondary">AI-Powered. Trust Assured.</p>
        </div>

        {/* Form */}
        <form onSubmit={handleSubmit} className="space-y-5">
          {error && (
            <div className="bg-red-50 text-red-600 text-sm px-4 py-2.5 rounded-md border border-red-200">
              {error}
            </div>
          )}

          <div>
            <label htmlFor="email" className="block text-sm font-medium text-primary mb-1.5">Email</label>
            <input
              id="email"
              type="email"
              autoComplete="email"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              placeholder="you@example.com"
              className="w-full px-4 py-2.5 border border-border rounded-md text-sm bg-white focus:outline-none focus:border-accent"
            />
          </div>

          <div>
            <label htmlFor="password" className="block text-sm font-medium text-primary mb-1.5">Password</label>
            <div className="relative">
              <input
                id="password"
                type={showPassword ? 'text' : 'password'}
                autoComplete="current-password"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                placeholder="Enter your password"
                className="w-full px-4 py-2.5 pr-10 border border-border rounded-md text-sm bg-white focus:outline-none focus:border-accent"
              />
              <button
                type="button"
                onClick={() => setShowPassword(!showPassword)}
                aria-label={`${showPassword ? 'Hide' : 'Show'} password`}
                className="absolute right-3 top-1/2 -translate-y-1/2 text-secondary hover:text-primary cursor-pointer"
              >
                {showPassword ? <EyeOff size={16} /> : <Eye size={16} />}
              </button>
            </div>
          </div>

          <Button variant="primary" size="lg" type="submit" className="w-full" disabled={loading}>
            {loading ? 'Signing In…' : 'Sign In'}
          </Button>

        </form>

        {/* Footer link */}
        <div className="mt-6 text-center">
          <p className="text-sm text-secondary">
            New here?{' '}
            <Link to="/signup" className="text-accent font-medium hover:underline">
              Create an account
            </Link>
          </p>
        </div>

        {/* Staff login link */}
        <div className="mt-4 text-center">
          <Link to="/staff-login" className="text-xs text-secondary hover:text-primary">
            Staff / Admin Access →
          </Link>
        </div>
      </Card>
    </div>
  );
};

export default UserLoginPage;
