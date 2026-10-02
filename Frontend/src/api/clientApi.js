const API_BASE = import.meta.env.VITE_API_BASE_URL || 'http://127.0.0.1:8000/api/v1';

function handleUnauthorized(response, token) {
  if (response.status === 401 && token) {
    localStorage.removeItem('insuretrust_token');
    if (window.location.pathname.startsWith('/ops')) {
      window.location.assign('/staff-login');
    } else {
      window.location.assign('/login');
    }
  }
}

async function request(path, { method = 'GET', body, token, headers = {} } = {}) {
  const options = {
    method,
    headers: {
      'Content-Type': 'application/json',
      ...(token ? { Authorization: `Bearer ${token}` } : {}),
      ...headers,
    },
  };

  if (body !== undefined) {
    options.body = JSON.stringify(body);
  }

  const response = await fetch(`${API_BASE}${path}`, options);
  handleUnauthorized(response, token);

  const data = await response.json().catch(() => ({}));

  if (!response.ok) {
    throw new Error(data.detail || 'Request failed');
  }

  return data;
}

async function requestForm(path, formData, token) {
  const response = await fetch(`${API_BASE}${path}`, {
    method: 'POST',
    headers: token ? { Authorization: `Bearer ${token}` } : {},
    body: formData,
  });
  handleUnauthorized(response, token);
  const data = await response.json().catch(() => ({}));

  if (!response.ok) {
    throw new Error(data.detail || 'Request failed');
  }

  return data;
}

export function loginCustomer(email, password) {
  return request('/auth/login/customer', { method: 'POST', body: { email, password } });
}

export function loginStaff(email, password) {
  return request('/auth/login/staff', { method: 'POST', body: { email, password } });
}

export function register(fullName, email, password) {
  return request('/auth/register', {
    method: 'POST',
    body: { email, password, full_name: fullName },
  });
}

export function getClaims(token, limit = 50) {
  return request(`/claims?limit=${limit}`, { method: 'GET', token });
}

export function getClaimById(claimId, token) {
  return request(`/claims/${claimId}`, { method: 'GET', token });
}

export function submitClaim(payload, token) {
  return request('/claims/submit', { method: 'POST', body: payload, token });
}

export function uploadDocument(claimId, documentType, file, token) {
  const formData = new FormData();
  formData.append('claim_id', claimId);
  formData.append('document_type', documentType);
  formData.append('file', file);
  return requestForm('/documents/upload', formData, token);
}

export function checkDocumentCompleteness(claimId, token) {
  return request(`/documents/check-completeness?claim_id=${encodeURIComponent(claimId)}`, {
    method: 'POST',
    token,
  });
}

export function postClaimIntakeChat(conversation, token) {
  return request('/claims/intake-chat', { method: 'POST', body: { conversation }, token });
}

export function postClaimChat(claimId, message, token) {
  return request(`/claims/${claimId}/chat`, { method: 'POST', body: { message }, token });
}

export function getClaimExplanation(claimId, token) {
  return request(`/explanation/${claimId}`, { method: 'GET', token });
}

export function postClaimExplanationQuestion(claimId, question, token) {
  return request('/explanation/chat', { method: 'POST', body: { claim_id: claimId, user_question: question }, token });
}

export function getOpsClaims(token) {
  return request('/ops/cases/queue', { method: 'GET', token });
}

export function getOpsClaimDetail(claimId, token) {
  return request(`/ops/cases/${claimId}/graph-state`, { method: 'GET', token });
}

export function getCaseGraphState(claimId, token) {
  return request(`/ops/cases/${claimId}/graph-state`, { method: 'GET', token });
}

export function getDebateTranscript(claimId, token) {
  return request(`/ops/cases/${claimId}/debate-transcript`, { method: 'GET', token });
}

export function getAuditTrail(claimId, token) {
  return request(`/ops/cases/${claimId}/audit-trail`, { method: 'GET', token });
}

export function submitDecisionAction(claimId, payload, token) {
  return request(`/ops/decisions/${claimId}/action`, { method: 'POST', body: payload, token });
}

export function getOpsUsers(token) {
  return request('/ops/users', { method: 'GET', token });
}

export function getOpsAnalytics(token) {
  return request('/analytics/kpis', { method: 'GET', token });
}

export function getAuditLogs(token) {
  return request('/analytics/audit-logs', { method: 'GET', token });
}
