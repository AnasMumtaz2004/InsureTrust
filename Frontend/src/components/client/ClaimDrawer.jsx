import { useState } from 'react';
import { Drawer, Button, Tabs, ChatComposer } from '../shared';

const claimSteps = [
  { key: 'type', label: 'Claim Type', fields: ['type'] },
  { key: 'details', label: 'Claim Details', fields: ['description', 'date', 'amount'] },
  { key: 'documents', label: 'Supporting Documents', fields: ['documents'] },
  { key: 'review', label: 'Review & Submit', fields: [] },
];

const ClaimDrawer = ({ isOpen, onClose }) => {
  const [mode, setMode] = useState('form'); // 'form' or 'chat'
  const [step, setStep] = useState(0);
  const [formData, setFormData] = useState({
    type: '',
    description: '',
    date: '',
    amount: '',
    documents: [],
  });
  const [chatMessages, setChatMessages] = useState([
    {
      role: 'assistant',
      content: "I'll help you file a new claim. Could you start by telling me what type of claim this is? (e.g., health, auto, life)",
    },
  ]);

  const handleFieldChange = (field, value) => {
    setFormData((prev) => ({ ...prev, [field]: value }));
  };

  const handleChatSend = (message) => {
    setChatMessages((prev) => [...prev, { role: 'user', content: message }]);

    // Simulate AI parsing and filling form fields
    setTimeout(() => {
      const lower = message.toLowerCase();
      if (lower.includes('health') || lower.includes('medical')) {
        setFormData((prev) => ({ ...prev, type: 'health' }));
      } else if (lower.includes('car') || lower.includes('auto') || lower.includes('vehicle')) {
        setFormData((prev) => ({ ...prev, type: 'car' }));
      }

      setChatMessages((prev) => [
        ...prev,
        {
          role: 'assistant',
          content: "Got it! I've noted that down. Can you describe what happened and the approximate date of the incident?",
        },
      ]);
    }, 800);
  };

  const modeTabs = [
    { key: 'form', label: 'Step-by-Step Form' },
    { key: 'chat', label: 'Describe to AI' },
  ];

  return (
    <Drawer isOpen={isOpen} onClose={onClose} title="File New Claim" width="max-w-xl">
      {/* Mode toggle */}
      <Tabs tabs={modeTabs} activeKey={mode} onChange={setMode} className="mb-6" />

      {mode === 'form' ? (
        <div>
          {/* Step indicator */}
          <div className="flex items-center gap-2 mb-6">
            {claimSteps.map((s, i) => (
              <div key={s.key} className="flex items-center gap-2">
                <div className={`w-7 h-7 rounded-full flex items-center justify-center text-xs font-medium ${
                  i <= step ? 'bg-accent text-white' : 'bg-border text-secondary'
                }`}>
                  {i + 1}
                </div>
                {i < claimSteps.length - 1 && (
                  <div className={`w-8 h-0.5 ${i < step ? 'bg-accent' : 'bg-border'}`} />
                )}
              </div>
            ))}
          </div>

          {/* Step content */}
          <div className="space-y-4">
            {step === 0 && (
              <>
                <label className="block text-sm font-medium text-primary">Claim Type</label>
                <select
                  value={formData.type}
                  onChange={(e) => handleFieldChange('type', e.target.value)}
                  className="w-full px-4 py-2.5 border border-border rounded-md text-sm bg-white focus:outline-none focus:border-accent"
                >
                  <option value="">Select type...</option>
                  <option value="health">Health Insurance</option>
                  <option value="car">Car Insurance</option>
                  <option value="life">Life Insurance</option>
                </select>
              </>
            )}
            {step === 1 && (
              <>
                <div>
                  <label className="block text-sm font-medium text-primary mb-1">Description</label>
                  <textarea
                    value={formData.description}
                    onChange={(e) => handleFieldChange('description', e.target.value)}
                    rows={3}
                    placeholder="Describe what happened..."
                    className="w-full px-4 py-2.5 border border-border rounded-md text-sm bg-white focus:outline-none focus:border-accent resize-none"
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium text-primary mb-1">Date of Incident</label>
                  <input
                    type="date"
                    value={formData.date}
                    onChange={(e) => handleFieldChange('date', e.target.value)}
                    className="w-full px-4 py-2.5 border border-border rounded-md text-sm bg-white focus:outline-none focus:border-accent"
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium text-primary mb-1">Estimated Amount</label>
                  <input
                    type="number"
                    value={formData.amount}
                    onChange={(e) => handleFieldChange('amount', e.target.value)}
                    placeholder="$0.00"
                    className="w-full px-4 py-2.5 border border-border rounded-md text-sm bg-white focus:outline-none focus:border-accent"
                  />
                </div>
              </>
            )}
            {step === 2 && (
              <>
                <label className="block text-sm font-medium text-primary">Upload Documents</label>
                <div className="border-2 border-dashed border-border rounded-lg p-8 text-center">
                  <p className="text-sm text-secondary">Drag & drop files here or click to browse</p>
                  <p className="text-xs text-secondary mt-1">PDF, JPG, PNG up to 10MB</p>
                </div>
              </>
            )}
            {step === 3 && (
              <div className="space-y-3">
                <h4 className="text-sm font-semibold text-primary">Review Your Claim</h4>
                <div className="bg-background rounded-lg p-4 space-y-2">
                  <p className="text-sm"><span className="text-secondary">Type:</span> <span className="font-medium">{formData.type || '—'}</span></p>
                  <p className="text-sm"><span className="text-secondary">Description:</span> <span className="font-medium">{formData.description || '—'}</span></p>
                  <p className="text-sm"><span className="text-secondary">Date:</span> <span className="font-medium">{formData.date || '—'}</span></p>
                  <p className="text-sm"><span className="text-secondary">Amount:</span> <span className="font-medium">{formData.amount ? `$${formData.amount}` : '—'}</span></p>
                </div>
              </div>
            )}
          </div>

          {/* Step navigation */}
          <div className="flex justify-between mt-6">
            <Button
              variant="outline"
              size="sm"
              onClick={() => setStep((s) => Math.max(0, s - 1))}
              disabled={step === 0}
            >
              Back
            </Button>
            {step < claimSteps.length - 1 ? (
              <Button
                variant="primary"
                size="sm"
                onClick={() => setStep((s) => Math.min(claimSteps.length - 1, s + 1))}
              >
                Next
              </Button>
            ) : (
              <Button variant="secondary" size="sm" onClick={onClose}>
                Submit Claim
              </Button>
            )}
          </div>
        </div>
      ) : (
        /* Chat mode */
        <div className="flex flex-col h-[calc(100vh-200px)]">
          <div className="flex-1 overflow-y-auto space-y-4 pb-4">
            {chatMessages.map((msg, i) => (
              <div
                key={i}
                className={`flex ${msg.role === 'user' ? 'justify-end' : 'justify-start'} transition-chat`}
              >
                <div
                  className={`max-w-[80%] px-4 py-2.5 rounded-lg text-sm ${
                    msg.role === 'user'
                      ? 'bg-primary text-white'
                      : 'bg-background text-primary border border-border'
                  }`}
                >
                  {msg.content}
                </div>
              </div>
            ))}
          </div>

          {/* Show live-filled form data */}
          {formData.type && (
            <div className="bg-accent/5 border border-accent/20 rounded-lg p-3 mb-3">
              <p className="text-xs font-medium text-accent mb-1">Auto-filled from chat:</p>
              {formData.type && <p className="text-xs text-primary">Type: {formData.type}</p>}
              {formData.description && <p className="text-xs text-primary">Description: {formData.description}</p>}
            </div>
          )}

          <ChatComposer onSend={handleChatSend} placeholder="Describe your claim..." />
        </div>
      )}
    </Drawer>
  );
};

export default ClaimDrawer;
