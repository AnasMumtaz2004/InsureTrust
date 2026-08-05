import AiAvatar from '../../assets/AiAvatar';

const mockDebate = [
  {
    agent: 'Underwriting Agent',
    position: 'Approve',
    message: 'The claim is well-documented with all necessary medical records. The treatment aligns with the diagnosis, and the hospital is within our network. Coverage is confirmed under the Health Premium Plan.',
    timestamp: '14:32:01',
  },
  {
    agent: 'Fraud Detection Agent',
    position: 'Flag for Review',
    message: 'While the claim appears legitimate, the total amount is 15% above the average for this procedure type in this region. Requesting additional verification of itemized billing.',
    timestamp: '14:32:15',
  },
  {
    agent: 'Underwriting Agent',
    position: 'Approve',
    message: 'The 15% variance is within acceptable range given the hospital tier (Tier 1 facility). Itemized bills have been cross-referenced with standard procedure codes. No discrepancy found.',
    timestamp: '14:32:28',
  },
  {
    agent: 'Compliance Agent',
    position: 'Approve',
    message: 'Regulatory checks passed. All documentation meets KYC requirements. No prior claims flagged for this policyholder. Recommending approval with standard deductible application.',
    timestamp: '14:32:45',
  },
];

const DebatePanel = () => {
  return (
    <div className="space-y-4">
      <div className="flex items-center justify-between mb-2">
        <h3 className="text-sm font-semibold text-primary">AI Debate Transcript</h3>
        <span className="text-xs text-secondary">4 exchanges</span>
      </div>

      {mockDebate.map((entry, index) => (
        <div key={index} className="flex gap-3">
          <AiAvatar size={28} className="shrink-0 mt-0.5" />
          <div className="flex-1 bg-background border border-border rounded-lg p-3">
            <div className="flex items-center justify-between mb-1">
              <div className="flex items-center gap-2">
                <span className="text-xs font-semibold text-primary">{entry.agent}</span>
                <span className={`text-xs font-medium px-2 py-0.5 rounded-full ${
                  entry.position === 'Approve'
                    ? 'bg-accent/10 text-accent'
                    : 'bg-warning/10 text-warning'
                }`}>
                  {entry.position}
                </span>
              </div>
              <span className="text-xs text-secondary">{entry.timestamp}</span>
            </div>
            <p className="text-xs text-secondary leading-relaxed">{entry.message}</p>
          </div>
        </div>
      ))}
    </div>
  );
};

export default DebatePanel;
