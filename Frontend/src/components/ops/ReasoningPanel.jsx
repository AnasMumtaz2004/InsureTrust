const asList = (value) => Array.isArray(value) ? value : value ? [value] : [];

const ReasoningPanel = ({ graphState = {} }) => {
  const policyClauses = asList(graphState.policy_clauses);
  const medicalFindings = asList(graphState.medical_findings);
  const mismatches = asList(graphState.code_mismatches);
  const unusualCharges = asList(graphState.unusual_charges);
  const precedentCases = asList(graphState.precedent_cases);
  const complianceFlags = asList(graphState.compliance_flags);
  const workflowPath = asList(graphState.workflow_path);
  const hasData = policyClauses.length || medicalFindings.length || mismatches.length
    || unusualCharges.length || precedentCases.length || complianceFlags.length
    || graphState.allowed_total !== undefined || graphState.workflow_reasoning || workflowPath.length;

  if (!hasData) {
    return <p className="py-8 text-center text-sm text-secondary">No reasoning data is available for this claim.</p>;
  }

  return (
    <div className="space-y-6">
      <h3 className="text-sm font-semibold text-primary">Claim reasoning</h3>

      <section>
        <h4 className="text-xs font-semibold uppercase text-secondary">Policy clauses used</h4>
        <p className="mt-1 text-sm text-primary">Coverage status: {graphState.coverage_status || 'Not available'}</p>
        {policyClauses.length ? (
          <ul className="mt-2 space-y-2">
            {policyClauses.map((clause, index) => (
              <li key={clause.id || `${clause.clause_title}-${index}`} className="border-l-2 border-accent pl-3">
                <p className="text-sm font-medium text-primary">{clause.clause_title || clause.title || 'Policy clause'}</p>
                {clause.content && <p className="mt-1 text-xs leading-5 text-secondary">{clause.content}</p>}
              </li>
            ))}
          </ul>
        ) : <p className="mt-2 text-xs text-secondary">No policy clauses were recorded.</p>}
      </section>

      <section>
        <h4 className="text-xs font-semibold uppercase text-secondary">Medical and billing findings</h4>
        <p className="mt-1 text-sm text-primary">Allowed total: {graphState.allowed_total == null ? 'Not available' : `$${Number(graphState.allowed_total).toLocaleString()}`}</p>
        {mismatches.length > 0 && (
          <div className="mt-2">
            <p className="text-xs font-medium text-primary">Code mismatches</p>
            <ul className="mt-1 list-disc space-y-1 pl-5 text-xs text-secondary">{mismatches.map((item, index) => <li key={`${item}-${index}`}>{typeof item === 'string' ? item : JSON.stringify(item)}</li>)}</ul>
          </div>
        )}
        {unusualCharges.length > 0 && (
          <div className="mt-2">
            <p className="text-xs font-medium text-primary">Unusual charges</p>
            <ul className="mt-1 list-disc space-y-1 pl-5 text-xs text-secondary">{unusualCharges.map((item, index) => <li key={`${item}-${index}`}>{typeof item === 'string' ? item : JSON.stringify(item)}</li>)}</ul>
          </div>
        )}
        {medicalFindings.length > 0 && (
          <ul className="mt-2 space-y-2 text-xs text-secondary">
            {medicalFindings.map((finding, index) => (
              <li key={`${finding.type || 'finding'}-${index}`}>
                <span className="font-medium text-primary">{finding.type || 'Finding'}:</span>{' '}
                {typeof finding.details === 'string' ? finding.details : JSON.stringify(finding.details ?? finding)}
              </li>
            ))}
          </ul>
        )}
      </section>

      <section>
        <h4 className="text-xs font-semibold uppercase text-secondary">Precedent cases</h4>
        <p className="mt-1 text-sm text-primary">Historical approval rate: {graphState.historical_approval_rate == null ? 'Not available' : `${Math.round(Number(graphState.historical_approval_rate) * 100)}%`}</p>
        {precedentCases.length ? (
          <ul className="mt-2 space-y-2">
            {precedentCases.map((precedent, index) => (
              <li key={precedent.id || precedent.precedent_code || index} className="text-xs text-secondary">
                <span className="font-medium text-primary">{precedent.precedent_code || precedent.id || 'Precedent'}:</span>{' '}
                {precedent.content || precedent.summary || 'No summary recorded.'}
              </li>
            ))}
          </ul>
        ) : <p className="mt-2 text-xs text-secondary">No precedent cases were recorded.</p>}
      </section>

      <section>
        <h4 className="text-xs font-semibold uppercase text-secondary">Compliance flags</h4>
        {complianceFlags.length ? (
          <ul className="mt-2 list-disc space-y-1 pl-5 text-xs text-secondary">{complianceFlags.map((flag, index) => <li key={`${flag}-${index}`}>{typeof flag === 'string' ? flag : JSON.stringify(flag)}</li>)}</ul>
        ) : <p className="mt-2 text-xs text-secondary">No compliance flags were recorded.</p>}
      </section>

      <section>
        <h4 className="text-xs font-semibold uppercase text-secondary">Workflow</h4>
        {graphState.workflow_reasoning && <p className="mt-2 text-sm leading-5 text-primary">{graphState.workflow_reasoning}</p>}
        {workflowPath.length ? (
          <ol className="mt-2 flex flex-wrap gap-2 text-xs text-secondary">
            {workflowPath.map((step, index) => <li key={`${step}-${index}`} className="rounded-md bg-background px-2 py-1">{step}</li>)}
          </ol>
        ) : <p className="mt-2 text-xs text-secondary">Workflow path is unavailable.</p>}
      </section>
    </div>
  );
};

export default ReasoningPanel;