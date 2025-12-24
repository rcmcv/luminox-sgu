// src/auth/useAuth.tsx
// Contexto de autenticação + hook useAuth,
// inspirado no fluxo simples do Labgest (token no localStorage).

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

export type UserRole = 'ADMIN' | 'OPERACAO' | 'VIEWER' | string;

export interface User {
  id: number;
  email: string;
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

export const AuthProvider: React.FC<AuthProviderProps> = ({ children }) => {
  const [user, setUser] = useState<User | null>(null);
  const [loading, setLoading] = useState<boolean>(true);

  // Busca o usuário atual em /users/me
  const loadCurrentUser = useCallback(async () => {
    try {
      const response = await api.get<User>('/api/v1/users/me');
      setUser(response.data);
    } catch (error) {
      console.warn('[Auth] Falha ao carregar /users/me', error);
      setUser(null);
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    // Só tenta carregar /me se já existir access_token salvo
    const token = getAccessToken();
    if (!token) {
      setLoading(false);
      return;
    }

    loadCurrentUser();
  }, [loadCurrentUser]);

  const login = useCallback(
    async (email: string, password: string) => {
      const response = await api.post<LoginResponse>('/api/v1/auth/login', {
        email,
        password,
      });

      const { access_token, refresh_token, user: userData } = response.data;

      // Salva tokens no localStorage
      setAuthTokens(access_token, refresh_token);

      // Marca como logado imediatamente (via token)
      if (userData) {
        setUser(userData);
      } else {
        // Tenta buscar os dados do usuário, mas falha aqui não bloqueia o acesso
        try {
          await loadCurrentUser();
        } catch {
          // ignora
        }
      }
    },
    [loadCurrentUser],
  );

  const logout = useCallback(() => {
    clearAuthTokens();
    setUser(null);
  }, []);

  // *** PONTO IMPORTANTE ***
  // A partir de agora, "autenticado" é quem TEM TOKEN, não quem tem user carregado
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
