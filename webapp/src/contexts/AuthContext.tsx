import React, { createContext, useContext, useState, useEffect } from 'react';
import axios from 'axios';

const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

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
    const [token, setToken] = useState<string | null>(localStorage.getItem('token'));
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        if (token) {
            // Verify token and get user info
            axios.defaults.headers.common['Authorization'] = `Bearer ${token}`;
            // In production, make API call to get user info
            const savedUser = localStorage.getItem('user');
            if (savedUser) {
                setUser(JSON.parse(savedUser));
            }
        }
        setLoading(false);
    }, [token]);

    const login = async (email: string, password: string) => {
        try {
            const response = await axios.post(`${API_URL}/api/auth/login`, {
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

            localStorage.setItem('token', access_token);
            localStorage.setItem('user', JSON.stringify(userData));

            setToken(access_token);
            setUser(userData);

            axios.defaults.headers.common['Authorization'] = `Bearer ${access_token}`;
        } catch (error) {
            throw error;
        }
    };

    const register = async (email: string, name: string, password: string) => {
        try {
            const response = await axios.post(`${API_URL}/api/auth/register`, {
                email,
                name,
                password,
                user_type: 'customer'
            });

            const { access_token, user_id, email: userEmail } = response.data;

            const userData = {
                id: user_id,
                email: userEmail,
                name: name,
                user_type: 'customer'
            };

            localStorage.setItem('token', access_token);
            localStorage.setItem('user', JSON.stringify(userData));

            setToken(access_token);
            setUser(userData);

            axios.defaults.headers.common['Authorization'] = `Bearer ${access_token}`;
        } catch (error) {
            throw error;
        }
    };

    const logout = () => {
        localStorage.removeItem('token');
        localStorage.removeItem('user');
        delete axios.defaults.headers.common['Authorization'];
        setToken(null);
        setUser(null);
    };

    return (
        <AuthContext.Provider value={{ user, token, login, register, logout, loading }}>
            {children}
        </AuthContext.Provider>
    );
}