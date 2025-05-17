// src/hooks/useAuth.js
import { useState, useEffect, createContext, useContext } from 'react';
import axios from 'axios';
import React from 'react';

// ✅ Set your backend API URL here
const API_BASE_URL = "http://127.0.0.1:8000/"; // Replace with your actual backend URL

// Create auth context
const AuthContext = createContext(null);
  
// Auth provider component
export function AuthProvider({ children }) {
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const initializeAuth = async () => {
      const savedUser = JSON.parse(localStorage.getItem('user'));
      if (savedUser) {
        setUser(savedUser);
        setLoading(false);
      } else {
        await checkAuthStatus();
      }
    };

    initializeAuth();
  }, []);

  // Function to check authentication status
  const checkAuthStatus = async () => {
    try {
      const response = await axios.get(`${API_BASE_URL}/current-user/`);
      setUser(response.data);
      localStorage.setItem('user', JSON.stringify(response.data));
    } catch (error) {
      setUser(null);
      localStorage.removeItem('user');
    } finally {
      setLoading(false);
    }
  };

  // Login function
  const login = async (username, password) => {
    try {
      await fetchCSRFToken();
      const response = await axios.post(`${API_BASE_URL}/login/`, { username, password });
      setUser(response.data);
      localStorage.setItem('user', JSON.stringify(response.data));
      return { success: true };
    } catch (error) {
      return {
        success: false,
        message: error.response?.data?.message || 'Login failed. Please try again.',
      };
    }
  };

  // Register function
  const register = async (userData) => {
    try {
      await fetchCSRFToken();
      const response = await axios.post(`${API_BASE_URL}/register/`, userData);
      setUser(response.data);
      localStorage.setItem('user', JSON.stringify(response.data));
      return { success: true };
    } catch (error) {
      return {
        success: false,
        message: error.response?.data?.message || 'Registration failed. Please try again.',
      };
    }
  };

  // Logout function
  const logout = async () => {
    try {
      await axios.post(`${API_BASE_URL}/logout/`);
      setUser(null);
      localStorage.removeItem('user');
      return { success: true };
    } catch (error) {
      return {
        success: false,
        message: error.response?.data?.message || 'Logout failed. Please try again.',
      };
    }
  };

  // Function to fetch CSRF Token (Reusable)
  const fetchCSRFToken = async () => {
    try {
      const csrfResponse = await axios.get(`${API_BASE_URL}/csrf/`);
      const csrfToken = csrfResponse.data.csrfToken;
      axios.defaults.headers.common['X-CSRFToken'] = csrfToken;
    } catch (error) {
      console.error("Failed to fetch CSRF Token:", error);
    }
  };

  const value = {
    user,
    loading,
    login,
    register,
    logout,
  };

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
}

// Custom hook to use auth context
export function useAuth() {
  const context = useContext(AuthContext);
  if (context === null) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
}
