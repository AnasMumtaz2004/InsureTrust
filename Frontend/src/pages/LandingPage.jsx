import { useNavigate } from 'react-router-dom';
import { Brain, ShieldCheck, Clock, Headphones, Star } from 'lucide-react';
import { Button } from '../components/shared';
import ShieldIllustration from '../assets/ShieldIllustration';

const features = [
  { icon: Brain, title: 'AI-Powered Insights', desc: 'Get personalized recommendations' },
  { icon: ShieldCheck, title: 'Trusted & Secure', desc: 'Your data is always protected' },
  { icon: Clock, title: 'Save Time & Money', desc: 'Compare and choose the best' },
  { icon: Headphones, title: '24/7 Support', desc: "We're here for you anytime" },
];

const insuranceCards = [
  { name: 'Health Insurance', price: '$19', color: 'accent' },
  { name: 'Car Insurance', price: '$29', color: 'primary' },
  { name: 'Life Insurance', price: '$15', color: 'accent' },
];

const LandingPage = () => {
  const navigate = useNavigate();

  return (
    <div>
      {/* Hero Section */}
      <section className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-12 md:py-20">
        <div className="grid md:grid-cols-2 gap-12 items-center">
          {/* Left — Text */}
          <div>
            <span className="eyebrow">AI-POWERED INSURANCE ASSISTANT</span>
            <h1 className="mt-4 text-4xl md:text-5xl lg:text-6xl font-extrabold leading-tight">
              <span className="text-primary">Smart Insurance.</span>
              <br />
              <span className="text-accent">Trusted Protection.</span>
            </h1>
            <p className="mt-6 text-base md:text-lg text-secondary max-w-lg">
              InsureTrust uses advanced AI agents to help you find the right insurance, instantly.
            </p>
            <div className="mt-8 flex flex-wrap gap-4">
              <Button variant="secondary" size="lg" onClick={() => navigate('/login')}>
                Get Started
              </Button>
              <Button variant="outline" size="lg" onClick={() => document.getElementById('features')?.scrollIntoView({ behavior: 'smooth' })}>
                Learn More
              </Button>
            </div>

            {/* Trust strip */}
            <div className="mt-10 flex items-center gap-4">
              <div className="flex -space-x-2">
                {['AM', 'SK', 'JD', 'RP'].map((initials, i) => (
                  <div
                    key={i}
                    className="w-8 h-8 rounded-full bg-primary text-white text-xs font-medium flex items-center justify-center border-2 border-white"
                  >
                    {initials}
                  </div>
                ))}
              </div>
              <div>
                <p className="text-sm font-medium text-primary">Trusted by 10,000+ users</p>
                <div className="flex items-center gap-0.5 mt-0.5">
                  {[1, 2, 3, 4, 5].map((i) => (
                    <Star key={i} size={14} className="text-warning fill-warning" />
                  ))}
                </div>
              </div>
            </div>
          </div>

          {/* Right — Illustration + floating cards */}
          <div className="relative flex justify-center">
            <ShieldIllustration className="w-64 md:w-80 lg:w-96" />

            {/* Floating insurance cards */}
            {insuranceCards.map((card, i) => (
              <div
                key={card.name}
                className={`absolute bg-white border border-border rounded-lg px-4 py-3 shadow-sm ${
                  i === 0 ? 'top-2 right-0 md:right-4' :
                  i === 1 ? 'top-1/2 -translate-y-1/2 right-0 md:-right-4' :
                  'bottom-8 right-4 md:right-0'
                }`}
              >
                <p className="text-xs font-semibold text-primary">{card.name}</p>
                <p className="text-sm font-bold text-accent mt-0.5">
                  From {card.price}<span className="text-xs font-normal text-secondary">/month</span>
                </p>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* Features Strip */}
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
    </div>
  );
};

export default LandingPage;
