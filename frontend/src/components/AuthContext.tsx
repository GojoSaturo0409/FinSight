import { createContext, useContext, useState, useEffect } from 'react';
import type { ReactNode } from 'react';
import { API_BASE } from '../api';

interface AuthState {
    token: string | null;
    user: { email: string } | null;
    isAuthenticated: boolean;
    login: (email: string, password: string) => Promise<{ ok: boolean; error?: string }>;
    register: (email: string, password: string) => Promise<{ ok: boolean; error?: string }>;
    logout: () => void;
}

const AuthContext = createContext<AuthState>({
    token: null,
    user: null,
    isAuthenticated: false,
    login: async () => ({ ok: false }),
    register: async () => ({ ok: false }),
    logout: () => { },
});

export const useAuth = () => useContext(AuthContext);

export const AuthProvider = ({ children }: { children: ReactNode }) => {
    const [token, setToken] = useState<string | null>(
        localStorage.getItem('finsight_token')
    );
    const [user, setUser] = useState<{ email: string } | null>(null);

    useEffect(() => {
        if (token) {
            try {
                const payload = JSON.parse(atob(token.split('.')[1]));
                setUser({ email: payload.sub });
            } catch {
                setUser(null);
            }
        } else {
            setUser(null);
        }
    }, [token]);

    const login = async (email: string, password: string) => {
        try {
            const formData = new URLSearchParams();
            formData.append('username', email);
            formData.append('password', password);

            const res = await fetch(`${API_BASE}/auth/login`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
                body: formData.toString(),
            });

            if (res.ok) {
                const data = await res.json();
                localStorage.setItem('finsight_token', data.access_token);
                setToken(data.access_token);
                return { ok: true };
            } else {
                const err = await res.json().catch(() => ({ detail: 'Login failed' }));
                return { ok: false, error: err.detail || 'Login failed' };
            }
        } catch {
            return { ok: false, error: 'Cannot connect to server' };
        }
    };

    const register = async (email: string, password: string) => {
        try {
            const res = await fetch(
                `${API_BASE}/auth/register?email=${encodeURIComponent(email)}&password=${encodeURIComponent(password)}`,
                { method: 'POST' }
            );

            if (res.ok) {
                return await login(email, password);
            } else {
                const err = await res.json().catch(() => ({ detail: 'Registration failed' }));
                return { ok: false, error: err.detail || 'Registration failed' };
            }
        } catch {
            return { ok: false, error: 'Cannot connect to server' };
        }
    };

    const logout = () => {
        localStorage.removeItem('finsight_token');
        setToken(null);
        setUser(null);
    };

    return (
        <AuthContext.Provider value={{ token, user, isAuthenticated: !!token, login, register, logout }}>
            {children}
        </AuthContext.Provider>
    );
};

export default AuthContext;
