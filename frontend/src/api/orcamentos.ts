// src/api/orcamentos.ts
// Funções de acesso à API de Orçamentos.

import api from './client';
import type { Orcamento } from '../types/orcamento';

// Tipos genéricos para lidar com diferentes formatos de resposta paginada
export interface OrcamentoListEnvelope {
  items?: Orcamento[];
  data?: Orcamento[];
  results?: Orcamento[];
  [key: string]: unknown;
}

export async function fetchOrcamentos(): Promise<Orcamento[]> {
  const response = await api.get<Orcamento[] | OrcamentoListEnvelope>(
    '/api/v1/orcamentos',
  );

  const data = response.data as Orcamento[] | OrcamentoListEnvelope;

  // Se a API retornar diretamente um array
  if (Array.isArray(data)) {
    return data;
  }

  // Se retornar em "items", "data" ou "results"
  if (Array.isArray(data.items)) return data.items;
  if (Array.isArray(data.data)) return data.data;
  if (Array.isArray(data.results)) return data.results;

  // Fallback
  return [];
}
