import { Bot } from 'lucide-react';

const AiAvatar = ({ size = 32, className = '' }) => {
  return (
    <div
      className={`flex items-center justify-center rounded-full bg-accent/10 ${className}`}
      style={{ width: size, height: size }}
    >
      <Bot size={size * 0.55} className="text-accent" />
    </div>
  );
};

export default AiAvatar;
