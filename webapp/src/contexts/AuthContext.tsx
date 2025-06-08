import React, { createContext, useContext, useState, useEffect } from 'react';
import api from '../services/api';
import { SecurityConfig } from '../config/security';

interface User {
    id: string;
    email: string;
    name: string;
    user_type: string;
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
            // Verify token and get user info
            api.defaults.headers.common['Authorization'] = `Bearer ${token}`;
            // In production, make API call to get user info
            const savedUser = localStorage.getItem(SecurityConfig.USER_KEY);
            if (savedUser) {
                setUser(JSON.parse(savedUser));
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

            const { access_token, user_id, email: userEmail } = response.data;

            const userData = {
                id: user_id,
                email: userEmail,
                name: userEmail.split('@')[0],
                user_type: response.data.user_type || 'customer'
            };

            localStorage.setItem(SecurityConfig.TOKEN_KEY, access_token);
            localStorage.setItem(SecurityConfig.USER_KEY, JSON.stringify(userData));

            setToken(access_token);
            setUser(userData);

            api.defaults.headers.common['Authorization'] = `Bearer ${access_token}`;
        } catch (error) {
            throw error;
        }
    };

    const register = async (email: string, name: string, password: string) => {
        try {
            const response = await api.post('/api/auth/register', {
                email,
                username: name,
                password,
                full_name: name,
                user_type: 'customer'
            });

            const { access_token, user_id, email: userEmail } = response.data;

            const userData = {
                id: user_id,
                email: userEmail,
                name: name,
                user_type: 'customer'
            };

            localStorage.setItem(SecurityConfig.TOKEN_KEY, access_token);
            localStorage.setItem(SecurityConfig.USER_KEY, JSON.stringify(userData));

            setToken(access_token);
            setUser(userData);

            api.defaults.headers.common['Authorization'] = `Bearer ${access_token}`;
        } catch (error) {
            throw error;
        }
    };

    const logout = () => {
        localStorage.removeItem(SecurityConfig.TOKEN_KEY);
        localStorage.removeItem(SecurityConfig.USER_KEY);
        delete api.defaults.headers.common['Authorization'];
        setToken(null);
        setUser(null);
    };

    return (
        <AuthContext.Provider value={{ user, token, login, register, logout, loading }}>
            {children}
        </AuthContext.Provider>
    );
}