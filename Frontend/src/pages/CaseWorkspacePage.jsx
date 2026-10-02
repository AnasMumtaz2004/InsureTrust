import { useEffect, useState } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { ArrowLeft, User, Calendar, DollarSign, FileText } from 'lucide-react';
import { Card, Tabs, Timeline, StatusChip } from '../components/shared';
import { ReasoningPanel, DebatePanel, DecisionActionBar } from '../components/ops';
import { RecommendationCard } from '../components/client';
import { useAuth } from '../auth/useAuth';
import { getClaimById } from '../api/clientApi';

const rightPanelTabs = [
  { key: 'recommendation', label: 'Recommendation' },
  { key: 'reasoning', label: 'Reasoning Trail' },
  { key: 'debate', label: 'Debate Transcript' },
];

const CaseWorkspacePage = () => {
  const { id } = useParams();
  const navigate = useNavigate();
  const [activeTab, setActiveTab] = useState('recommendation');
  const [claim, setClaim] = useState(null);
  const [loading, setLoading] = useState(true);
  const { token } = useAuth();

  useEffect(() => {
    const loadClaim = async () => {
      if (!token || !id) return;
      try {
        const data = await getClaimById(id, token);
        setClaim(data);
      } catch (error) {
        console.error(error);
      } finally {
        setLoading(false);
      }
    };

    loadClaim();
  }, [id, token]);

  const handleSendBack = () => {
    alert('Claim sent back for additional information.');
    navigate('/ops/queue');
  };

  const handleOverride = (reason) => {
    alert(`Claim overridden. Reason: ${reason}`);
    navigate('/ops/queue');
  };

  const handleApprove = () => {
    alert('Claim approved successfully.');
    navigate('/ops/queue');
  };

  if (loading) {
    return <div className="text-sm text-secondary">Loading claim workspace…</div>;
  }

  if (!claim) {
    return <div className="text-sm text-secondary">Unable to load the selected claim.</div>;
  }

  const timelineItems = [
    { title: 'Claim Submitted', timestamp: new Date(claim.created_at).toLocaleString(), active: true },
    { title: 'AI Review Completed', timestamp: claim.final_decision ? 'Decision generated' : 'Analyzing policy and documents', active: true },
    { title: 'Human Review', timestamp: claim.status, active: claim.status !== 'APPROVED' },
  ];

  const recommendationFeatures = [
    claim.final_decision ? `Decision: ${claim.final_decision?.decision_type} - ${claim.final_decision?.rationale}` : 'Decision is still being prepared',
    `Policy clauses reviewed: ${claim.policy_clauses?.length || 0}`,
    `Compliance flags: ${claim.compliance_flags?.length || 0}`,
    `Citations found: ${claim.citations?.length || 0}`,
  ];

  return (
    <div className="pb-24">
      {/* Back button */}
      <button
        onClick={() => navigate('/ops/queue')}
        className="flex items-center gap-2 text-sm text-secondary hover:text-primary mb-4 cursor-pointer"
      >
        <ArrowLeft size={16} />
        Back to Queue
      </button>

      {/* Header */}
      <div className="flex flex-wrap items-center justify-between gap-4 mb-6">
        <div>
          <h2 className="text-xl font-bold text-primary">{claim.claim_number || id}</h2>
          <p className="text-sm text-secondary mt-0.5">{claim.policy_number} • Claimant {claim.claimant_id}</p>
        </div>
        <StatusChip status={(claim.status || '').toLowerCase().replace(/ /g, '-')} label={claim.status || 'In Review'} />
      </div>

      {/* Two-panel layout */}
      <div className="grid lg:grid-cols-2 gap-6">
        {/* LEFT PANEL — Claim facts */}
        <div className="space-y-5">
          {/* Stat boxes */}
          <div className="grid grid-cols-2 gap-4">
            <Card className="p-4">
              <div className="flex items-center gap-3">
                <DollarSign size={18} className="text-accent" />
                <div>
                  <p className="text-xs text-secondary">Claim Amount</p>
                  <p className="text-lg font-bold text-primary">${(claim.total_claimed_amount || 0).toLocaleString()}</p>
                </div>
              </div>
            </Card>
            <Card className="p-4">
              <div className="flex items-center gap-3">
                <Calendar size={18} className="text-accent" />
                <div>
                  <p className="text-xs text-secondary">Date of Incident</p>
                  <p className="text-lg font-bold text-primary">{new Date(claim.created_at).toLocaleDateString()}</p>
                </div>
              </div>
            </Card>
            <Card className="p-4">
              <div className="flex items-center gap-3">
                <FileText size={18} className="text-accent" />
                <div>
                  <p className="text-xs text-secondary">Policy Number</p>
                  <p className="text-sm font-semibold text-primary">{claim.policy_number}</p>
                </div>
              </div>
            </Card>
            <Card className="p-4">
              <div className="flex items-center gap-3">
                <User size={18} className="text-accent" />
                <div>
                  <p className="text-xs text-secondary">Claimant</p>
                  <p className="text-sm font-semibold text-primary">{claim.claimant_id}</p>
                </div>
              </div>
            </Card>
          </div>

          {/* Claimant statement */}
          <Card className="p-5">
            <h3 className="text-sm font-semibold text-primary mb-3">Claimant Statement</h3>
            <p className="text-sm text-secondary leading-relaxed">The adjudication workflow has loaded claim {claim.claim_number || id} with status {claim.status}. Review the recommendation, audit trail, and debate details below.</p>
          </Card>

          {/* Timeline */}
          <Card className="p-5">
            <h3 className="text-sm font-semibold text-primary mb-4">Claim Timeline</h3>
            <Timeline items={timelineItems} />
          </Card>
        </div>

        {/* RIGHT PANEL — Tabbed content */}
        <div>
          <Card>
            <Tabs tabs={rightPanelTabs} activeKey={activeTab} onChange={setActiveTab} className="px-5" />
            <div className="p-5">
              {activeTab === 'recommendation' && (
                <div className="space-y-4">
                  <div className="bg-accent/5 border border-accent/20 rounded-lg p-4 mb-4">
                    <p className="text-sm font-semibold text-accent">AI Recommendation</p>
                    <p className="text-xs text-secondary mt-1">
                      The current workflow is using the live claim state from the backend and surfaces the latest decision context for review.
                    </p>
                  </div>
                  <RecommendationCard
                    compact
                    title="Approval Details"
                    features={recommendationFeatures}
                  />
                </div>
              )}
              {activeTab === 'reasoning' && <ReasoningPanel />}
              {activeTab === 'debate' && <DebatePanel />}
            </div>
          </Card>
        </div>
      </div>

      {/* Fixed bottom action bar */}
      <DecisionActionBar
        onSendBack={handleSendBack}
        onOverride={handleOverride}
        onApprove={handleApprove}
      />
    </div>
  );
};

export default CaseWorkspacePage;
