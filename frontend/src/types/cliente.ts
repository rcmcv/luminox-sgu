// src/types/cliente.ts
// Tipos relacionados a Clientes. Campos opcionais para se adaptar ao backend.

export interface Cliente {
  id: number;
  nome?: string | null;
  nome_fantasia?: string | null;
  razao_social?: string | null;

  // Campos extras que o backend possa enviar
  [key: string]: unknown;
}
