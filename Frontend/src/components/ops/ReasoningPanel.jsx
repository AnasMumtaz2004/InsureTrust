import { Card } from '../shared';

const mockReasoning = [
  {
    step: 1,
    title: 'Document Verification',
    result: 'Passed',
    detail: 'All required documents present: medical bills (3), hospital admission record, discharge summary.',
    confidence: 0.95,
  },
  {
    step: 2,
    title: 'Policy Coverage Check',
    result: 'Covered',
    detail: 'Claim type (hospitalization) falls within Health Premium Plan coverage. Deductible of $500 applies.',
    confidence: 0.98,
  },
  {
    step: 3,
    title: 'Fraud Signal Analysis',
    result: 'Low Risk',
    detail: 'No anomalies detected. Claim amount is consistent with historical data for similar treatments.',
    confidence: 0.92,
  },
  {
    step: 4,
    title: 'Amount Validation',
    result: 'Within Limits',
    detail: 'Claimed amount ($4,500) is within the network hospital rate for the procedure. No excess billing detected.',
    confidence: 0.89,
  },
];

const ReasoningPanel = () => {
  return (
    <div className="space-y-4">
      <div className="flex items-center justify-between mb-2">
        <h3 className="text-sm font-semibold text-primary">AI Reasoning Trail</h3>
        <span className="text-xs text-secondary">4 steps completed</span>
      </div>

      {mockReasoning.map((item) => (
        <Card key={item.step} className="p-4">
          <div className="flex items-start justify-between gap-3">
            <div className="flex items-start gap-3">
              <div className="w-7 h-7 rounded-full bg-accent/10 text-accent flex items-center justify-center text-xs font-bold shrink-0">
                {item.step}
              </div>
              <div>
                <div className="flex items-center gap-2">
                  <h4 className="text-sm font-medium text-primary">{item.title}</h4>
                  <span className={`text-xs font-medium px-2 py-0.5 rounded-full ${
                    item.result === 'Passed' || item.result === 'Covered' || item.result === 'Low Risk' || item.result === 'Within Limits'
                      ? 'bg-accent/10 text-accent'
                      : 'bg-warning/10 text-warning'
                  }`}>
                    {item.result}
                  </span>
                </div>
                <p className="text-xs text-secondary mt-1">{item.detail}</p>
              </div>
            </div>
            <div className="text-right shrink-0">
              <span className="text-xs text-secondary">Confidence</span>
              <div className="w-16 h-1.5 bg-border rounded-full mt-1">
                <div
                  className="h-full bg-accent rounded-full"
                  style={{ width: `${item.confidence * 100}%` }}
                />
              </div>
              <span className="text-xs font-medium text-primary">{Math.round(item.confidence * 100)}%</span>
            </div>
          </div>
        </Card>
      ))}
    </div>
  );
};

export default ReasoningPanel;
