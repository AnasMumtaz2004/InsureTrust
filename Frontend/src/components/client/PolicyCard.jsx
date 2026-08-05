import { Heart, Car, Shield } from 'lucide-react';
import { StatusChip } from '../shared';

const iconMap = {
  health: Heart,
  car: Car,
  life: Shield,
};

const PolicyCard = ({ name, type = 'health', status = 'active', onClick }) => {
  const Icon = iconMap[type] || Shield;

  return (
    <div
      className="flex items-center justify-between px-4 py-3 bg-white border border-border rounded-lg cursor-pointer hover:bg-background transition-colors duration-150"
      onClick={onClick}
    >
      <div className="flex items-center gap-3">
        <div className="p-2 bg-accent/10 rounded-lg">
          <Icon size={18} className="text-accent" />
        </div>
        <span className="text-sm font-medium text-primary">{name}</span>
      </div>
      <StatusChip status={status} />
    </div>
  );
};

export default PolicyCard;
