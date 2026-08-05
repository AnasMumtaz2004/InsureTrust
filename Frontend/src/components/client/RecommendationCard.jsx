import { Shield, Check } from 'lucide-react';
import { Card, Button } from '../shared';

const RecommendationCard = ({ title, description, features = [], ctaText = 'View Details', onCta, compact = false }) => {
  if (compact) {
    return (
      <div className="bg-accent/5 border border-accent/20 rounded-lg p-4">
        <div className="flex items-start gap-3">
          <div className="p-2 bg-accent/10 rounded-lg shrink-0">
            <Shield size={18} className="text-accent" />
          </div>
          <div className="flex-1 min-w-0">
            <h4 className="text-sm font-semibold text-primary">{title}</h4>
            {description && (
              <p className="text-xs text-secondary mt-1">{description}</p>
            )}
            {features.length > 0 && (
              <ul className="mt-2 space-y-1">
                {features.map((feature, i) => (
                  <li key={i} className="flex items-start gap-2 text-xs text-primary">
                    <Check size={14} className="text-accent shrink-0 mt-0.5" />
                    {feature}
                  </li>
                ))}
              </ul>
            )}
            {onCta && (
              <Button variant="secondary" size="sm" className="mt-3" onClick={onCta}>
                {ctaText}
              </Button>
            )}
          </div>
        </div>
      </div>
    );
  }

  return (
    <Card className="p-5">
      <div className="flex items-start gap-4">
        <div className="p-3 bg-accent/10 rounded-lg shrink-0">
          <Shield size={24} className="text-accent" />
        </div>
        <div className="flex-1 min-w-0">
          <h4 className="text-sm font-semibold text-primary">{title}</h4>
          {description && (
            <p className="text-xs text-secondary mt-1">{description}</p>
          )}
          {features.length > 0 && (
            <ul className="mt-3 space-y-1.5">
              {features.map((feature, i) => (
                <li key={i} className="flex items-start gap-2 text-sm text-primary">
                  <Check size={16} className="text-accent shrink-0 mt-0.5" />
                  {feature}
                </li>
              ))}
            </ul>
          )}
          {onCta && (
            <Button variant="secondary" size="sm" className="mt-4" onClick={onCta}>
              {ctaText}
            </Button>
          )}
        </div>
      </div>
    </Card>
  );
};

export default RecommendationCard;
