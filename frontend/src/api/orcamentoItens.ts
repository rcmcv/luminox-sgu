// src/api/orcamentoItens.ts
// Funções de acesso à API de itens de orçamento.

import api from './client';
import type { OrcamentoItem } from '../types/orcamentoItem';

// Envelope genérico, caso a API use items/data/results
export interface OrcamentoItemListEnvelope {
  items?: OrcamentoItem[];
  data?: OrcamentoItem[];
  results?: OrcamentoItem[];
  [key: string]: unknown;
}

// 👉 Ajuste este endpoint quando soubermos o caminho exato do backend.
// Exemplo comum: /api/v1/orcamentos/{id}/itens
const ORCAMENTO_ITENS_BASE = '/api/v1/orcamentos';

export async function fetchOrcamentoItens(
  orcamentoId: number,
): Promise<OrcamentoItem[]> {
  const url = `${ORCAMENTO_ITENS_BASE}/${orcamentoId}/itens`;

  try {
    const response = await api.get<OrcamentoItem[] | OrcamentoItemListEnvelope>(
      url,
    );

    const data = response.data;

    if (Array.isArray(data)) {
      return data;
    }

    if (Array.isArray(data.items)) return data.items;
    if (Array.isArray(data.data)) return data.data;
    if (Array.isArray(data.results)) return data.results;

    console.warn(
      '[Orçamento Itens] Resposta inesperada da API, retornando lista vazia:',
      data,
    );
    return [];
  } catch (error: any) {
    console.warn(
      '[Orçamento Itens] Erro ao buscar itens, retornando lista vazia:',
      url,
      error?.response?.status,
      error?.response?.data ?? error,
    );
    // Não propaga o erro para não quebrar a tela de detalhes do orçamento
    return [];
  }
}
