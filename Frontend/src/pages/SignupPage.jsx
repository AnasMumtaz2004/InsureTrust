import { useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { Eye, EyeOff } from 'lucide-react';
import Logo from '../assets/Logo';
import { Button, Card } from '../components/shared';
import { useAuth } from '../auth/useAuth';
import { register } from '../api/clientApi';

const inputClassName = 'w-full px-4 py-2.5 border border-border rounded-md text-sm bg-white focus:outline-none focus:border-accent';

const SignupPage = () => {
  const [formData, setFormData] = useState({
    fullName: '',
    email: '',
    password: '',
    confirmPassword: '',
  });
  const [showPassword, setShowPassword] = useState(false);
  const [showConfirmPassword, setShowConfirmPassword] = useState(false);
  const [termsAccepted, setTermsAccepted] = useState(false);
  const [fieldErrors, setFieldErrors] = useState({});
  const [error, setError] = useState('');
  const [submitting, setSubmitting] = useState(false);
  const { login } = useAuth();
  const navigate = useNavigate();

  const updateField = (field, value) => {
    setFormData((current) => ({ ...current, [field]: value }));
    setFieldErrors((current) => ({ ...current, [field]: '' }));
    setError('');
  };

  const validate = () => {
    const errors = {};
    if (!formData.fullName.trim()) errors.fullName = 'Full name is required.';
    if (!formData.email.trim()) {
      errors.email = 'Email is required.';
    } else if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(formData.email.trim())) {
      errors.email = 'Enter a valid email address.';
    }
    if (!formData.password) {
      errors.password = 'Password is required.';
    } else if (formData.password.length < 8) {
      errors.password = 'Password must be at least 8 characters.';
    }
    if (!formData.confirmPassword) {
      errors.confirmPassword = 'Please confirm your password.';
    } else if (formData.password !== formData.confirmPassword) {
      errors.confirmPassword = 'Passwords do not match.';
    }
    if (!termsAccepted) errors.termsAccepted = 'You must accept the terms to continue.';
    setFieldErrors(errors);
    return Object.keys(errors).length === 0;
  };

  const handleSubmit = async (event) => {
    event.preventDefault();
    setError('');
    if (!validate()) return;

    try {
      setSubmitting(true);
      await register(formData.fullName.trim(), formData.email.trim(), formData.password);
      await login('customer', { email: formData.email.trim(), password: formData.password });
      navigate('/dashboard');
    } catch (requestError) {
      setError(requestError.message || 'Unable to create your account right now.');
    } finally {
      setSubmitting(false);
    }
  };

  const renderPasswordToggle = (field, visible, setVisible, label) => (
    <button
      type="button"
      onClick={() => setVisible(!visible)}
      aria-label={`${visible ? 'Hide' : 'Show'} ${label.toLowerCase()}`}
      className="absolute right-3 top-1/2 -translate-y-1/2 text-secondary hover:text-primary cursor-pointer"
    >
      {visible ? <EyeOff size={16} /> : <Eye size={16} />}
    </button>
  );

  return (
    <div className="min-h-screen bg-background flex items-center justify-center px-4 py-10">
      <Card className="w-full max-w-md p-8">
        <div className="text-center mb-8">
          <div className="flex justify-center mb-4">
            <Logo size="lg" />
          </div>
          <p className="text-sm text-secondary">Create your InsureTrust account.</p>
        </div>

        <form onSubmit={handleSubmit} className="space-y-5" noValidate>
          {error && (
            <div role="alert" className="bg-red-50 text-red-600 text-sm px-4 py-2.5 rounded-md border border-red-200">
              {error}
            </div>
          )}

          <div>
            <label htmlFor="fullName" className="block text-sm font-medium text-primary mb-1.5">Full name</label>
            <input
              id="fullName"
              type="text"
              autoComplete="name"
              value={formData.fullName}
              onChange={(event) => updateField('fullName', event.target.value)}
              className={inputClassName}
              aria-invalid={!!fieldErrors.fullName}
              aria-describedby={fieldErrors.fullName ? 'fullName-error' : undefined}
            />
            {fieldErrors.fullName && <p id="fullName-error" className="mt-1 text-xs text-red-600">{fieldErrors.fullName}</p>}
          </div>

          <div>
            <label htmlFor="email" className="block text-sm font-medium text-primary mb-1.5">Email</label>
            <input
              id="email"
              type="email"
              autoComplete="email"
              value={formData.email}
              onChange={(event) => updateField('email', event.target.value)}
              className={inputClassName}
              aria-invalid={!!fieldErrors.email}
              aria-describedby={fieldErrors.email ? 'email-error' : undefined}
            />
            {fieldErrors.email && <p id="email-error" className="mt-1 text-xs text-red-600">{fieldErrors.email}</p>}
          </div>

          <div>
            <label htmlFor="password" className="block text-sm font-medium text-primary mb-1.5">Password</label>
            <div className="relative">
              <input
                id="password"
                type={showPassword ? 'text' : 'password'}
                autoComplete="new-password"
                value={formData.password}
                onChange={(event) => updateField('password', event.target.value)}
                className={`${inputClassName} pr-10`}
                aria-invalid={!!fieldErrors.password}
                aria-describedby={fieldErrors.password ? 'password-error' : undefined}
              />
              {renderPasswordToggle('password', showPassword, setShowPassword, 'Password')}
            </div>
            {fieldErrors.password && <p id="password-error" className="mt-1 text-xs text-red-600">{fieldErrors.password}</p>}
          </div>

          <div>
            <label htmlFor="confirmPassword" className="block text-sm font-medium text-primary mb-1.5">Confirm password</label>
            <div className="relative">
              <input
                id="confirmPassword"
                type={showConfirmPassword ? 'text' : 'password'}
                autoComplete="new-password"
                value={formData.confirmPassword}
                onChange={(event) => updateField('confirmPassword', event.target.value)}
                className={`${inputClassName} pr-10`}
                aria-invalid={!!fieldErrors.confirmPassword}
                aria-describedby={fieldErrors.confirmPassword ? 'confirmPassword-error' : undefined}
              />
              {renderPasswordToggle('confirmPassword', showConfirmPassword, setShowConfirmPassword, 'confirm password')}
            </div>
            {fieldErrors.confirmPassword && <p id="confirmPassword-error" className="mt-1 text-xs text-red-600">{fieldErrors.confirmPassword}</p>}
          </div>

          <div>
            <label className="flex items-start gap-2 text-sm text-secondary">
              <input
                type="checkbox"
                checked={termsAccepted}
                onChange={(event) => {
                  setTermsAccepted(event.target.checked);
                  setFieldErrors((current) => ({ ...current, termsAccepted: '' }));
                }}
                className="mt-0.5 accent-accent"
                aria-invalid={!!fieldErrors.termsAccepted}
                aria-describedby={fieldErrors.termsAccepted ? 'terms-error' : undefined}
              />
              <span>I agree to the terms.</span>
            </label>
            {fieldErrors.termsAccepted && <p id="terms-error" className="mt-1 text-xs text-red-600">{fieldErrors.termsAccepted}</p>}
          </div>

          <Button variant="primary" size="lg" type="submit" className="w-full" disabled={submitting}>
            {submitting ? 'Creating Account…' : 'Create Account'}
          </Button>
        </form>

        <div className="mt-6 text-center">
          <p className="text-sm text-secondary">
            Already have an account?{' '}
            <Link to="/login" className="text-accent font-medium hover:underline">Sign in</Link>
          </p>
        </div>
      </Card>
    </div>
  );
};

export default SignupPage;