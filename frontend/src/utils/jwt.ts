// src/utils/jwt.ts
// Funções utilitárias para trabalhar com JWT no frontend

export function decodeJwtPayload(token: string): any | null {
  try {
    const parts = token.split('.');
    if (parts.length !== 3) {
      return null;
    }

    const payload = parts[1];

    // Ajusta base64url -> base64
    let base64 = payload.replace(/-/g, '+').replace(/_/g, '/');
    const padding = base64.length % 4;
    if (padding) {
      base64 += '='.repeat(4 - padding);
    }

    const decoded = atob(base64);
    return JSON.parse(decoded);
  } catch (error) {
    console.warn('[JWT] Falha ao decodificar token', error);
    return null;
  }
}
