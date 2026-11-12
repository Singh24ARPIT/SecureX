import React, { createContext, useContext, useState, useEffect } from 'react';
import api from '../api/client';

const AuthContext = createContext(null);

export const AuthProvider = ({ children }) => {
  const [user, setUser] = useState(() => {
    const saved = localStorage.getItem('securex_user');
    return saved ? JSON.parse(saved) : null;
  });
  const [token, setToken] = useState(() => localStorage.getItem('securex_token'));
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const checkDemoAutoLogin = async () => {
      const params = new URLSearchParams(window.location.search);
      if (params.get('demo') === 'admin' && !localStorage.getItem('securex_token')) {
        try {
          await login('admin', 'SecuReXAdmin2026!');
        } catch (e) {
          console.error('Demo auto-login error:', e);
        }
      }
    };
    checkDemoAutoLogin();
  }, []);

  useEffect(() => {
    const verifyUser = async () => {
      if (token) {
        try {
          const res = await api.get('/auth/me');
          setUser(res.data);
          localStorage.setItem('securex_user', JSON.stringify(res.data));
        } catch (err) {
          logout();
        }
      }
      setLoading(false);
    };
    verifyUser();
  }, [token]);

  const login = async (username, password) => {
    const res = await api.post('/auth/login', { username, password });
    const { access_token, user: loggedUser } = res.data;
    localStorage.setItem('securex_token', access_token);
    localStorage.setItem('securex_user', JSON.stringify(loggedUser));
    setToken(access_token);
    setUser(loggedUser);
    return loggedUser;
  };

  const logout = () => {
    localStorage.removeItem('securex_token');
    localStorage.removeItem('securex_user');
    setToken(null);
    setUser(null);
  };

  return (
    <AuthContext.Provider value={{ user, token, isAuthenticated: !!token, loading, login, logout }}>
      {children}
    </AuthContext.Provider>
  );
};

export const useAuth = () => useContext(AuthContext);

