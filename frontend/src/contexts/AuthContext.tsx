import { createContext, useContext, useState, useCallback, type ReactNode } from 'react';
import { login as apiLogin, register as apiRegister } from '../services/api';
import type { User } from '../types';

interface AuthState {
  user: User | null;
  token: string | null;
  loading: boolean;
}

interface AuthContextType extends AuthState {
  login: (email: string, password: string) => Promise<void>;
  register: (email: string, password: string, name: string) => Promise<void>;
  logout: () => void;
}

const AuthContext = createContext<AuthContextType | null>(null);

const TOKEN_KEY = 'precoperto_token';
const USER_KEY = 'precoperto_user';

export const AuthProvider = ({ children }: { children: ReactNode }) => {
  const [state, setState] = useState<AuthState>(() => {
    const token = localStorage.getItem(TOKEN_KEY);
    const userStr = localStorage.getItem(USER_KEY);
    let user: User | null = null;
    if (token && userStr) {
      try {
        user = JSON.parse(userStr);
      } catch {
        localStorage.removeItem(TOKEN_KEY);
        localStorage.removeItem(USER_KEY);
      }
    }
    return { user, token, loading: false };
  });

  const saveAuth = useCallback((token: string, user: User) => {
    localStorage.setItem(TOKEN_KEY, token);
    localStorage.setItem(USER_KEY, JSON.stringify(user));
    setState({ user, token, loading: false });
  }, []);

  const clearAuth = useCallback(() => {
    localStorage.removeItem(TOKEN_KEY);
    localStorage.removeItem(USER_KEY);
    setState({ user: null, token: null, loading: false });
  }, []);

  const login = useCallback(async (email: string, password: string) => {
    setState(prev => ({ ...prev, loading: true }));
    try {
      const data = await apiLogin(email, password);
      saveAuth(data.access_token, data.user);
    } catch (err) {
      setState(prev => ({ ...prev, loading: false }));
      throw err;
    }
  }, [saveAuth]);

  const register = useCallback(async (email: string, password: string, name: string) => {
    setState(prev => ({ ...prev, loading: true }));
    try {
      const data = await apiRegister(email, password, name);
      saveAuth(data.access_token, data.user);
    } catch (err) {
      setState(prev => ({ ...prev, loading: false }));
      throw err;
    }
  }, [saveAuth]);

  const logout = useCallback(() => {
    clearAuth();
  }, [clearAuth]);

  return (
    <AuthContext.Provider value={{ ...state, login, register, logout }}>
      {children}
    </AuthContext.Provider>
  );
};

// eslint-disable-next-line react/only-export-components
export const useAuth = () => {
  const ctx = useContext(AuthContext);
  if (!ctx) throw new Error('useAuth must be used inside AuthProvider');
  return ctx;
};
