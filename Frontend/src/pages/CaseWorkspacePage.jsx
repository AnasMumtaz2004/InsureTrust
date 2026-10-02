import { useEffect, useState } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { ArrowLeft, User, Calendar, DollarSign, FileText } from 'lucide-react';
import { Card, Tabs, Timeline, StatusChip } from '../components/shared';
import { ReasoningPanel, DebatePanel, DecisionActionBar } from '../components/ops';
import { useAuth } from '../auth/useAuth';
import {
  getClaimById,
  getCaseGraphState,
  getDebateTranscript,
  getAuditTrail,
  submitDecisionAction,
} from '../api/clientApi';

const rightPanelTabs = [
  { key: 'recommendation', label: 'Recommendation' },
  { key: 'reasoning', label: 'Reasoning Trail' },
  { key: 'debate', label: 'Debate Transcript' },
];

const formatStatus = (status = '') => status.toLowerCase().replace(/_/g, '-')
  .replace(/\b\w/g, (letter) => letter.toUpperCase());

const CaseWorkspacePage = () => {
  const { id } = useParams();
  const navigate = useNavigate();
  const [activeTab, setActiveTab] = useState('recommendation');
  const [claim, setClaim] = useState(null);
  const [graphState, setGraphState] = useState({});
  const [debateTranscript, setDebateTranscript] = useState(null);
  const [auditTrail, setAuditTrail] = useState([]);
  const [loading, setLoading] = useState(true);
  const [loadError, setLoadError] = useState('');
  const [actionBanner, setActionBanner] = useState(null);
  const [submittingAction, setSubmittingAction] = useState(false);
  const { token } = useAuth();

  useEffect(() => {
    let active = true;
    const loadWorkspace = async () => {
      if (!token || !id) return;
      setLoading(true);
      setLoadError('');
      const [claimResult, graphResult, debateResult, auditResult] = await Promise.allSettled([
        getClaimById(id, token),
        getCaseGraphState(id, token),
        getDebateTranscript(id, token),
        getAuditTrail(id, token),
      ]);

      if (!active) return;
      if (claimResult.status === 'fulfilled') {
        setClaim(claimResult.value);
      } else {
        setClaim(null);
        setLoadError(claimResult.reason?.message || 'Unable to load the selected claim.');
      }

      const graphValues = graphResult.status === 'fulfilled' ? graphResult.value?.values || {} : {};
      setGraphState({ ...(claimResult.status === 'fulfilled' ? claimResult.value : {}), ...graphValues });

      if (debateResult.status === 'fulfilled') {
        setDebateTranscript(debateResult.value);
      } else if (debateResult.reason?.message?.includes('404')) {
        setDebateTranscript(null);
      } else {
        setDebateTranscript(graphValues.debate_transcript || null);
      }

      setAuditTrail(auditResult.status === 'fulfilled' && Array.isArray(auditResult.value) ? auditResult.value : []);
      setLoading(false);
    };

    loadWorkspace();
    return () => { active = false; };
  }, [id, token]);

  const handleAction = async (action, payload) => {
    setSubmittingAction(true);
    setActionBanner(null);
    try {
      const result = await submitDecisionAction(id, { action, ...payload }, token);
      setActionBanner({
        type: 'success',
        message: result.message || `Claim ${action.toLowerCase()} action completed.`,
      });
      window.setTimeout(() => navigate('/ops/queue'), 1400);
    } catch (error) {
      setActionBanner({ type: 'error', message: error.message || 'Unable to submit this decision.' });
    } finally {
      setSubmittingAction(false);
    }
  };

  if (loading) {
    return <div className="text-sm text-secondary">Loading claim workspace…</div>;
  }

  if (!claim) {
    return (
      <div className="space-y-4">
        <button type="button" onClick={() => navigate('/ops/queue')} className="flex items-center gap-2 text-sm text-secondary hover:text-primary">
          <ArrowLeft size={16} /> Back to Queue
        </button>
        <p role="alert" className="text-sm text-red-600">{loadError || 'Unable to load the selected claim.'}</p>
      </div>
    );
  }

  const finalDecision = graphState.final_decision || graphState.draft_decision || claim.final_decision || {};
  const itemizedPayout = finalDecision.itemized_payout || graphState.itemized_payout || {};
  const citations = claim.citations?.length ? claim.citations : graphState.citations || [];
  const timelineItems = auditTrail.map((entry) => ({
    title: `${entry.agent_name || 'System'} · ${entry.action || 'Event'}`,
    description: entry.state_snapshot?.status ? `Status: ${entry.state_snapshot.status}` : undefined,
    timestamp: entry.timestamp ? new Date(entry.timestamp).toLocaleString() : '',
    active: true,
  }));

  return (
    <div className="pb-32">
      <button
        type="button"
        onClick={() => navigate('/ops/queue')}
        className="mb-4 flex items-center gap-2 text-sm text-secondary hover:text-primary"
      >
        <ArrowLeft size={16} /> Back to Queue
      </button>

      <div className="mb-6 flex flex-wrap items-center justify-between gap-4">
        <div>
          <h2 className="text-xl font-bold text-primary">{claim.claim_number || id}</h2>
          <p className="mt-0.5 text-sm text-secondary">{claim.policy_number} · Claimant {claim.claimant_id}</p>
        </div>
        <StatusChip status={claim.status || 'default'} label={formatStatus(claim.status || 'Unknown')} />
      </div>

      {actionBanner && (
        <div role={actionBanner.type === 'error' ? 'alert' : 'status'} className={`mb-5 rounded-md border px-4 py-3 text-sm ${actionBanner.type === 'success' ? 'border-accent/30 bg-accent/5 text-primary' : 'border-red-200 bg-red-50 text-red-600'}`}>
          {actionBanner.message}
        </div>
      )}
      {claim.status === 'PROCESSING_FAILED' && (
        <div role="status" className="mb-5 rounded-md border border-warning/30 bg-warning/10 px-4 py-3 text-sm text-primary">
          Processing failed. Contact an administrator.
        </div>
      )}

      <div className="grid gap-6 lg:grid-cols-2">
        <div className="space-y-5">
          <div className="grid grid-cols-2 gap-4">
            <Card className="p-4">
              <div className="flex items-center gap-3"><DollarSign size={18} className="text-accent" /><div><p className="text-xs text-secondary">Claim Amount</p><p className="text-lg font-bold text-primary">${Number(claim.total_claimed_amount || 0).toLocaleString()}</p></div></div>
            </Card>
            <Card className="p-4">
              <div className="flex items-center gap-3"><Calendar size={18} className="text-accent" /><div><p className="text-xs text-secondary">Date of Incident</p><p className="text-sm font-bold text-primary">{graphState.incident_date || 'Not recorded'}</p></div></div>
            </Card>
            <Card className="p-4">
              <div className="flex items-center gap-3"><FileText size={18} className="text-accent" /><div className="min-w-0"><p className="text-xs text-secondary">Policy Number</p><p className="break-all text-sm font-semibold text-primary">{claim.policy_number}</p></div></div>
            </Card>
            <Card className="p-4">
              <div className="flex items-center gap-3"><User size={18} className="text-accent" /><div className="min-w-0"><p className="text-xs text-secondary">Claimant</p><p className="break-all text-sm font-semibold text-primary">{claim.claimant_id}</p></div></div>
            </Card>
          </div>

          <Card className="p-5">
            <h3 className="mb-3 text-sm font-semibold text-primary">Claimant Statement</h3>
            <p className="whitespace-pre-line text-sm leading-relaxed text-secondary">{graphState.description || 'No claim description is available.'}</p>
          </Card>

          <Card className="p-5">
            <h3 className="mb-4 text-sm font-semibold text-primary">Claim Timeline</h3>
            {timelineItems.length ? <Timeline items={timelineItems} /> : <p className="text-sm text-secondary">No audit events are available for this claim.</p>}
          </Card>
        </div>

        <Card>
          <Tabs tabs={rightPanelTabs} activeKey={activeTab} onChange={setActiveTab} className="px-5" />
          <div className="p-5">
            {activeTab === 'recommendation' && (
              <div className="space-y-5">
                <section>
                  <h3 className="text-sm font-semibold text-primary">Decision rationale</h3>
                  <p className="mt-2 whitespace-pre-line text-sm leading-6 text-secondary">
                    {finalDecision.rationale || graphState.rationale || 'No recommendation rationale is available.'}
                  </p>
                </section>
                <section>
                  <h4 className="text-xs font-semibold uppercase text-secondary">Citations</h4>
                  {citations.length ? (
                    <ul className="mt-2 space-y-2 text-sm text-secondary">{citations.map((citation, index) => <li key={`${citation}-${index}`} className="break-words">{citation}</li>)}</ul>
                  ) : <p className="mt-2 text-xs text-secondary">No citations were recorded.</p>}
                </section>
                <section>
                  <h4 className="text-xs font-semibold uppercase text-secondary">Itemized payout</h4>
                  {Object.keys(itemizedPayout).length ? (
                    <dl className="mt-2 space-y-2">
                      {Object.entries(itemizedPayout).map(([label, value]) => (
                        <div key={label} className="flex flex-wrap justify-between gap-2 border-b border-border pb-2 text-sm">
                          <dt className="text-secondary">{label.replace(/_/g, ' ')}</dt>
                          <dd className="font-medium text-primary">{typeof value === 'number' ? `$${value.toLocaleString()}` : typeof value === 'object' ? JSON.stringify(value) : String(value)}</dd>
                        </div>
                      ))}
                    </dl>
                  ) : <p className="mt-2 text-xs text-secondary">No itemized payout is available.</p>}
                </section>
              </div>
            )}
            {activeTab === 'reasoning' && <ReasoningPanel graphState={graphState} />}
            {activeTab === 'debate' && <DebatePanel transcript={debateTranscript || graphState.debate_transcript} />}
          </div>
        </Card>
      </div>

      {claim.status === 'PENDING_APPROVAL' && (
        <DecisionActionBar
          disabled={claim.status !== 'PENDING_APPROVAL'}
          submitting={submittingAction}
          onApprove={(payload) => handleAction('APPROVE', payload)}
          onOverride={(payload) => handleAction('OVERRIDE', payload)}
          onSendBack={(payload) => handleAction('SEND_BACK', payload)}
        />
      )}
    </div>
  );
};

export default CaseWorkspacePage;