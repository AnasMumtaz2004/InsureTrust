import { useEffect, useState } from 'react';
import { Avatar } from '../shared';
import { useAuth } from '../../auth/useAuth';
import { getOpsUsers } from '../../api/clientApi';

const AdjustersList = () => {
  const [users, setUsers] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const { token } = useAuth();

  useEffect(() => {
    let active = true;
    const loadUsers = async () => {
      if (!token) return;
      try {
        const result = await getOpsUsers(token);
        if (active) setUsers(result || []);
      } catch (requestError) {
        if (active) setError(requestError.message || 'Unable to load staff users.');
      } finally {
        if (active) setLoading(false);
      }
    };
    loadUsers();
    return () => { active = false; };
  }, [token]);

  return (
    <div>
      <h3 className="mb-3 text-sm font-semibold text-primary">Staff Adjusters</h3>
      {loading ? (
        <p className="text-xs text-secondary">Loading staff…</p>
      ) : error ? (
        <p role="alert" className="text-xs text-red-600">{error}</p>
      ) : users.length === 0 ? (
        <p className="text-xs text-secondary">No staff users found.</p>
      ) : (
        <ul className="space-y-3">
          {users.map((user) => (
            <li key={user.id} className="flex min-w-0 items-center gap-3">
              <Avatar name={user.full_name} size="sm" />
              <div className="min-w-0 flex-1">
                <p className="truncate text-sm font-medium text-primary">{user.full_name}</p>
                <p className="text-xs text-secondary">{user.claims_acted_on} claims acted on</p>
              </div>
            </li>
          ))}
        </ul>
      )}
    </div>
  );
};

export default AdjustersList;