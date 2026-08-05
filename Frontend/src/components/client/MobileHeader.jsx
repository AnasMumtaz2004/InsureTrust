import { Bell } from 'lucide-react';
import { IconButton, Avatar } from '../shared';
import { useAuth } from '../../auth/AuthContext';

const MobileHeader = () => {
  const { user } = useAuth();
  const name = user?.name || 'User';

  return (
    <div className="md:hidden flex items-center justify-between px-5 py-4 bg-white border-b border-border">
      <div>
        <h1 className="text-xl font-bold text-primary">Hello, {name}</h1>
        <p className="text-sm text-secondary">Good to see you!</p>
      </div>
      <div className="flex items-center gap-2">
        <IconButton icon={Bell} badge="2" />
        <Avatar name={name} size="md" />
      </div>
    </div>
  );
};

export default MobileHeader;
