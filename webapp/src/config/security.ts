// webapp/src/config/security.ts
/**
 * Frontend security configuration
 */

// Extend ImportMeta interface for Vite env variables
/// <reference types="vite/client" />
interface ImportMetaEnv {
    readonly VITE_API_URL?: string;
    // add other env variables here as needed
}

interface ImportMeta {
    readonly env: ImportMetaEnv;
}

export const SecurityConfig = {
    // API endpoints
    API_URL: import.meta.env.VITE_API_URL || 'http://localhost:8000',

    // Token management
    TOKEN_KEY: 'quantum_commerce_token',
    USER_KEY: 'quantum_commerce_user',

    // Security headers
    getAuthHeaders: () => {
        const token = localStorage.getItem(SecurityConfig.TOKEN_KEY);
        return token ? { Authorization: `Bearer ${token}` } : {};
    },

    // XSS protection
    sanitizeInput: (input: string): string => {
        return input
            .replace(/</g, '&lt;')
            .replace(/>/g, '&gt;')
            .replace(/"/g, '&quot;')
            .replace(/'/g, '&#x27;')
            .replace(/\//g, '&#x2F;');
    },

    // CSRF token
    getCSRFToken: (): string => {
        return document.querySelector('meta[name="csrf-token"]')?.getAttribute('content') || '';
    }
  };