import Card from './Card';

const KpiCard = ({ title, value, linkText, linkHref, icon: Icon }) => {
  return (
    <Card className="p-5">
      <div className="flex items-start justify-between">
        <div>
          <p className="text-sm text-secondary font-medium">{title}</p>
          <p className="text-2xl font-bold text-primary mt-1">{value}</p>
          {linkText && (
            <a
              href={linkHref || '#'}
              className="text-xs text-accent font-medium mt-2 inline-block hover:underline"
            >
              {linkText}
            </a>
          )}
        </div>
        {Icon && (
          <div className="p-2 bg-accent/10 rounded-lg">
            <Icon size={20} className="text-accent" />
          </div>
        )}
      </div>
    </Card>
  );
};

export default KpiCard;
