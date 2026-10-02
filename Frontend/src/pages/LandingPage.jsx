import { useNavigate } from 'react-router-dom';
import { Brain, Check, Clock, Headphones, ShieldCheck } from 'lucide-react';
import { Button } from '../components/shared';
import { useAuth } from '../auth/useAuth';
import ShieldIllustration from '../assets/ShieldIllustration';

const features = [
  { icon: Brain, title: 'AI-Powered Insights', desc: 'Get personalized recommendations' },
  { icon: ShieldCheck, title: 'Trusted & Secure', desc: 'Your data is always protected' },
  { icon: Clock, title: 'Save Time & Money', desc: 'Compare and choose the best' },
  { icon: Headphones, title: '24/7 Support', desc: "We're here for you anytime" },
];

const claimSteps = [
  { number: '01', title: 'Submit your claim', description: 'Share the claim details and supporting documents in one place.' },
  { number: '02', title: 'AI agents review the details', description: 'Policy, billing and precedent evidence are reviewed together.' },
  { number: '03', title: 'A human adjuster signs off', description: 'Complex and high-value cases receive human review before a decision.' },
];

const productNames = ['Health', 'Auto', 'Life'];

const LandingPage = () => {
  const navigate = useNavigate();
  const { isAuthenticated, role } = useAuth();

  const handleGetStarted = () => {
    if (isAuthenticated) {
      navigate(role === 'customer' ? '/dashboard' : '/ops/queue');
    } else {
      navigate('/signup');
    }
  };

  return (
    <div className="overflow-x-clip">
      <section className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-12 md:py-20">
        <div className="grid md:grid-cols-2 gap-10 lg:gap-12 items-center">
          <div>
            <span className="eyebrow">CLAIMS, MADE CLEARER</span>
            <h1 className="mt-4 text-4xl md:text-5xl lg:text-6xl font-extrabold leading-tight">
              <span className="text-primary">Clearer claim</span>
              <br />
              <span className="text-accent">decisions.</span>
            </h1>
            <p className="mt-6 text-base md:text-lg text-secondary max-w-lg">
              InsureTrust brings policy, billing and precedent review together so each claim has a clearer path forward.
            </p>
            <div className="mt-8 flex flex-wrap gap-4">
              <Button variant="secondary" size="lg" onClick={handleGetStarted}>
                Get Started
              </Button>
              <Button
                variant="outline"
                size="lg"
                onClick={() => document.getElementById('how-it-works')?.scrollIntoView({ behavior: 'smooth' })}
              >
                Learn More
              </Button>
            </div>

            <div className="mt-8 border-t border-border pt-5">
              <p className="text-sm font-semibold text-primary">Built for faster, clearer claim decisions.</p>
              <ul className="mt-3 grid gap-2 text-sm text-secondary">
                {['AI-assisted review', 'Human sign-off on high-value claims', 'Full audit trail'].map((item) => (
                  <li key={item} className="flex items-center gap-2">
                    <Check size={16} className="text-accent shrink-0" aria-hidden="true" />
                    <span>{item}</span>
                  </li>
                ))}
              </ul>
            </div>
          </div>

          <div className="flex flex-col items-center justify-center gap-5">
            <div className="hidden md:flex flex-wrap items-center justify-center gap-2" aria-label="Insurance products">
              {productNames.map((name) => (
                <span key={name} className="rounded-full border border-border bg-white px-3 py-1.5 text-xs font-semibold text-primary shadow-sm">
                  {name}
                </span>
              ))}
            </div>
            <ShieldIllustration className="w-64 md:w-72 lg:w-96 max-w-full" />
          </div>
        </div>
      </section>

      <section id="features" className="bg-primary">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-8">
            {features.map((feature) => (
              <div key={feature.title} className="flex items-start gap-4">
                <div className="p-2 bg-accent/20 rounded-lg shrink-0">
                  <feature.icon size={24} className="text-accent" />
                </div>
                <div>
                  <h3 className="text-sm font-semibold text-white">{feature.title}</h3>
                  <p className="text-xs text-white/70 mt-1">{feature.desc}</p>
                </div>
              </div>
            ))}
          </div>
        </div>
      </section>

      <section id="how-it-works" className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-16 md:py-20">
        <div className="max-w-2xl">
          <span className="eyebrow">A CLEAR PROCESS</span>
          <h2 className="mt-3 text-3xl font-bold text-primary">How it works</h2>
        </div>
        <ol className="mt-9 grid gap-8 md:grid-cols-3">
          {claimSteps.map((step) => (
            <li key={step.number} className="border-t-2 border-accent pt-4">
              <span className="text-xs font-semibold text-accent">STEP {step.number}</span>
              <h3 className="mt-3 text-lg font-semibold text-primary">{step.title}</h3>
              <p className="mt-2 text-sm leading-6 text-secondary">{step.description}</p>
            </li>
          ))}
        </ol>
      </section>

      <section className="bg-white border-y border-border">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-16 md:py-20">
          <div className="max-w-2xl">
            <span className="eyebrow">BUILT AROUND YOUR CLAIM</span>
            <h2 className="mt-3 text-3xl font-bold text-primary">Why InsureTrust</h2>
          </div>
          <div className="mt-9 grid gap-8 sm:grid-cols-2 lg:grid-cols-4">
            {features.map((feature) => (
              <article key={feature.title} className="border-l-2 border-accent pl-4">
                <feature.icon size={22} className="text-accent" aria-hidden="true" />
                <h3 className="mt-3 text-sm font-semibold text-primary">{feature.title}</h3>
                <p className="mt-1 text-sm leading-6 text-secondary">{feature.desc}</p>
              </article>
            ))}
          </div>
        </div>
      </section>

      <section className="bg-primary">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-14 md:py-16 flex flex-col gap-6 sm:flex-row sm:items-center sm:justify-between">
          <div>
            <h2 className="text-2xl font-bold text-white">Start with a clearer claim process.</h2>
            <p className="mt-2 text-sm text-white/70">Create an account to submit and follow your claim.</p>
          </div>
          <Button variant="secondary" size="lg" onClick={() => navigate('/signup')}>
            Get Started
          </Button>
        </div>
      </section>
    </div>
  );
};

export default LandingPage;