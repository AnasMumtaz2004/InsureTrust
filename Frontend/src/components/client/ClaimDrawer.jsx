import { useState } from 'react';
import { FileText, UploadCloud, X } from 'lucide-react';
import { Drawer, Button, Tabs, ChatComposer } from '../shared';
import { useAuth } from '../../auth/useAuth';
import { postClaimIntakeChat, submitClaim, uploadDocument } from '../../api/clientApi';

const claimSteps = [
  { key: 'details', label: 'Claim Details' },
  { key: 'codes', label: 'Medical Codes' },
  { key: 'documents', label: 'Documents' },
  { key: 'review', label: 'Review & Submit' },
];

const initialFormData = {
  policy_number: '',
  incident_date: '',
  claimed_amount: '',
  description: '',
  diagnosis_codes: '',
  procedure_codes: '',
};

const fieldClassName = 'w-full px-4 py-2.5 border border-border rounded-md text-sm bg-white focus:outline-none focus:border-accent';
const diagnosisPattern = /^[A-Z]\d{2}(\.\w{1,4})?$/;
const procedurePattern = /^(\d{5}|[A-Z]\d{4})$/;
const allowedTypes = new Set(['application/pdf', 'image/jpeg', 'image/png']);
const allowedExtensions = /\.(pdf|jpe?g|png)$/i;
const maxFileBytes = 10 * 1024 * 1024;

const splitCodes = (codes) => codes.split(',').map((code) => code.trim().toUpperCase()).filter(Boolean);

