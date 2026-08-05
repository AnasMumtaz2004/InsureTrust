const ShieldIllustration = ({ className = '' }) => {
  return (
    <div className={`relative ${className}`}>
      <svg viewBox="0 0 400 400" fill="none" xmlns="http://www.w3.org/2000/svg" className="w-full h-full">
        {/* Background glow */}
        <defs>
          <radialGradient id="glow" cx="50%" cy="50%" r="50%">
            <stop offset="0%" stopColor="#14B8A6" stopOpacity="0.15" />
            <stop offset="100%" stopColor="#14B8A6" stopOpacity="0" />
          </radialGradient>
          <linearGradient id="shieldGrad" x1="200" y1="60" x2="200" y2="340" gradientUnits="userSpaceOnUse">
            <stop offset="0%" stopColor="#14B8A6" />
            <stop offset="100%" stopColor="#0F172A" />
          </linearGradient>
        </defs>

        <circle cx="200" cy="200" r="180" fill="url(#glow)" />

        {/* Shield shape */}
        <path
          d="M200 70 L310 120 C310 120 320 240 200 330 C80 240 90 120 90 120 L200 70Z"
          fill="url(#shieldGrad)"
          opacity="0.9"
        />

        {/* Inner shield highlight */}
        <path
          d="M200 95 L290 135 C290 135 298 235 200 310 C102 235 110 135 110 135 L200 95Z"
          fill="none"
          stroke="white"
          strokeOpacity="0.2"
          strokeWidth="1.5"
        />

        {/* Check mark */}
        <path
          d="M165 200 L190 225 L240 175"
          stroke="white"
          strokeWidth="8"
          strokeLinecap="round"
          strokeLinejoin="round"
          fill="none"
        />

        {/* Decorative dots */}
        <circle cx="85" cy="100" r="4" fill="#14B8A6" opacity="0.4" />
        <circle cx="320" cy="90" r="3" fill="#14B8A6" opacity="0.3" />
        <circle cx="340" cy="280" r="5" fill="#0F172A" opacity="0.2" />
        <circle cx="60" cy="260" r="3" fill="#14B8A6" opacity="0.3" />
      </svg>
    </div>
  );
};

export default ShieldIllustration;
