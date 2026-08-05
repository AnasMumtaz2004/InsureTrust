import { useState } from 'react';
import { ArrowLeft, AlertTriangle, Check } from 'lucide-react';
import { Button } from '../shared';

const DecisionActionBar = ({ onSendBack, onOverride, onApprove }) => {
  const [showOverrideReason, setShowOverrideReason] = useState(false);
  const [overrideReason, setOverrideReason] = useState('');

  const handleOverrideConfirm = () => {
    if (overrideReason.trim()) {
      onOverride?.(overrideReason.trim());
      setShowOverrideReason(false);
      setOverrideReason('');
    }
  };

  return (
    <div className="fixed bottom-0 left-0 right-0 bg-white border-t border-border z-40">
      {/* Override reason field */}
      {showOverrideReason && (
        <div className="px-6 py-4 border-b border-border bg-warning/5">
          <label className="block text-sm font-medium text-primary mb-2">
            <AlertTriangle size={14} className="inline text-warning mr-1" />
            Override requires a mandatory reason
          </label>
          <textarea
            value={overrideReason}
            onChange={(e) => setOverrideReason(e.target.value)}
            placeholder="Explain why this AI recommendation should be overridden..."
            rows={2}
            className="w-full px-4 py-2.5 border border-border rounded-md text-sm bg-white focus:outline-none focus:border-accent resize-none"
          />
          <div className="flex justify-end gap-2 mt-2">
            <Button variant="outline" size="sm" onClick={() => setShowOverrideReason(false)}>
              Cancel
            </Button>
            <Button
              variant="danger"
              size="sm"
              onClick={handleOverrideConfirm}
              disabled={!overrideReason.trim()}
            >
              Confirm Override
            </Button>
          </div>
        </div>
      )}

      {/* Action buttons */}
      <div className="flex items-center justify-between px-6 py-3">
        <Button variant="outline" size="md" onClick={onSendBack}>
          <ArrowLeft size={16} />
          Send Back
        </Button>
        <div className="flex gap-3">
          <Button
            variant={showOverrideReason ? 'outline' : 'danger'}
            size="md"
            onClick={() => setShowOverrideReason(!showOverrideReason)}
          >
            <AlertTriangle size={16} />
            Override
          </Button>
          <Button variant="secondary" size="md" onClick={onApprove}>
            <Check size={16} />
            Approve
          </Button>
        </div>
      </div>
    </div>
  );
};

export default DecisionActionBar;
