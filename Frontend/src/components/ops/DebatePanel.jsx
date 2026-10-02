const DebatePanel = ({ transcript }) => {
  const approvalArguments = transcript?.pro_approval_view || transcript?.pro_approval_arguments || [];
  const denialArguments = transcript?.pro_denial_view || transcript?.pro_denial_arguments || [];
  const synthesis = transcript?.synthesis || transcript?.reconciliation_summary;
  const hasDebate = approvalArguments.length || denialArguments.length || synthesis;

  if (!hasDebate) {
    return <p className="py-8 text-center text-sm text-secondary">No debate was needed for this claim.</p>;
  }

  return (
    <div className="space-y-5">
      <h3 className="text-sm font-semibold text-primary">Debate transcript</h3>
      <section>
        <h4 className="text-xs font-semibold uppercase text-secondary">Pro-approval view</h4>
        {approvalArguments.length ? (
          <ul className="mt-2 list-disc space-y-2 pl-5 text-sm leading-5 text-secondary">
            {approvalArguments.map((argument, index) => <li key={`approval-${index}`}>{argument}</li>)}
          </ul>
        ) : <p className="mt-2 text-xs text-secondary">No pro-approval arguments were recorded.</p>}
      </section>
      <section>
        <h4 className="text-xs font-semibold uppercase text-secondary">Pro-denial view</h4>
        {denialArguments.length ? (
          <ul className="mt-2 list-disc space-y-2 pl-5 text-sm leading-5 text-secondary">
            {denialArguments.map((argument, index) => <li key={`denial-${index}`}>{argument}</li>)}
          </ul>
        ) : <p className="mt-2 text-xs text-secondary">No pro-denial arguments were recorded.</p>}
      </section>
      {synthesis && (
        <section className="border-t border-border pt-4">
          <h4 className="text-xs font-semibold uppercase text-secondary">Synthesis</h4>
          <p className="mt-2 text-sm leading-5 text-primary">{synthesis}</p>
        </section>
      )}
      {transcript.confidence_delta != null && (
        <p className="text-xs text-secondary">Confidence delta: {Number(transcript.confidence_delta).toFixed(2)}</p>
      )}
    </div>
  );
};

export default DebatePanel;