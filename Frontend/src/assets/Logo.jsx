import { Shield } from 'lucide-react';

const Logo = ({ size = 'md', className = '' }) => {
  const sizes = {
    sm: { icon: 18, text: 'text-lg' },
    md: { icon: 24, text: 'text-xl' },
    lg: { icon: 32, text: 'text-2xl' },
  };

  const s = sizes[size] || sizes.md;

  return (
    <div className={`flex items-center gap-2 ${className}`}>
      <div className="relative">
        <Shield size={s.icon} className="text-accent fill-accent/20" strokeWidth={2} />
        <div className="absolute inset-0 flex items-center justify-center">
          <div className="w-1.5 h-1.5 bg-accent rounded-full" style={{ marginTop: '2px' }} />
        </div>
      </div>
      <span className={`font-bold text-primary ${s.text}`}>
        Insure<span className="text-accent">Trust</span>
      </span>
    </div>
  );
};

export default Logo;
