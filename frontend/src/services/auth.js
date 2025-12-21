/**
 * Authentication service for managing user login, registration, and JWT tokens
 */
import api from './api';

const TOKEN_KEY = 'quant_learn_token';
const USER_KEY = 'quant_learn_user';

/**
 * Register a new user
 * @param {Object} registrationData - User registration data
 * @param {string} registrationData.user_id - Username or email
 * @param {string} registrationData.password - Password (min 8 characters)
 * @param {string} [registrationData.name] - User's display name
 * @param {string} [registrationData.email] - User's email
 * @param {string} [registrationData.role='candidate'] - User role: candidate, recruiter, admin
 * @param {Object} [candidateData] - Candidate-specific fields (if role is candidate)
 * @param {Object} [recruiterData] - Recruiter-specific fields (if role is recruiter)
 * @returns {Promise<Object>} Token response with access_token, user_id, role, name
 */
export const register = async (registrationData) => {
  try {
    const response = await api.post('/auth/register', registrationData);
    const { access_token, user_id, role, name } = response.data;

    // Store token and user info
    localStorage.setItem(TOKEN_KEY, access_token);
    localStorage.setItem(USER_KEY, JSON.stringify({ user_id, role, name }));

    // Set default Authorization header for future requests
    api.defaults.headers.common['Authorization'] = `Bearer ${access_token}`;

    return response.data;
  } catch (error) {
    console.error('Registration error:', error.response?.data || error.message);
    throw error;
  }
};

/**
 * Login user
 * @param {string} user_id - Username or email
 * @param {string} password - User password
 * @returns {Promise<Object>} Token response with access_token, user_id, role, name
 */
export const login = async (user_id, password) => {
  try {
    const response = await api.post('/auth/login', { user_id, password });
    const { access_token, user_id: userId, role, name } = response.data;

    // Store token and user info
    localStorage.setItem(TOKEN_KEY, access_token);
    localStorage.setItem(USER_KEY, JSON.stringify({ user_id: userId, role, name }));

    // Set default Authorization header for future requests
    api.defaults.headers.common['Authorization'] = `Bearer ${access_token}`;

    return response.data;
  } catch (error) {
    console.error('Login error:', error.response?.data || error.message);
    throw error;
  }
};

/**
 * Logout user (clear token and user data)
 */
export const logout = async () => {
  try {
    // Call logout endpoint (optional, for logging purposes)
    await api.post('/auth/logout');
  } catch (error) {
    console.warn('Logout endpoint error:', error.message);
  } finally {
    // Clear local storage
    localStorage.removeItem(TOKEN_KEY);
    localStorage.removeItem(USER_KEY);

    // Remove Authorization header
    delete api.defaults.headers.common['Authorization'];
  }
};

/**
 * Get stored JWT token
 * @returns {string|null} JWT token or null if not found
 */
export const getToken = () => {
  return localStorage.getItem(TOKEN_KEY);
};

/**
 * Get stored user info
 * @returns {Object|null} User object with user_id, role, name or null if not found
 */
export const getUser = () => {
  const userStr = localStorage.getItem(USER_KEY);
  return userStr ? JSON.parse(userStr) : null;
};

/**
 * Get user role
 * @returns {string|null} User role ('candidate', 'recruiter', 'admin') or null
 */
export const getRole = () => {
  const user = getUser();
  return user ? user.role : null;
};

/**
 * Check if user is authenticated
 * @returns {boolean} True if user has a token
 */
export const isAuthenticated = () => {
  return !!getToken();
};

/**
 * Check if user has specific role
 * @param {string|string[]} roles - Role(s) to check against
 * @returns {boolean} True if user has one of the specified roles
 */
export const hasRole = (roles) => {
  const userRole = getRole();
  if (!userRole) return false;

  if (Array.isArray(roles)) {
    return roles.includes(userRole);
  }
  return userRole === roles;
};

/**
 * Check if current user is admin
 * Admin is identified by email: inanna.dumuzi66@gmail.com
 * @returns {boolean} True if user is admin
 */
export const isAdmin = () => {
  const user = getUser();
  return user && user.user_id === 'inanna.dumuzi66@gmail.com';
};

/**
 * Initialize auth service (restore token from storage)
 * Call this when app starts to restore authentication state
 */
export const initAuth = () => {
  const token = getToken();
  if (token) {
    api.defaults.headers.common['Authorization'] = `Bearer ${token}`;
  }
};

/**
 * Axios interceptor to handle 401 errors (token expiration)
 */
api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      // Token expired or invalid, logout user
      logout();
      // Optionally redirect to login page
      window.location.href = '/login';
    }
    return Promise.reject(error);
  }
);

// Initialize auth on module load
initAuth();

export default {
  register,
  login,
  logout,
  getToken,
  getUser,
  getRole,
  isAuthenticated,
  hasRole,
  isAdmin,
  initAuth,
};
