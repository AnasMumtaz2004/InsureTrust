import { useState } from 'react';
import { ArrowLeft, AlertTriangle, Check } from 'lucide-react';
import { Button } from '../shared';

const fieldClassName = 'w-full rounded-md border border-border bg-white px-3 py-2 text-sm text-primary focus:outline-none focus:border-accent';

const DecisionActionBar = ({ onSendBack, onOverride, onApprove, disabled = false, submitting = false }) => {
  const [openAction, setOpenAction] = useState('');
  const [notes, setNotes] = useState('');
  const [modifiedPayout, setModifiedPayout] = useState('');
  const [decisionType, setDecisionType] = useState('');
  const [error, setError] = useState('');
  const [confirmDeny, setConfirmDeny] = useState(false);
  const isDisabled = disabled || submitting;

  const closeForm = () => {
    setOpenAction('');
    setError('');
    setConfirmDeny(false);
  };

  const handleApprove = () => {
    onApprove?.({ adjudicator_notes: notes.trim() || 'Approved by human adjudicator.' });
  };

  const handleSendBack = () => {
    if (!notes.trim()) {
      setError('Notes are required to send a claim back.');
      return;
    }
    onSendBack?.({ adjudicator_notes: notes.trim() });
  };

  const handleOverride = () => {
    if (!notes.trim()) {
      setError('An override reason is required.');
      return;
    }
    if (!decisionType && modifiedPayout === '') {
      setError('Enter a modified payout or choose a decision type.');
      return;
    }
    if (modifiedPayout !== '' && (!Number.isFinite(Number(modifiedPayout)) || Number(modifiedPayout) < 0)) {
      setError('Payout must be zero or greater.');
      return;
    }

    const payload = {
      adjudicator_notes: notes.trim(),
      ...(modifiedPayout !== '' ? { modified_payout: Number(modifiedPayout) } : {}),
      ...(decisionType ? { decision_type: decisionType } : {}),
    };
    if (decisionType === 'DENY' && !confirmDeny) {
      setConfirmDeny(true);
      return;
    }
    onOverride?.(payload);
  };

  return (
    <div className="fixed bottom-0 left-0 right-0 z-40 border-t border-border bg-white">
      {openAction && (
        <div className="border-b border-border bg-background px-4 py-4 sm:px-6">
          {openAction === 'override' && !confirmDeny && (
            <p className="mb-3 flex items-center gap-2 text-sm font-medium text-primary">
              <AlertTriangle size={15} className="text-warning" /> Override details
            </p>
          )}
          {confirmDeny ? (
            <div role="alert" className="space-y-3">
              <p className="text-sm font-semibold text-primary">Confirm denial override</p>
              <p className="text-xs text-secondary">This will record a DENY decision for this claim. Confirm only if this is intended.</p>
              <div className="flex justify-end gap-2">
                <Button variant="outline" size="sm" onClick={() => setConfirmDeny(false)} disabled={isDisabled}>Go Back</Button>
                <Button variant="danger" size="sm" onClick={handleOverride} disabled={isDisabled}>Confirm DENY</Button>
              </div>
            </div>
          ) : (
            <div className="space-y-3">
              <div>
                <label htmlFor="adjudicator-notes" className="mb-1 block text-xs font-medium text-primary">
                  {openAction === 'approve' ? 'Notes (optional)' : openAction === 'override' ? 'Override reason (required)' : 'Send-back notes (required)'}
                </label>
                <textarea
                  id="adjudicator-notes"
                  value={notes}
                  onChange={(event) => { setNotes(event.target.value); setError(''); }}
                  placeholder={openAction === 'approve' ? 'Add an optional note…' : 'Explain the action…'}
                  rows={2}
                  className={`${fieldClassName} resize-y`}
                  disabled={isDisabled}
                />
              </div>
              {openAction === 'override' && (
                <div className="grid gap-3 sm:grid-cols-2">
                  <div>
                    <label htmlFor="modified-payout" className="mb-1 block text-xs font-medium text-primary">Modified payout</label>
                    <input id="modified-payout" type="number" min="0" step="0.01" value={modifiedPayout} onChange={(event) => { setModifiedPayout(event.target.value); setError(''); }} placeholder="Optional" className={fieldClassName} disabled={isDisabled} />
                  </div>
                  <div>
                    <label htmlFor="decision-type" className="mb-1 block text-xs font-medium text-primary">Decision type</label>
                    <select id="decision-type" value={decisionType} onChange={(event) => { setDecisionType(event.target.value); setConfirmDeny(false); setError(''); }} className={fieldClassName} disabled={isDisabled}>
                      <option value="">No change</option>
                      <option value="APPROVE">Approve</option>
                      <option value="PARTIAL_APPROVE">Partial approve</option>
                      <option value="DENY">Deny</option>
                    </select>
                  </div>
                </div>
              )}
              {error && <p role="alert" className="text-xs text-red-600">{error}</p>}
              <div className="flex justify-end gap-2">
                <Button variant="outline" size="sm" onClick={closeForm} disabled={isDisabled}>Cancel</Button>
                <Button
                  variant={openAction === 'override' ? 'danger' : 'primary'}
                  size="sm"
                  onClick={openAction === 'override' ? handleOverride : openAction === 'send-back' ? handleSendBack : handleApprove}
                  disabled={isDisabled}
                >
                  {submitting ? 'Submitting…' : openAction === 'override' ? 'Continue Override' : openAction === 'send-back' ? 'Send Back' : 'Approve Claim'}
                </Button>
              </div>
            </div>
          )}
        </div>
      )}

      <div className="flex flex-wrap items-center justify-between gap-3 px-4 py-3 sm:px-6">
        <Button variant="outline" size="md" onClick={() => { setOpenAction('send-back'); setNotes(''); setError(''); }} disabled={isDisabled}>
          <ArrowLeft size={16} /> Send Back
        </Button>
        <div className="flex gap-2 sm:gap-3">
          <Button variant="danger" size="md" onClick={() => { setOpenAction('override'); setNotes(''); setError(''); setModifiedPayout(''); setDecisionType(''); setConfirmDeny(false); }} disabled={isDisabled}>
            <AlertTriangle size={16} /> Override
          </Button>
          <Button variant="secondary" size="md" onClick={() => { setOpenAction('approve'); setNotes(''); setError(''); }} disabled={isDisabled}>
            <Check size={16} /> Approve
          </Button>
        </div>
      </div>
    </div>
  );
};

export default DecisionActionBar;