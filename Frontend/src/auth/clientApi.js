/**
 * Client API module — customer-facing endpoints ONLY.
 * This module structurally cannot call internal/ops endpoints.
 */

const CLIENT_API_BASE = '/api/client';

const getAuthHeaders = () => {
  const token = localStorage.getItem('insuretrust_token');
  return {
    'Content-Type': 'application/json',
    ...(token ? { Authorization: `Bearer ${token}` } : {}),
  };
};

const clientFetch = async (path, options = {}) => {
  const response = await fetch(`${CLIENT_API_BASE}${path}`, {
    ...options,
    headers: { ...getAuthHeaders(), ...options.headers },
  });

  if (response.status === 401) {
    localStorage.removeItem('insuretrust_token');
    window.location.href = '/login';
    throw new Error('Unauthorized');
  }

  if (!response.ok) {
    throw new Error(`API error: ${response.status}`);
  }

  return response.json();
};

export const clientApi = {
  // Policies
  getPolicies: () => clientFetch('/policies'),
  getPolicy: (id) => clientFetch(`/policies/${id}`),

  // Claims — customer-safe fields only
  getClaims: () => clientFetch('/claims'),
  getClaim: (id) => clientFetch(`/claims/${id}`),
  createClaim: (data) => clientFetch('/claims', { method: 'POST', body: JSON.stringify(data) }),

  // Dashboard
  getDashboardStats: () => clientFetch('/dashboard/stats'),
  getRecentActivity: () => clientFetch('/dashboard/activity'),
  getRecommendations: () => clientFetch('/recommendations'),

  // AI Assistant
  sendMessage: (message) => clientFetch('/assistant/chat', { method: 'POST', body: JSON.stringify({ message }) }),

  // Profile
  getProfile: () => clientFetch('/profile'),
  updateProfile: (data) => clientFetch('/profile', { method: 'PUT', body: JSON.stringify(data) }),
};

export default clientApi;
