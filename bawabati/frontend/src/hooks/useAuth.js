// src/hooks/useAuth.js
import { useState, useEffect, createContext, useContext } from 'react';
import React from 'react';
import { apiEndpoints, api } from '../services/api';
import { withErrorHandling } from '../utils/errorHandler';

// Destructure API endpoints
const { auth, user } = apiEndpoints;

// Create auth context
const AuthContext = createContext(null);

// Auth provider component
export function AuthProvider({ children }) {
  const [userState, setUserState] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const initializeAuth = async () => {
      if (process.env.NODE_ENV === 'development') {
        const savedUser = JSON.parse(localStorage.getItem('user'));
        if (savedUser) {
          setUserState(savedUser);
          setLoading(false);
          return;
        }
      }
      await checkAuthStatus();
    };

    initializeAuth();
  }, []);

  // ✅ Function to fetch and set CSRF Token
  const fetchAndSetCSRFToken = async () => {
    try {
      const response = await api.get('/csrf/', { withCredentials: true });
      const csrfToken = response.data?.csrfToken;

      if (csrfToken) {
        api.defaults.headers.common['X-CSRFToken'] = csrfToken;
        document.cookie = `csrftoken=${csrfToken}; path=/;`;
      }
    } catch (error) {
      console.error("Failed to fetch CSRF Token:", error);
    }
  };

  // ✅ Function to check authentication status
  const checkAuthStatus = async () => {
    setLoading(true);
    await fetchAndSetCSRFToken(); // Make sure CSRF token is set

    const { data, error } = await withErrorHandling(
      () => user.getCurrentUser()
    );

    if (data && !error) {
      setUserState(data);
      if (process.env.NODE_ENV === 'development') {
        localStorage.setItem('user', JSON.stringify(data));
      }
    } else {
      setUserState(null);
      localStorage.removeItem('user');
    }

    setLoading(false);
  };

  // ✅ Login function
// src/hooks/useAuth.js
const login = async (username, password) => {
  try {
      await fetchAndSetCSRFToken(); // Make sure CSRF token is set

      const response = await api.post('/login/', {
          username,
          password
      }, { withCredentials: true });

      if (response.data) {
          setUserState(response.data);
          localStorage.setItem('user', JSON.stringify(response.data));
          return { success: true };
      } else {
          return { success: false, message: 'Login failed' };
      }
  } catch (error) {
      console.error('Login error:', error);
      return {
          success: false,
          message: 'Login failed. Please try again.',
      };
  }
};


  // ✅ Register function
  const register = async (userData) => {
    try {
      await fetchAndSetCSRFToken();
      const { data, error } = await withErrorHandling(
        () => auth.register(userData)
      );

      if (error) return { success: false, message: error.message };
      setUserState(data);
      localStorage.setItem('user', JSON.stringify(data));

      return { success: true };
    } catch (error) {
      console.error('Registration error:', error);
      return {
        success: false,
        message: 'Registration failed. Please try again.',
      };
    }
  };

  // ✅ Logout function
  const logout = async () => {
    try {
      await fetchAndSetCSRFToken();
      await auth.logout();
      setUserState(null);
      localStorage.removeItem('user');
      return { success: true };
    } catch (error) {
      console.error('Logout error:', error);
      return {
        success: false,
        message: 'Logout failed. Please try again.',
      };
    }
  };

  const authContextValue = {
    user: userState,
    loading,
    login,
    register,
    logout,
    refreshUser: checkAuthStatus,
  };

  return <AuthContext.Provider value={authContextValue}>{children}</AuthContext.Provider>;
}

// ✅ Custom hook to use auth context
export function useAuth() {
  const context = useContext(AuthContext);
  if (context === null) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
}
