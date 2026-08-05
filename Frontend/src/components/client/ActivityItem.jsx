import { StatusChip } from '../shared';

const iconColors = {
  claim: 'bg-accent/10 text-accent',
  renewal: 'bg-primary/10 text-primary',
  payment: 'bg-accent/10 text-accent',
};

const ActivityItem = ({ icon: Icon, title, subtitle, status, statusLabel, timestamp }) => {
  return (
    <div className="flex items-start gap-3 py-3">
      {Icon && (
        <div className={`p-2 rounded-lg shrink-0 ${iconColors[status] || 'bg-secondary/10 text-secondary'}`}>
          <Icon size={16} />
        </div>
      )}
      <div className="flex-1 min-w-0">
        <div className="flex items-start justify-between gap-2">
          <div>
            <p className="text-sm font-medium text-primary">{title}</p>
            {subtitle && <p className="text-xs text-secondary mt-0.5">{subtitle}</p>}
          </div>
          <div className="flex flex-col items-end gap-1 shrink-0">
            {statusLabel && <StatusChip status={status} label={statusLabel} />}
            {timestamp && <span className="text-xs text-secondary">{timestamp}</span>}
          </div>
        </div>
      </div>
    </div>
  );
};

export default ActivityItem;
