import React, { createContext, useContext, useState, useEffect } from 'react';
import { authAPI, getToken, setToken, removeToken } from '../services/api';

const AuthContext = createContext({});

export const useAuth = () => {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
};

export const AuthProvider = ({ children }) => {
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(true);
  const [isAuthenticated, setIsAuthenticated] = useState(false);

  useEffect(() => {
    checkAuthStatus();
  }, []);

  const checkAuthStatus = async () => {
    const token = getToken();
    if (!token) {
      setLoading(false);
      return;
    }

    try {
      const response = await authAPI.getMe();
      setUser(response.data);
      setIsAuthenticated(true);
    } catch (error) {
      console.error('Auth check failed:', error);
      removeToken();
    } finally {
      setLoading(false);
    }
  };

  const login = async (email, password) => {
    try {
      const response = await authAPI.login(email, password);
      const { access_token, user: userData } = response.data;
      
      setToken(access_token);
      setUser(userData);
      setIsAuthenticated(true);
      
      return { success: true, user: userData };
    } catch (error) {
      return { 
        success: false, 
        message: error.response?.data?.detail || 'Login failed' 
      };
    }
  };

  const register = async (userData) => {
    try {
      const response = await authAPI.register(userData);
      return { success: true, message: response.data.message };
    } catch (error) {
      return { 
        success: false, 
        message: error.response?.data?.detail || 'Registration failed' 
      };
    }
  };

  const logout = () => {
    removeToken();
    setUser(null);
    setIsAuthenticated(false);
  };

  const verifyEmail = async (token) => {
    try {
      const response = await authAPI.verifyEmail(token);
      return { success: true, message: response.data.message };
    } catch (error) {
      return { 
        success: false, 
        message: error.response?.data?.detail || 'Verification failed' 
      };
    }
  };

  const value = {
    user,
    loading,
    isAuthenticated,
    login,
    register,
    logout,
    verifyEmail,
    checkAuthStatus,
  };

  return (
    <AuthContext.Provider value={value}>
      {children}
    </AuthContext.Provider>
  );
};