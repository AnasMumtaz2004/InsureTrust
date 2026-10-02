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
  'pending-approval': {
    container: 'bg-warning/10 text-warning',
    icon: false,
  },
  approved: {
    container: 'bg-accent/10 text-accent',
    icon: true,
  },
  'partial-approved': {
    container: 'bg-warning/10 text-warning',
    icon: false,
  },
  denied: {
    container: 'bg-primary/10 text-primary',
    icon: false,
  },
  overridden: {
    container: 'bg-secondary/10 text-secondary',
    icon: false,
  },
  'sent-back': {
    container: 'bg-warning/10 text-warning',
    icon: false,
  },
  'processing-failed': {
    container: 'bg-primary/10 text-primary',
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
  const normalizedStatus = status.toLowerCase().replace(/_/g, '-');
  const style = statusStyles[normalizedStatus] || statusStyles.default;
  const displayLabel = label || normalizedStatus.charAt(0).toUpperCase() + normalizedStatus.slice(1);

  return (
    <span className={`inline-flex items-center gap-1 px-2.5 py-0.5 rounded-full text-xs font-medium ${style.container}`}>
      {style.icon && <Check size={12} strokeWidth={2.5} />}
      {displayLabel}
    </span>
  );
};

export default StatusChip;
