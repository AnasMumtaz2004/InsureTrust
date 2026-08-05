import { Avatar } from '../shared';

const mockAdjusters = [
  { name: 'Dr. Smith', status: 'online', activeClaims: 3 },
  { name: 'J. Williams', status: 'online', activeClaims: 5 },
  { name: 'R. Brown', status: 'away', activeClaims: 2 },
  { name: 'A. Martinez', status: 'offline', activeClaims: 0 },
  { name: 'K. Taylor', status: 'online', activeClaims: 4 },
];

const statusColors = {
  online: 'bg-accent',
  away: 'bg-warning',
  offline: 'bg-secondary',
};

const AdjustersList = () => {
  return (
    <div>
      <h3 className="text-sm font-semibold text-primary mb-3">Active Adjusters</h3>
      <div className="space-y-3">
        {mockAdjusters.map((adjuster) => (
          <div key={adjuster.name} className="flex items-center gap-3">
            <div className="relative">
              <Avatar name={adjuster.name} size="sm" />
              <span className={`absolute -bottom-0.5 -right-0.5 w-3 h-3 rounded-full border-2 border-white ${statusColors[adjuster.status]}`} />
            </div>
            <div className="flex-1 min-w-0">
              <p className="text-sm font-medium text-primary truncate">{adjuster.name}</p>
              <p className="text-xs text-secondary">{adjuster.activeClaims} active claims</p>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
};

export default AdjustersList;
