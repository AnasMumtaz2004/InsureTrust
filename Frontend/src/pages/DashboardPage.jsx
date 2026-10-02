import { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { DollarSign, FileText, Clock, PiggyBank, Plus } from 'lucide-react';
import { Card, ChatComposer, Drawer, KpiCard, StatusChip } from '../components/shared';
import { ClaimDrawer } from '../components/client';
import { useAuth } from '../auth/useAuth';
import { getClaims, getClaimExplanation, postClaimExplanationQuestion } from '../api/clientApi';

const formatStatus = (status = '') => status.toLowerCase().replace(/_/g, ' ')
  .replace(/\b\w/g, (letter) => letter.toUpperCase());

const DashboardPage = () => {
  const [claimDrawerOpen, setClaimDrawerOpen] = useState(false);
  const [claims, setClaims] = useState([]);
  const [loading, setLoading] = useState(true);
  const [refreshKey, setRefreshKey] = useState(0);
  const [submitNotice, setSubmitNotice] = useState('');
  const [selectedClaim, setSelectedClaim] = useState(null);
  const [explanation, setExplanation] = useState(null);
  const [explanationLoading, setExplanationLoading] = useState(false);
  const [explanationError, setExplanationError] = useState('');
  const [chatMessages, setChatMessages] = useState([]);
  const [chatLoading, setChatLoading] = useState(false);
  const navigate = useNavigate();
  const { token } = useAuth();

  useEffect(() => {
    let active = true;
    const loadClaims = async () => {
      if (!token) return;
      setLoading(true);
      try {
        const data = await getClaims(token, 50);
        if (active) setClaims(data || []);
      } catch (error) {
        console.error(error);
        if (active) setClaims([]);
      } finally {
        if (active) setLoading(false);
      }
    };
    loadClaims();
    return () => { active = false; };
  }, [token, refreshKey]);

  useEffect(() => {
    let active = true;
    const loadExplanation = async () => {
      if (!selectedClaim || !token) return;
      setExplanation(null);
      setExplanationError('');
      setExplanationLoading(true);
      try {
        const data = await getClaimExplanation(selectedClaim.id, token);
        if (active) setExplanation(data);
      } catch (error) {
        if (active) setExplanationError(error.message || 'Unable to load the claim explanation.');
      } finally {
        if (active) setExplanationLoading(false);
      }
    };
    loadExplanation();
    return () => { active = false; };
  }, [selectedClaim, token]);

  const totalClaimed = claims.reduce((sum, claim) => sum + (claim.total_claimed_amount || 0), 0);
  const inProgressCount = claims.filter((claim) => ['IN_REVIEW', 'PENDING_APPROVAL'].includes(claim.status)).length;

  const handleSubmitted = (claim, uploadResults) => {
    setClaimDrawerOpen(false);
    setRefreshKey((current) => current + 1);
    const failures = uploadResults.filter((result) => !result.uploaded);
    setSubmitNotice(failures.length
      ? `Claim ${claim.claim_number} submitted. ${failures.length} document${failures.length === 1 ? '' : 's'} could not be uploaded.`
      : `Claim ${claim.claim_number} submitted successfully.`);
  };

  const askQuestion = async (question) => {
    if (!selectedClaim || !token || !question.trim() || chatLoading) return;
    setChatMessages((current) => [...current, { role: 'user', content: question }]);
    setChatLoading(true);
    try {
      const response = await postClaimExplanationQuestion(selectedClaim.id, question, token);
      setChatMessages((current) => [...current, { role: 'assistant', content: response.answer }]);
    } catch (error) {
      setChatMessages((current) => [...current, {
        role: 'assistant',
        content: error.message || 'I could not answer that question right now.',
      }]);
    } finally {
      setChatLoading(false);
    }
  };

  const closeDetails = () => {
    setSelectedClaim(null);
    setExplanation(null);
    setChatMessages([]);
  };

  return (
    <>
      <div className="space-y-6">
        {submitNotice && (
          <div role="status" className="rounded-md border border-accent/30 bg-accent/5 px-4 py-3 text-sm text-primary">
            {submitNotice}
            <button type="button" onClick={() => setSubmitNotice('')} aria-label="Dismiss claim submission notice" className="ml-3 font-medium text-accent hover:underline">Dismiss</button>
          </div>
        )}

        <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-4">
          <KpiCard title="Claims Filed" value={loading ? '…' : claims.length} linkText="View claims" icon={FileText} />
          <KpiCard title="Total Claimed" value={loading ? '…' : `$${totalClaimed.toLocaleString()}`} linkText="See details" icon={DollarSign} />
          <KpiCard title="Claims in Progress" value={loading ? '…' : inProgressCount} linkText="Open claims" icon={Clock} />
          <KpiCard title="Coverage Ready" value={loading ? '…' : 'Live'} linkText="Ask AI" icon={PiggyBank} />
        </div>

        <Card className="p-5">
          <div className="mb-4 flex items-center justify-between gap-3">
            <h3 className="text-base font-semibold text-primary">Your Claims</h3>
            <button type="button" onClick={() => navigate('/assistant')} className="text-xs font-medium text-accent hover:underline">Ask AI Assistant</button>
          </div>

          {loading ? (
            <div className="py-10 text-center text-sm text-secondary">Loading your claims…</div>
          ) : claims.length === 0 ? (
            <div className="py-10 text-center text-sm text-secondary">No claims yet. File your first claim to see it here.</div>
          ) : (
            <div className="space-y-3">
              {claims.map((claim) => (
                <button
                  key={claim.id}
                  type="button"
                  onClick={() => {
                    setChatMessages([]);
                    setSelectedClaim(claim);
                  }}
                  className="block w-full rounded-md border border-border p-4 text-left transition-colors hover:border-accent focus:outline-none focus:ring-2 focus:ring-accent/40"
                  aria-label={`View claim ${claim.claim_number}, ${formatStatus(claim.status)}`}
                >
                  <div className="flex flex-wrap items-center justify-between gap-3">
                    <div className="min-w-0">
                      <p className="break-all font-semibold text-primary">{claim.claim_number}</p>
                      <p className="mt-1 text-sm text-secondary">{claim.policy_number}</p>
                    </div>
                    <StatusChip status={claim.status || 'default'} label={formatStatus(claim.status || 'Unknown')} />
                  </div>
                  <div className="mt-3 flex flex-wrap items-center justify-between gap-2 text-sm text-secondary">
                    <span>Claimed: ${Number(claim.total_claimed_amount || 0).toLocaleString()}</span>
                    <span>Approved: ${Number(claim.approved_amount || 0).toLocaleString()}</span>
                  </div>
                </button>
              ))}
            </div>
          )}
        </Card>

        <button
          type="button"
          onClick={() => setClaimDrawerOpen(true)}
          className="fixed bottom-6 right-6 z-30 flex items-center gap-2 rounded-full bg-accent p-4 text-white shadow-lg transition-colors hover:bg-accent/90"
          aria-label="File new claim"
        >
          <Plus size={20} />
          <span className="hidden text-sm font-medium lg:inline">File New Claim</span>
        </button>
      </div>

      <ClaimDrawer
        isOpen={claimDrawerOpen}
        onClose={() => setClaimDrawerOpen(false)}
        onSubmitted={handleSubmitted}
      />

      <Drawer isOpen={!!selectedClaim} onClose={closeDetails} title={selectedClaim?.claim_number || 'Claim details'} width="max-w-2xl">
        {selectedClaim && (
          <div className="space-y-6">
            <div className="flex flex-wrap items-center justify-between gap-3 border-b border-border pb-4">
              <div>
                <p className="text-sm text-secondary">{selectedClaim.policy_number}</p>
                <p className="mt-1 text-sm text-secondary">Claimed ${Number(selectedClaim.total_claimed_amount || 0).toLocaleString()}</p>
              </div>
              <StatusChip status={selectedClaim.status || 'default'} label={formatStatus(selectedClaim.status || 'Unknown')} />
            </div>

            {explanationLoading ? (
              <p className="text-sm text-secondary">Loading claim explanation…</p>
            ) : explanationError ? (
              <p role="alert" className="text-sm text-red-600">{explanationError}</p>
            ) : explanation && (
              <>
                <section>
                  <h4 className="text-sm font-semibold text-primary">Summary</h4>
                  <p className="mt-2 whitespace-pre-line text-sm leading-6 text-secondary">{explanation.summary}</p>
                </section>

                <section>
                  <h4 className="text-sm font-semibold text-primary">Policy basis</h4>
                  {explanation.policy_basis?.length ? (
                    <ul className="mt-2 list-disc space-y-1 pl-5 text-sm text-secondary">
                      {explanation.policy_basis.map((basis, index) => <li key={`${basis}-${index}`}>{basis}</li>)}
                    </ul>
                  ) : <p className="mt-2 text-sm text-secondary">No policy clauses were returned.</p>}
                </section>

                {explanation.citations?.length > 0 && (
                  <section>
                    <h4 className="text-sm font-semibold text-primary">Citations</h4>
                    <ul className="mt-2 space-y-1 text-sm text-secondary">
                      {explanation.citations.map((citation, index) => <li key={`${citation}-${index}`} className="break-words">{citation}</li>)}
                    </ul>
                  </section>
                )}

                <section className="border-t border-border pt-5">
                  <h4 className="text-sm font-semibold text-primary">Questions about this decision</h4>
                  <div className="mt-3 flex flex-wrap gap-2">
                    {(explanation.frequently_asked_questions || []).map((faq, index) => (
                      <button key={`${faq.question}-${index}`} type="button" onClick={() => askQuestion(faq.question)} disabled={chatLoading} className="rounded-md border border-border px-3 py-2 text-left text-xs text-primary hover:border-accent disabled:opacity-50">
                        {faq.question}
                      </button>
                    ))}
                  </div>
                  {chatMessages.length > 0 && (
                    <div className="mt-4 max-h-56 space-y-3 overflow-y-auto" aria-live="polite">
                      {chatMessages.map((message, index) => (
                        <div key={`${message.role}-${index}`} className={`max-w-[90%] break-words rounded-md px-3 py-2 text-sm ${message.role === 'user' ? 'ml-auto bg-primary text-white' : 'bg-background text-primary'}`}>
                          {message.content}
                        </div>
                      ))}
                      {chatLoading && <p className="text-xs text-secondary">Preparing an answer…</p>}
                    </div>
                  )}
                  <div className="mt-4 -mx-6 -mb-6">
                    <ChatComposer onSend={askQuestion} disabled={chatLoading || explanationLoading} placeholder="Ask about your claim..." />
                  </div>
                </section>
              </>
            )}
          </div>
        )}
      </Drawer>
    </>
  );
};

export default DashboardPage;