import { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { FileText, DollarSign, Clock, PiggyBank, Plus } from 'lucide-react';
import { Card, KpiCard } from '../components/shared';
import { ClaimDrawer } from '../components/client';
import { useAuth } from '../auth/useAuth';
import { getClaims } from '../api/clientApi';

const DashboardPage = () => {
  const [claimDrawerOpen, setClaimDrawerOpen] = useState(false);
  const [claims, setClaims] = useState([]);
  const [loading, setLoading] = useState(true);
  const navigate = useNavigate();
  const { token } = useAuth();

  useEffect(() => {
    const loadClaims = async () => {
      if (!token) return;
      try {
        const data = await getClaims(token, 10);
        setClaims(data || []);
      } catch (error) {
        console.error(error);
        setClaims([]);
      } finally {
        setLoading(false);
      }
    };

    loadClaims();
  }, [token]);

  const totalClaimed = claims.reduce((sum, claim) => sum + (claim.total_claimed_amount || 0), 0);
  const inProgressCount = claims.filter((claim) => claim.status === 'IN_REVIEW').length;

  return (
    <>
      <div className="space-y-6">
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
          <KpiCard title="Claims Filed" value={loading ? '…' : claims.length} linkText="View claims" icon={FileText} />
          <KpiCard title="Total Claimed" value={loading ? '…' : `$${totalClaimed.toLocaleString()}`} linkText="See details" icon={DollarSign} />
          <KpiCard title="Claims in Progress" value={loading ? '…' : inProgressCount} linkText="Open claims" icon={Clock} />
          <KpiCard title="Coverage Ready" value={loading ? '…' : 'Live'} linkText="Ask AI" icon={PiggyBank} />
        </div>

        <Card className="p-5">
          <div className="flex items-center justify-between mb-4">
            <h3 className="text-base font-semibold text-primary">Your Claims</h3>
            <button onClick={() => navigate('/assistant')} className="text-xs text-accent font-medium hover:underline cursor-pointer">Ask AI Assistant</button>
          </div>

          {loading ? (
            <div className="py-10 text-center text-sm text-secondary">Loading your claims…</div>
          ) : claims.length === 0 ? (
            <div className="py-10 text-center text-sm text-secondary">No claims yet — file your first claim to see it here.</div>
          ) : (
            <div className="space-y-3">
              {claims.map((claim) => (
                <div key={claim.id} className="border border-border rounded-lg p-4">
                  <div className="flex items-center justify-between">
                    <div>
                      <p className="font-semibold text-primary">{claim.claim_number}</p>
                      <p className="text-sm text-secondary">{claim.policy_number}</p>
                    </div>
                    <span className="text-sm text-accent">{claim.status}</span>
                  </div>
                  <div className="mt-3 flex items-center justify-between text-sm text-secondary">
                    <span>Claimed: ${claim.total_claimed_amount?.toLocaleString()}</span>
                    <span>Approved: ${claim.approved_amount?.toLocaleString()}</span>
                  </div>
                </div>
              ))}
            </div>
          )}
        </Card>

        <button
          onClick={() => setClaimDrawerOpen(true)}
          className="fixed bottom-6 right-6 bg-accent text-white p-4 rounded-full shadow-lg hover:bg-accent/90 cursor-pointer transition-colors duration-150 z-30 flex items-center gap-2"
        >
          <Plus size={20} />
          <span className="text-sm font-medium hidden lg:inline">File New Claim</span>
        </button>
      </div>

      {/* Claim Drawer */}
      <ClaimDrawer isOpen={claimDrawerOpen} onClose={() => setClaimDrawerOpen(false)} />
    </>
  );
};

export default DashboardPage;
