import { useMemo, useState } from 'react';
import { Search, ChevronDown } from 'lucide-react';
import { StatusChip } from '../shared';

const ClaimsTable = ({ claims = [], loading = false, onSelectClaim }) => {
  const [search, setSearch] = useState('');
  const [filterType, setFilterType] = useState('all');
  const [filterStatus, setFilterStatus] = useState('all');
  const [filterComplexity, setFilterComplexity] = useState('all');
  const [sortComplexity, setSortComplexity] = useState('none');

  const filtered = useMemo(() => {
    const matching = (claims || []).filter((claim) => {
      const claimLabel = `${claim.claim_number || ''} ${claim.policy_number || ''}`.toLowerCase();
      const matchSearch = claimLabel.includes(search.toLowerCase()) || (claim.claim_id || claim.id || '').toLowerCase().includes(search.toLowerCase());
      const matchType = filterType === 'all' || (claim.product_line || claim.type || '').toLowerCase() === filterType;
      const normalizedStatus = (claim.status || '').toLowerCase().replace(/_/g, '-');
      const matchStatus = filterStatus === 'all' || normalizedStatus === filterStatus;
      const isHighComplexity = (claim.complexity_score || 0) >= 7;
      const matchComplexity = filterComplexity === 'all'
        || (filterComplexity === 'high' && isHighComplexity)
        || (filterComplexity === 'standard' && !isHighComplexity);
      return matchSearch && matchType && matchStatus && matchComplexity;
    });
    if (sortComplexity === 'high-first') matching.sort((a, b) => (b.complexity_score || 0) - (a.complexity_score || 0));
    if (sortComplexity === 'low-first') matching.sort((a, b) => (a.complexity_score || 0) - (b.complexity_score || 0));
    return matching;
  }, [claims, filterComplexity, filterStatus, filterType, search, sortComplexity]);

  return (
    <div>
      {/* Search and filters */}
      <div className="flex flex-wrap items-center gap-3 mb-4">
        <div className="relative flex-1 min-w-50">
          <Search size={16} className="absolute left-3 top-1/2 -translate-y-1/2 text-secondary" />
          <input
            type="text"
            placeholder="Search claims..."
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            className="w-full pl-9 pr-4 py-2 border border-border rounded-md text-sm bg-white focus:outline-none focus:border-accent"
          />
        </div>
        <div className="relative">
          <select
            value={filterType}
            onChange={(e) => setFilterType(e.target.value)}
            className="appearance-none pl-3 pr-8 py-2 border border-border rounded-md text-sm bg-white focus:outline-none focus:border-accent cursor-pointer"
          >
            <option value="all">All Types</option>
            <option value="health">Health</option>
            <option value="auto">Auto</option>
            <option value="life">Life</option>
          </select>
          <ChevronDown size={14} className="absolute right-2.5 top-1/2 -translate-y-1/2 text-secondary pointer-events-none" />
        </div>
        <div className="relative">
          <select
            value={filterStatus}
            onChange={(e) => setFilterStatus(e.target.value)}
            className="appearance-none pl-3 pr-8 py-2 border border-border rounded-md text-sm bg-white focus:outline-none focus:border-accent cursor-pointer"
          >
            <option value="all">All Status</option>
            <option value="in-review">In Review</option>
            <option value="pending-approval">Pending Approval</option>
            <option value="approved">Approved</option>
            <option value="partial-approved">Partial Approved</option>
            <option value="denied">Denied</option>
            <option value="overridden">Overridden</option>
            <option value="sent-back">Sent Back</option>
            <option value="processing-failed">Processing Failed</option>
          </select>
          <ChevronDown size={14} className="absolute right-2.5 top-1/2 -translate-y-1/2 text-secondary pointer-events-none" />
        </div>
        <div className="relative">
          <label htmlFor="complexity-filter" className="sr-only">Filter by complexity</label>
          <select id="complexity-filter" value={filterComplexity} onChange={(e) => setFilterComplexity(e.target.value)} className="appearance-none pl-3 pr-8 py-2 border border-border rounded-md text-sm bg-white focus:outline-none focus:border-accent cursor-pointer">
            <option value="all">All Complexity</option>
            <option value="high">High (7+)</option>
            <option value="standard">Standard (&lt;7)</option>
          </select>
          <ChevronDown size={14} className="absolute right-2.5 top-1/2 -translate-y-1/2 text-secondary pointer-events-none" />
        </div>
        <div className="relative">
          <label htmlFor="complexity-sort" className="sr-only">Sort by complexity</label>
          <select id="complexity-sort" value={sortComplexity} onChange={(e) => setSortComplexity(e.target.value)} className="appearance-none pl-3 pr-8 py-2 border border-border rounded-md text-sm bg-white focus:outline-none focus:border-accent cursor-pointer">
            <option value="none">Default order</option>
            <option value="high-first">Complexity: high first</option>
            <option value="low-first">Complexity: low first</option>
          </select>
          <ChevronDown size={14} className="absolute right-2.5 top-1/2 -translate-y-1/2 text-secondary pointer-events-none" />
        </div>
      </div>

      {/* Table */}
      <div className="overflow-x-auto border border-border rounded-lg">
        <table className="w-full text-sm">
          <thead>
            <tr className="bg-background">
              <th className="text-left px-4 py-3 font-medium text-secondary">Claim ID</th>
              <th className="text-left px-4 py-3 font-medium text-secondary">Policy</th>
              <th className="text-left px-4 py-3 font-medium text-secondary">Status</th>
              <th className="text-left px-4 py-3 font-medium text-secondary">Amount</th>
              <th className="text-left px-4 py-3 font-medium text-secondary">Complexity</th>
              <th className="text-left px-4 py-3 font-medium text-secondary">Flags</th>
              <th className="text-left px-4 py-3 font-medium text-secondary">Created</th>
            </tr>
          </thead>
          <tbody>
            {loading ? (
              <tr>
                <td colSpan={7} className="px-4 py-8 text-center text-secondary">Loading claims…</td>
              </tr>
            ) : filtered.length === 0 ? (
              <tr>
                <td colSpan={7} className="px-4 py-8 text-center text-secondary">No claims match your filters.</td>
              </tr>
            ) : filtered.map((claim) => (
              <tr
                key={claim.claim_id || claim.id}
                onClick={() => onSelectClaim?.(claim)}
                className="border-t border-border hover:bg-background cursor-pointer transition-colors duration-150"
              >
                <td className="px-4 py-3 font-medium text-accent">
                  <span>{claim.claim_number || claim.claim_id || claim.id}</span>
                  {((claim.complexity_score || 0) >= 7 || (claim.total_claimed_amount || 0) >= 5000) && (
                    <span className="ml-2 inline-flex rounded-full bg-warning/10 px-2 py-0.5 text-[10px] font-semibold text-warning">High priority</span>
                  )}
                </td>
                <td className="px-4 py-3 text-primary">{claim.policy_number}</td>
                <td className="px-4 py-3"><StatusChip status={(claim.status || '').toLowerCase().replace(/_/g, '-')} /></td>
                <td className="px-4 py-3 text-primary">${(claim.total_claimed_amount || 0).toLocaleString()}</td>
                <td className="px-4 py-3 text-primary">{Number(claim.complexity_score || 0).toFixed(1)}</td>
                <td className="px-4 py-3 text-primary">{claim.compliance_flags?.length || 0}</td>
                <td className="px-4 py-3 text-secondary">{claim.created_at ? new Date(claim.created_at).toLocaleDateString() : '—'}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
};

export default ClaimsTable;
