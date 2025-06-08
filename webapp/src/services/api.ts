// webapp/src/services/api.ts
/**
 * Secure API service
 */
import axios from 'axios';
import { SecurityConfig } from '../config/security';

// Create axios instance
const api = axios.create({
    baseURL: SecurityConfig.API_URL,
    timeout: 30000,
    headers: {
        'Content-Type': 'application/json',
    }
});

// Request interceptor
api.interceptors.request.use(
    (config) => {
        // Add auth token
        const token = localStorage.getItem(SecurityConfig.TOKEN_KEY);
        if (token) {
            config.headers.Authorization = `Bearer ${token}`;
        }

        // Add CSRF token
        const csrfToken = SecurityConfig.getCSRFToken();
        if (csrfToken) {
            config.headers['X-CSRF-Token'] = csrfToken;
        }

        return config;
    },
    (error) => {
        return Promise.reject(error);
    }
);

// Response interceptor
api.interceptors.response.use(
    (response) => response,
    (error) => {
        if (error.response?.status === 401) {
            // Token expired or invalid
            localStorage.removeItem(SecurityConfig.TOKEN_KEY);
            localStorage.removeItem(SecurityConfig.USER_KEY);
            window.location.href = '/login';
        }

        return Promise.reject(error);
    }
);

export default api;