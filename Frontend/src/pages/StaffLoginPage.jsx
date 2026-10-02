import { useState } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import { Eye, EyeOff, CircleCheck } from 'lucide-react';
import Logo from '../assets/Logo';
import { Button, Card } from '../components/shared';
import { useAuth } from '../auth/useAuth';

const StaffLoginPage = () => {
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
      await login('staff', { email, password });
      navigate('/ops/queue');
    } catch (err) {
      setError(err.message || 'Unable to sign in right now.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-background flex flex-col">
      {/* Dark navy header bar */}
      <div className="bg-primary py-4 px-6">
        <div className="max-w-md mx-auto flex items-center justify-between">
          <Logo size="md" className="[&_span]:text-white" />
          <span className="text-sm font-medium text-white/80">Staff / Admin Access</span>
        </div>
      </div>

      {/* Login form */}
      <div className="flex-1 flex items-center justify-center px-4 py-12">
        <Card className="w-full max-w-md p-8">
          <div className="mb-8">
            <h2 className="text-xl font-bold text-primary">Staff Login</h2>
            <p className="text-sm text-secondary mt-1">Access the InsureTrust operations dashboard.</p>
          </div>

          <form onSubmit={handleSubmit} className="space-y-5">
            {error && (
              <div className="bg-red-50 text-red-600 text-sm px-4 py-2.5 rounded-md border border-red-200">
                {error}
              </div>
            )}

            <div>
              <label className="block text-sm font-medium text-primary mb-1.5">Staff Email</label>
              <input
                type="email"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                placeholder="Enter your staff email"
                className="w-full px-4 py-2.5 border border-border rounded-md text-sm bg-white focus:outline-none focus:border-accent"
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-primary mb-1.5">Password</label>
              <div className="relative">
                <input
                  type={showPassword ? 'text' : 'password'}
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                  placeholder="Enter your password"
                  className="w-full px-4 py-2.5 pr-10 border border-border rounded-md text-sm bg-white focus:outline-none focus:border-accent"
                />
                <button
                  type="button"
                  onClick={() => setShowPassword(!showPassword)}
                  className="absolute right-3 top-1/2 -translate-y-1/2 text-secondary hover:text-primary cursor-pointer"
                >
                  {showPassword ? <EyeOff size={16} /> : <Eye size={16} />}
                </button>
              </div>
            </div>

            <Button variant="primary" size="lg" type="submit" className="w-full" disabled={loading}>
              {loading ? 'Signing In…' : 'Access Dashboard'}
            </Button>
          </form>

          {/* System status */}
          <div className="mt-6 flex items-center justify-center gap-2">
            <CircleCheck size={14} className="text-accent" />
            <span className="text-xs text-secondary">All systems operational</span>
          </div>

          {/* Customer login link */}
          <div className="mt-4 text-center">
            <Link to="/login" className="text-xs text-secondary hover:text-primary">
              ← Customer Login
            </Link>
          </div>
        </Card>
      </div>
    </div>
  );
};

export default StaffLoginPage;