const ClaimDrawer = ({ isOpen, onClose, onSubmitted = () => {} }) => {
  const [mode, setMode] = useState('form');
  const [step, setStep] = useState(0);
  const [formData, setFormData] = useState(initialFormData);
  const [fieldErrors, setFieldErrors] = useState({});
  const [documentType, setDocumentType] = useState('MEDICAL_BILL');
  const [files, setFiles] = useState([]);
  const [submitting, setSubmitting] = useState(false);
  const [submitError, setSubmitError] = useState('');
  const [uploadProgress, setUploadProgress] = useState(null);
  const [chatMessages, setChatMessages] = useState([
    { role: 'assistant', content: 'Tell me what happened and I can gather the details needed for your claim.' },
  ]);
  const [chatLoading, setChatLoading] = useState(false);
  const { token } = useAuth();

  const updateField = (field, value) => {
    setFormData((current) => ({ ...current, [field]: value }));
    setFieldErrors((current) => ({ ...current, [field]: '' }));
    setSubmitError('');
  };

  const validateStep = (stepIndex) => {
    const errors = {};
    if (stepIndex === 0) {
      if (!formData.policy_number.trim()) errors.policy_number = 'Policy number is required.';
      if (!formData.incident_date) {
        errors.incident_date = 'Incident date is required.';
      } else {
        const today = new Date();
        today.setMinutes(today.getMinutes() - today.getTimezoneOffset());
        const todayString = today.toISOString().slice(0, 10);
        if (formData.incident_date > todayString) errors.incident_date = 'Incident date cannot be in the future.';
      }
      if (!formData.claimed_amount || Number(formData.claimed_amount) <= 0) {
        errors.claimed_amount = 'Enter an amount greater than 0.';
      }
      if (!formData.description.trim()) errors.description = 'Description is required.';
    }
    if (stepIndex === 1) {
      const diagnoses = splitCodes(formData.diagnosis_codes);
      const procedures = splitCodes(formData.procedure_codes);
      if (diagnoses.some((code) => !diagnosisPattern.test(code))) {
        errors.diagnosis_codes = 'Use valid ICD-10 codes separated by commas.';
      }
      if (procedures.some((code) => !procedurePattern.test(code))) {
        errors.procedure_codes = 'Use valid CPT codes separated by commas.';
      }
    }
    setFieldErrors((current) => ({ ...current, ...errors }));
    return Object.keys(errors).length === 0;
  };

  const addFiles = (fileList) => {
    const newFiles = Array.from(fileList).map((file) => {
      let error = '';
      if (!allowedTypes.has(file.type) && !allowedExtensions.test(file.name)) {
        error = 'Choose a PDF, JPG, or PNG file.';
      } else if (file.size > maxFileBytes) {
        error = 'File must be 10MB or smaller.';
      }
      return {
        id: globalThis.crypto?.randomUUID?.() || `${Date.now()}-${Math.random()}`,
        file,
        status: error ? 'failed' : 'queued',
        error,
      };
    });
    setFiles((current) => [...current, ...newFiles]);
  };

  const updateFile = (id, changes) => {
    setFiles((current) => current.map((entry) => (entry.id === id ? { ...entry, ...changes } : entry)));
  };

  const handleSubmit = async () => {
    setSubmitError('');
    if (!validateStep(0)) {
      setStep(0);
      return;
    }
    if (!validateStep(1)) {
      setStep(1);
      return;
    }

    setSubmitting(true);
    const payload = {
      policy_number: formData.policy_number.trim(),
      incident_date: formData.incident_date,
      claimed_amount: Number(formData.claimed_amount),
      description: formData.description.trim(),
      diagnosis_codes: splitCodes(formData.diagnosis_codes),
      procedure_codes: splitCodes(formData.procedure_codes),
    };

    try {
      const claim = await submitClaim(payload, token);
      const readyFiles = files.filter((entry) => entry.status === 'queued');
      const uploadResults = [];
      setUploadProgress(readyFiles.length ? { completed: 0, total: readyFiles.length } : null);

      for (const [index, entry] of readyFiles.entries()) {
        updateFile(entry.id, { status: 'uploading', error: '' });
        setUploadProgress({ completed: index, total: readyFiles.length, current: entry.file.name });
        try {
          await uploadDocument(claim.id, documentType, entry.file, token);
          updateFile(entry.id, { status: 'uploaded' });
          uploadResults.push({ file: entry.file.name, uploaded: true });
        } catch (uploadError) {
          const message = uploadError.message || 'Upload failed.';
          updateFile(entry.id, { status: 'failed', error: message });
          uploadResults.push({ file: entry.file.name, uploaded: false, error: message });
        }
        setUploadProgress({ completed: index + 1, total: readyFiles.length });
      }

      onSubmitted(claim, uploadResults);
      setFormData(initialFormData);
      setFieldErrors({});
      setFiles([]);
      setStep(0);
      setMode('form');
      setUploadProgress(null);
      onClose();
    } catch (error) {
      const detail = typeof error.message === 'string' ? error.message : JSON.stringify(error.message);
      setSubmitError(detail || 'Unable to submit your claim.');
    } finally {
      setSubmitting(false);
    }
  };

  const handleChatSend = async (message) => {
    const conversation = [...chatMessages, { role: 'user', content: message }];
    setChatMessages(conversation);
    setChatLoading(true);
    try {
      const response = await postClaimIntakeChat(conversation, token);
      const extracted = response.extracted_fields || {};
      setFormData((current) => ({
        ...current,
        ...Object.fromEntries(Object.entries(extracted).map(([key, value]) => [
          key,
          Array.isArray(value) ? value.join(', ') : String(value ?? ''),
        ])),
      }));
      const fieldLabels = {
        policy_number: 'policy number',
        incident_date: 'incident date',
        claimed_amount: 'claimed amount',
        description: 'what happened',
      };
      const missing = (response.missing_fields || []).map((field) => fieldLabels[field] || field.replace(/_/g, ' '));
      const followUp = missing.length ? ` I still need: ${missing.join(', ')}.` : '';
      setChatMessages((current) => [...current, {
        role: 'assistant',
        content: `${response.reply || 'I have updated your claim details.'}${followUp}`,
      }]);
    } catch (error) {
      setChatMessages((current) => [...current, {
        role: 'assistant',
        content: error.message || 'I could not process that message right now. You can continue with the form.',
      }]);
    } finally {
      setChatLoading(false);
    }
  };

  const modeTabs = [
    { key: 'form', label: 'Step-by-Step Form' },
    { key: 'chat', label: 'Describe to AI' },
  ];

  const renderFieldError = (field) => fieldErrors[field] && (
    <p className="mt-1 text-xs text-red-600" role="alert">{fieldErrors[field]}</p>
  );

  return (
    <Drawer isOpen={isOpen} onClose={onClose} title="File New Claim" width="max-w-xl">
      <Tabs tabs={modeTabs} activeKey={mode} onChange={setMode} className="mb-6" />

      {submitError && (
        <div role="alert" className="mb-4 rounded-md border border-red-200 bg-red-50 px-4 py-2.5 text-sm text-red-600">
          {submitError}
        </div>
      )}

      {mode === 'form' ? (
        <div>
          <div className="mb-6 flex items-center gap-2" aria-label={`Step ${step + 1} of ${claimSteps.length}: ${claimSteps[step].label}`}>
            {claimSteps.map((claimStep, index) => (
              <div key={claimStep.key} className="flex min-w-0 flex-1 items-center gap-2">
                <div className={`flex h-7 w-7 shrink-0 items-center justify-center rounded-full text-xs font-medium ${index <= step ? 'bg-accent text-white' : 'bg-border text-secondary'}`}>
                  {index + 1}
                </div>
                {index < claimSteps.length - 1 && <div className={`h-0.5 min-w-2 flex-1 ${index < step ? 'bg-accent' : 'bg-border'}`} />}
              </div>
            ))}
          </div>
          <p className="mb-5 text-sm font-medium text-primary">{claimSteps[step].label}</p>

          <div className="space-y-4">
            {step === 0 && (
              <>
                <div>
                  <label htmlFor="policy-number" className="mb-1 block text-sm font-medium text-primary">Policy number</label>
                  <input id="policy-number" value={formData.policy_number} onChange={(event) => updateField('policy_number', event.target.value)} placeholder="e.g. POL-HE-2023-001" className={fieldClassName} aria-invalid={!!fieldErrors.policy_number} />
                  {renderFieldError('policy_number')}
                </div>
                <div>
                  <label htmlFor="incident-date" className="mb-1 block text-sm font-medium text-primary">Incident date</label>
                  <input id="incident-date" type="date" value={formData.incident_date} onChange={(event) => updateField('incident_date', event.target.value)} className={fieldClassName} aria-invalid={!!fieldErrors.incident_date} />
                  {renderFieldError('incident_date')}
                </div>
                <div>
                  <label htmlFor="claimed-amount" className="mb-1 block text-sm font-medium text-primary">Claimed amount</label>
                  <input id="claimed-amount" type="number" min="0.01" step="0.01" value={formData.claimed_amount} onChange={(event) => updateField('claimed_amount', event.target.value)} placeholder="0.00" className={fieldClassName} aria-invalid={!!fieldErrors.claimed_amount} />
                  {renderFieldError('claimed_amount')}
                </div>
                <div>
                  <label htmlFor="claim-description" className="mb-1 block text-sm font-medium text-primary">Description</label>
                  <textarea id="claim-description" rows={4} value={formData.description} onChange={(event) => updateField('description', event.target.value)} placeholder="Describe what happened..." className={`${fieldClassName} resize-y`} aria-invalid={!!fieldErrors.description} />
                  {renderFieldError('description')}
                </div>
              </>
            )}

            {step === 1 && (
              <>
                <div>
                  <label htmlFor="diagnosis-codes" className="mb-1 block text-sm font-medium text-primary">Diagnosis codes</label>
                  <input id="diagnosis-codes" value={formData.diagnosis_codes} onChange={(event) => updateField('diagnosis_codes', event.target.value)} placeholder="e.g. M54.5, J45.9" className={fieldClassName} aria-invalid={!!fieldErrors.diagnosis_codes} />
                  {renderFieldError('diagnosis_codes')}
                </div>
                <div>
                  <label htmlFor="procedure-codes" className="mb-1 block text-sm font-medium text-primary">Procedure codes</label>
                  <input id="procedure-codes" value={formData.procedure_codes} onChange={(event) => updateField('procedure_codes', event.target.value)} placeholder="e.g. 99214, A1234" className={fieldClassName} aria-invalid={!!fieldErrors.procedure_codes} />
                  {renderFieldError('procedure_codes')}
                </div>
              </>
            )}

            {step === 2 && (
              <>
                <div>
                  <label htmlFor="document-type" className="mb-1 block text-sm font-medium text-primary">Document type</label>
                  <select id="document-type" value={documentType} onChange={(event) => setDocumentType(event.target.value)} className={fieldClassName}>
                    <option value="MEDICAL_BILL">Medical bill</option>
                    <option value="CLINICAL_NOTE">Clinical note</option>
                    <option value="RECEIPT">Receipt</option>
                  </select>
                </div>
                <label
                  htmlFor="claim-files"
                  onDragOver={(event) => event.preventDefault()}
                  onDrop={(event) => {
                    event.preventDefault();
                    addFiles(event.dataTransfer.files);
                  }}
                  className="flex cursor-pointer flex-col items-center justify-center rounded-md border-2 border-dashed border-border px-5 py-8 text-center hover:border-accent"
                >
                  <UploadCloud size={28} className="text-accent" aria-hidden="true" />
                  <span className="mt-2 text-sm font-medium text-primary">Drop files here or browse</span>
                  <span className="mt-1 text-xs text-secondary">PDF, JPG, or PNG, up to 10MB each</span>
                  <input
                    id="claim-files"
                    type="file"
                    accept="application/pdf,image/jpeg,image/png,.pdf,.jpg,.jpeg,.png"
                    multiple
                    className="sr-only"
                    onChange={(event) => {
                      addFiles(event.target.files);
                      event.target.value = '';
                    }}
                  />
                </label>
                {files.length > 0 && (
                  <ul className="space-y-2" aria-label="Selected documents">
                    {files.map((entry) => (
                      <li key={entry.id} className="flex items-start gap-3 rounded-md border border-border p-3">
                        <FileText size={16} className="mt-0.5 shrink-0 text-secondary" aria-hidden="true" />
                        <div className="min-w-0 flex-1">
                          <p className="break-all text-sm font-medium text-primary">{entry.file.name}</p>
                          <p className={`text-xs ${entry.error ? 'text-red-600' : 'text-secondary'}`}>
                            {entry.error || (entry.status === 'uploading' ? 'Uploading…' : entry.status === 'uploaded' ? 'Uploaded' : entry.status === 'failed' ? 'Upload failed' : 'Ready to upload')}
                          </p>
                        </div>
                        {!submitting && ['queued', 'failed'].includes(entry.status) && (
                          <button type="button" onClick={() => setFiles((current) => current.filter((item) => item.id !== entry.id))} aria-label={`Remove ${entry.file.name}`} className="text-secondary hover:text-primary">
                            <X size={16} />
                          </button>
                        )}
                      </li>
                    ))}
                  </ul>
                )}
              </>
            )}

            {step === 3 && (
              <div className="space-y-3 rounded-md bg-background p-4">
                <p className="text-sm"><span className="text-secondary">Policy number:</span> <span className="font-medium text-primary">{formData.policy_number}</span></p>
                <p className="text-sm"><span className="text-secondary">Incident date:</span> <span className="font-medium text-primary">{formData.incident_date}</span></p>
                <p className="text-sm"><span className="text-secondary">Claimed amount:</span> <span className="font-medium text-primary">${Number(formData.claimed_amount || 0).toLocaleString()}</span></p>
                <p className="break-words text-sm"><span className="text-secondary">Description:</span> <span className="font-medium text-primary">{formData.description}</span></p>
                <p className="break-words text-sm"><span className="text-secondary">Diagnosis codes:</span> <span className="font-medium text-primary">{formData.diagnosis_codes || 'None provided'}</span></p>
                <p className="break-words text-sm"><span className="text-secondary">Procedure codes:</span> <span className="font-medium text-primary">{formData.procedure_codes || 'None provided'}</span></p>
                <p className="text-sm"><span className="text-secondary">Documents:</span> <span className="font-medium text-primary">{files.length || 'None attached'}</span></p>
              </div>
            )}
          </div>

          {uploadProgress && (
            <div aria-live="polite" className="mt-4 space-y-1">
              <p className="text-xs text-secondary">
                {uploadProgress.current ? `Uploading ${uploadProgress.completed + 1} of ${uploadProgress.total}: ${uploadProgress.current}` : `${uploadProgress.completed} of ${uploadProgress.total} documents processed`}
              </p>
              <progress className="h-2 w-full accent-accent" value={uploadProgress.completed} max={uploadProgress.total} />
            </div>
          )}

          <div className="mt-6 flex justify-between gap-3">
            <Button variant="outline" size="sm" onClick={() => setStep((current) => Math.max(0, current - 1))} disabled={step === 0 || submitting}>
              Back
            </Button>
            {step < claimSteps.length - 1 ? (
              <Button
                variant="primary"
                size="sm"
                onClick={() => {
                  if (validateStep(step)) setStep((current) => current + 1);
                }}
                disabled={submitting}
              >
                Next
              </Button>
            ) : (
              <Button variant="secondary" size="sm" onClick={handleSubmit} disabled={submitting}>
                {submitting ? 'Submitting…' : 'Submit Claim'}
              </Button>
            )}
          </div>
        </div>
      ) : (
        <div className="flex h-[calc(100vh-200px)] flex-col">
          <div className="flex-1 space-y-4 overflow-y-auto pb-4" aria-live="polite">
            {chatMessages.map((message, index) => (
              <div key={`${message.role}-${index}`} className={`flex ${message.role === 'user' ? 'justify-end' : 'justify-start'} transition-chat`}>
                <div className={`max-w-[85%] break-words rounded-lg border px-4 py-2.5 text-sm ${message.role === 'user' ? 'border-primary bg-primary text-white' : 'border-border bg-background text-primary'}`}>
                  {message.content}
                </div>
              </div>
            ))}
            {chatLoading && <p className="text-xs text-secondary">Reviewing the details…</p>}
          </div>
          {Object.entries(formData).some(([, value]) => value) && (
            <div className="mb-3 rounded-md border border-accent/20 bg-accent/5 p-3">
              <p className="mb-1 text-xs font-medium text-accent">Added to claim form</p>
              {formData.policy_number && <p className="text-xs text-primary">Policy: {formData.policy_number}</p>}
              {formData.incident_date && <p className="text-xs text-primary">Incident date: {formData.incident_date}</p>}
              {formData.claimed_amount && <p className="text-xs text-primary">Amount: ${formData.claimed_amount}</p>}
              {formData.description && <p className="text-xs text-primary">Description: {formData.description}</p>}
              {formData.diagnosis_codes && <p className="text-xs text-primary">Diagnosis codes: {formData.diagnosis_codes}</p>}
              {formData.procedure_codes && <p className="text-xs text-primary">Procedure codes: {formData.procedure_codes}</p>}
            </div>
          )}
          <ChatComposer onSend={handleChatSend} placeholder="Describe your claim..." disabled={chatLoading || submitting} />
        </div>
      )}
    </Drawer>
  );
};

export default ClaimDrawer;