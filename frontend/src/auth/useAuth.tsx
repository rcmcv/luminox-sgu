// src/auth/useAuth.tsx
// Contexto de autenticação + hook useAuth,
// agora lendo dados básicos do usuário direto do JWT (access_token).

import React, {
  createContext,
  useCallback,
  useContext,
  useEffect,
  useState,
} from 'react';
import api, {
  clearAuthTokens,
  setAuthTokens,
  getAccessToken,
} from '../api/client';
import { decodeJwtPayload } from '../utils/jwt';

export type UserRole = 'ADMIN' | 'OPERACAO' | 'VIEWER' | string;

export interface User {
  id?: number;
  email?: string;
  name?: string;
  role?: UserRole;
}

// Resposta esperada do backend no login
type LoginResponse = {
  access_token: string;
  refresh_token?: string;
  token_type?: string;
  user?: User;
};

interface AuthContextValue {
  user: User | null;
  isAuthenticated: boolean;
  loading: boolean;
  login: (email: string, password: string) => Promise<void>;
  logout: () => void;
}

const AuthContext = createContext<AuthContextValue | undefined>(undefined);

interface AuthProviderProps {
  children: React.ReactNode;
}

// Constrói um User a partir do payload do JWT
function buildUserFromToken(token: string): User | null {
  const payload = decodeJwtPayload(token);
  if (!payload) {
    return null;
  }

  const id =
    (payload.id as number | undefined) ??
    (payload.user_id as number | undefined);

  const email =
    (payload.email as string | undefined) ??
    (payload.sub as string | undefined);

  const name =
    (payload.name as string | undefined) ??
    (payload.full_name as string | undefined) ??
    (payload.username as string | undefined) ??
    email ??
    'Usuário';

  const role =
    (payload.role as string | undefined) ??
    (payload.perfil as string | undefined) ??
    ((Array.isArray(payload.scopes) && payload.scopes[0]) as string | undefined);

  return {
    id,
    email,
    name,
    role,
  };
}

export const AuthProvider: React.FC<AuthProviderProps> = ({ children }) => {
  const [user, setUser] = useState<User | null>(null);
  const [loading, setLoading] = useState<boolean>(true);

  // Ao montar o app, tenta montar o usuário a partir do token já salvo
  useEffect(() => {
    const token = getAccessToken();
    if (!token) {
      setLoading(false);
      return;
    }

    const tokenUser = buildUserFromToken(token);
    setUser(tokenUser);
    setLoading(false);
  }, []);

  const login = useCallback(async (email: string, password: string) => {
    const response = await api.post<LoginResponse>('/api/v1/auth/login', {
      email,
      password,
    });

    const { access_token, refresh_token, user: userData } = response.data;

    // Salva tokens no localStorage
    setAuthTokens(access_token, refresh_token);

    // Monta usuário:
    // 1) se backend já enviar user no login, aproveita
    // 2) se não, decodifica do token
    if (userData) {
      setUser(userData);
    } else {
      const tokenUser = buildUserFromToken(access_token);
      setUser(tokenUser);
    }
  }, []);

  const logout = useCallback(() => {
    clearAuthTokens();
    setUser(null);
  }, []);

  // Autenticado = existe access_token no localStorage
  const isAuthenticated = !!getAccessToken();

  const value: AuthContextValue = {
    user,
    isAuthenticated,
    loading,
    login,
    logout,
  };

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
};

export const useAuth = (): AuthContextValue => {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error('useAuth deve ser usado dentro de um AuthProvider');
  }
  return context;
};
