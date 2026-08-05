/**
 * Ops API module — staff/internal endpoints ONLY.
 * Separate from client API to enforce structural separation.
 * Includes org_id in requests for multi-tenant support.
 */

const OPS_API_BASE = '/api/ops';

const getAuthHeaders = () => {
  const token = localStorage.getItem('insuretrust_token');
  return {
    'Content-Type': 'application/json',
    ...(token ? { Authorization: `Bearer ${token}` } : {}),
  };
};

const opsFetch = async (path, options = {}) => {
  const response = await fetch(`${OPS_API_BASE}${path}`, {
    ...options,
    headers: { ...getAuthHeaders(), ...options.headers },
  });

  if (response.status === 401) {
    localStorage.removeItem('insuretrust_token');
    window.location.href = '/staff-login';
    throw new Error('Unauthorized');
  }

  if (response.status === 403) {
    throw new Error('Forbidden — insufficient permissions');
  }

  if (!response.ok) {
    throw new Error(`API error: ${response.status}`);
  }

  return response.json();
};

export const opsApi = {
  // Claims Queue — full internal fields including fraud signals, reasoning
  getClaimsQueue: (params) => opsFetch(`/claims?${new URLSearchParams(params)}`),
  getClaimDetail: (id) => opsFetch(`/claims/${id}`),
  getClaimReasoning: (id) => opsFetch(`/claims/${id}/reasoning`),
  getClaimDebate: (id) => opsFetch(`/claims/${id}/debate`),

  // Claim actions
  approveClaim: (id) => opsFetch(`/claims/${id}/approve`, { method: 'POST' }),
  overrideClaim: (id, reason) => opsFetch(`/claims/${id}/override`, { method: 'POST', body: JSON.stringify({ reason }) }),
  sendBackClaim: (id, notes) => opsFetch(`/claims/${id}/send-back`, { method: 'POST', body: JSON.stringify({ notes }) }),

  // Analytics
  getAnalytics: () => opsFetch('/analytics'),
  getKpis: () => opsFetch('/kpis'),

  // Audit logs
  getAuditLogs: (params) => opsFetch(`/audit-logs?${new URLSearchParams(params)}`),

  // User management
  getUsers: () => opsFetch('/users'),
  getAdjusters: () => opsFetch('/adjusters'),
};

export default opsApi;
