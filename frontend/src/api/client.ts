// src/api/client.ts
// Cliente Axios centralizado com interceptors de autenticação e refresh token,
// inspirado no Labgest, mas em TypeScript simples.

import axios from 'axios';

const API_BASE_URL = import.meta.env.VITE_API_URL ?? 'http://127.0.0.1:8000';

const ACCESS_TOKEN_KEY = 'luminox_access_token';
const REFRESH_TOKEN_KEY = 'luminox_refresh_token';

export function getAccessToken(): string | null {
  return localStorage.getItem(ACCESS_TOKEN_KEY);
}

export function getRefreshToken(): string | null {
  return localStorage.getItem(REFRESH_TOKEN_KEY);
}

export function setAuthTokens(accessToken: string, refreshToken?: string): void {
  localStorage.setItem(ACCESS_TOKEN_KEY, accessToken);
  if (refreshToken) {
    localStorage.setItem(REFRESH_TOKEN_KEY, refreshToken);
  }
}

export function clearAuthTokens(): void {
  localStorage.removeItem(ACCESS_TOKEN_KEY);
  localStorage.removeItem(REFRESH_TOKEN_KEY);
}

// Instância principal da API
const api = axios.create({
  baseURL: API_BASE_URL,
});

// Instância separada pro refresh, pra evitar interceptor recursivo
const refreshClient = axios.create({
  baseURL: API_BASE_URL,
});

let isRefreshing = false;
let pendingRequests: {
  resolve: (value?: unknown) => void;
  reject: (reason?: unknown) => void;
}[] = [];

function processPendingRequests(error: unknown, token?: string) {
  pendingRequests.forEach((p) => {
    if (error) {
      p.reject(error);
    } else {
      p.resolve(token);
    }
  });
  pendingRequests = [];
}

// Interceptor de requisição: adiciona Authorization se houver token
api.interceptors.request.use(
  (config: any) => {
    const token = getAccessToken();

    if (!config.headers) {
      config.headers = {};
    }

    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }

    return config;
  },
  (error) => Promise.reject(error),
);

// Interceptor de resposta: tenta refresh em caso de 401
api.interceptors.response.use(
  (response) => response,
  async (error: any) => {
    const originalRequest = error.config as any;

    // Se não houver resposta ou requisição original, só rejeita
    if (!error.response || !originalRequest) {
      return Promise.reject(error);
    }

    const status = error.response.status;

    // Se não for 401, não vamos mexer
    if (status !== 401) {
      return Promise.reject(error);
    }

    const url: string | undefined = originalRequest.url;

    // Não tentar refresh/redirect para endpoints de login/refresh
    if (
      url &&
      (url.includes('/api/v1/auth/login') ||
        url.includes('/api/v1/auth/refresh'))
    ) {
      return Promise.reject(error);
    }

    // Evita loop infinito
    if (originalRequest._retry) {
      return Promise.reject(error);
    }

    const refreshToken = getRefreshToken();
    if (!refreshToken) {
      clearAuthTokens();
      window.location.href = '/login';
      return Promise.reject(error);
    }

    if (isRefreshing) {
      // Já tem um refresh em andamento, coloca essa requisição na fila
      return new Promise((resolve, reject) => {
        pendingRequests.push({
          resolve: (token: unknown) => {
            if (typeof token === 'string') {
              originalRequest.headers = {
                ...(originalRequest.headers ?? {}),
                Authorization: `Bearer ${token}`,
              };
            }
            resolve(api(originalRequest));
          },
          reject,
        });
      });
    }

    originalRequest._retry = true;
    isRefreshing = true;

    try {
      const response = await refreshClient.post('/api/v1/auth/refresh', {
        refresh_token: refreshToken,
      });

      const newAccessToken: string = response.data.access_token;
      const newRefreshToken: string | undefined = response.data.refresh_token;

      setAuthTokens(newAccessToken, newRefreshToken);
      api.defaults.headers.common.Authorization = `Bearer ${newAccessToken}`;

      processPendingRequests(null, newAccessToken);
      isRefreshing = false;

      originalRequest.headers = {
        ...(originalRequest.headers ?? {}),
        Authorization: `Bearer ${newAccessToken}`,
      };

      return api(originalRequest);
    } catch (err) {
      processPendingRequests(err);
      isRefreshing = false;
      clearAuthTokens();
      window.location.href = '/login';
      return Promise.reject(err);
    }
  },
);

export default api;
