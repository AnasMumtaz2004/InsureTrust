import { createContext, useState, useCallback } from 'react';
import { loginCustomer, loginStaff } from '../api/clientApi';

const AuthContext = createContext(null);

const decodeToken = (token) => {
  try {
    const payload = JSON.parse(atob(token.split('.')[1]));
    return payload;
  } catch {
    return null;
  }
};

export const AuthProvider = ({ children }) => {
  const [user, setUser] = useState(() => {
    const stored = localStorage.getItem('insuretrust_token');
    if (stored) {
      const decoded = decodeToken(stored);
      const isValid = decoded && Number(decoded.exp) > Math.floor(Date.now() / 1000);
      if (isValid) {
        return { ...decoded, token: stored };
      }
      localStorage.removeItem('insuretrust_token');
    }
    return null;
  });

  const login = useCallback(async (role, userData = {}) => {
    const response = role === 'customer'
      ? await loginCustomer(userData.email, userData.password)
      : await loginStaff(userData.email, userData.password);

    const token = response.access_token;
    const decoded = decodeToken(token);

    if (!decoded) {
      throw new Error('Unable to decode authentication token.');
    }

    const normalizedUser = {
      ...decoded,
      token,
      name: decoded.name || decoded.full_name || userData.name || 'User',
      email: decoded.email || userData.email || '',
    };

    localStorage.setItem('insuretrust_token', token);
    setUser(normalizedUser);

    return normalizedUser;
  }, []);

  const logout = useCallback(() => {
    localStorage.removeItem('insuretrust_token');
    setUser(null);
  }, []);

  const value = {
    user,
    token: user?.token || null,
    role: user?.role || null,
    isAuthenticated: !!user,
    login,
    logout,
  };

  return (
    <AuthContext.Provider value={value}>
      {children}
    </AuthContext.Provider>
  );
};

export default AuthContext;
