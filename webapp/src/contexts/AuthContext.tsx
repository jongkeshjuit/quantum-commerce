// webapp/src/contexts/AuthContext.tsx - FIXED VERSION
import React, { createContext, useContext, useState, useEffect } from 'react';
import api from '../services/api';
import { SecurityConfig } from '../config/security';

interface User {
    id: string;
    email: string;
    name: string;
    username: string;
    user_type: string;
    is_admin?: boolean;
}

interface AuthContextType {
    user: User | null;
    token: string | null;
    login: (email: string, password: string) => Promise<void>;
    register: (email: string, name: string, password: string) => Promise<void>;
    logout: () => void;
    loading: boolean;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export function useAuth() {
    const context = useContext(AuthContext);
    if (!context) {
        throw new Error('useAuth must be used within AuthProvider');
    }
    return context;
}

export function AuthProvider({ children }: { children: React.ReactNode }) {
    const [user, setUser] = useState<User | null>(null);
    const [token, setToken] = useState<string | null>(localStorage.getItem(SecurityConfig.TOKEN_KEY));
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        if (token) {
            api.defaults.headers.common['Authorization'] = `Bearer ${token}`;
            const savedUser = localStorage.getItem(SecurityConfig.USER_KEY);
            if (savedUser) {
                try {
                    setUser(JSON.parse(savedUser));
                } catch (error) {
                    console.error('Error parsing saved user:', error);
                    localStorage.removeItem(SecurityConfig.USER_KEY);
                    localStorage.removeItem(SecurityConfig.TOKEN_KEY);
                    setToken(null);
                }
            }
        }
        setLoading(false);
    }, [token]);

    const login = async (email: string, password: string) => {
        try {
            const response = await api.post('/api/auth/login', {
                email,
                password
            });

            console.log('Login response:', response.data); // Debug log

            // Handle different response structures from backend
            const userData: User = {
                id: response.data.user?.id || response.data.user_id || response.data.id,
                email: response.data.user?.email || response.data.email || email,
                name: response.data.user?.full_name || response.data.user?.username || response.data.username || response.data.name || email.split('@')[0],
                username: response.data.user?.username || response.data.username || email.split('@')[0],
                user_type: (response.data.user?.is_admin || response.data.is_admin) ? 'admin' : 'customer',
                is_admin: response.data.user?.is_admin || response.data.is_admin || false
            };

            const accessToken = response.data.access_token;

            if (!accessToken) {
                throw new Error('No access token received');
            }

            localStorage.setItem(SecurityConfig.TOKEN_KEY, accessToken);
            localStorage.setItem(SecurityConfig.USER_KEY, JSON.stringify(userData));

            setToken(accessToken);
            setUser(userData);

            api.defaults.headers.common['Authorization'] = `Bearer ${accessToken}`;
            
            console.log('Login successful:', userData); // Debug log
        } catch (error: any) {
            console.error('Login error:', error.response?.data || error.message);
            throw error;
        }
    };

    const register = async (email: string, name: string, password: string) => {
        try {
            const response = await api.post('/api/auth/register', {
                email,
                username: name,
                password,
                full_name: name
            });

            console.log('Register response:', response.data); // Debug log

            // Handle registration response
            const userData: User = {
                id: response.data.user?.id || response.data.user_id || response.data.id,
                email: response.data.user?.email || response.data.email || email,
                name: response.data.user?.full_name || response.data.user?.username || response.data.username || name,
                username: response.data.user?.username || response.data.username || name,
                user_type: (response.data.user?.is_admin || response.data.is_admin) ? 'admin' : 'customer',
                is_admin: response.data.user?.is_admin || response.data.is_admin || false
            };

            const accessToken = response.data.access_token;

            if (!accessToken) {
                throw new Error('No access token received');
            }

            localStorage.setItem(SecurityConfig.TOKEN_KEY, accessToken);
            localStorage.setItem(SecurityConfig.USER_KEY, JSON.stringify(userData));

            setToken(accessToken);
            setUser(userData);

            api.defaults.headers.common['Authorization'] = `Bearer ${accessToken}`;
            
            console.log('Registration successful:', userData); // Debug log
        } catch (error: any) {
            console.error('Registration error:', error.response?.data || error.message);
            throw error;
        }
    };

    const logout = () => {
        localStorage.removeItem(SecurityConfig.TOKEN_KEY);
        localStorage.removeItem(SecurityConfig.USER_KEY);
        delete api.defaults.headers.common['Authorization'];
        setToken(null);
        setUser(null);
        console.log('Logout successful'); // Debug log
    };

    return (
        <AuthContext.Provider value={{ user, token, login, register, logout, loading }}>
            {children}
        </AuthContext.Provider>
    );
}