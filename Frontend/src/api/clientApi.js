const API_BASE = import.meta.env.VITE_API_BASE_URL || 'http://127.0.0.1:8000/api/v1';

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
  
  if (response.status === 401 && token) {
    localStorage.removeItem('insuretrust_token');
    if (window.location.pathname.startsWith('/ops')) {
      window.location.assign('/staff-login');
    } else {
      window.location.assign('/login');
    }
  }

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

export function getClaims(token, limit = 50) {
  return request(`/claims?limit=${limit}`, { method: 'GET', token });
}

export function getClaimById(claimId, token) {
  return request(`/claims/${claimId}`, { method: 'GET', token });
}

export function submitClaim(payload, token) {
  return request('/claims/submit', { method: 'POST', body: payload, token });
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

export function getOpsAnalytics(token) {
  return request('/analytics/kpis', { method: 'GET', token });
}

export function getAuditLogs(token) {
  return request('/analytics/audit-logs', { method: 'GET', token });
}
