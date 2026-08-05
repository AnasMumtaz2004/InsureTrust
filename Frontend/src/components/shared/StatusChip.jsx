import { Check } from 'lucide-react';

const statusStyles = {
  active: {
    container: 'bg-accent/10 text-accent',
    icon: true,
  },
  success: {
    container: 'bg-accent/10 text-accent',
    icon: true,
  },
  'in-review': {
    container: 'bg-warning/10 text-warning',
    icon: false,
  },
  pending: {
    container: 'bg-secondary/10 text-secondary',
    icon: false,
  },
  default: {
    container: 'bg-secondary/10 text-secondary',
    icon: false,
  },
};

const StatusChip = ({ status = 'default', label }) => {
  const style = statusStyles[status] || statusStyles.default;
  const displayLabel = label || status.charAt(0).toUpperCase() + status.slice(1);

  return (
    <span className={`inline-flex items-center gap-1 px-2.5 py-0.5 rounded-full text-xs font-medium ${style.container}`}>
      {style.icon && <Check size={12} strokeWidth={2.5} />}
      {displayLabel}
    </span>
  );
};

export default StatusChip;
