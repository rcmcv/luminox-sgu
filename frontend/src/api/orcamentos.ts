// src/api/orcamentos.ts
// Funções de acesso à API de Orçamentos.

import api from './client';
import type { Orcamento } from '../types/orcamento';

export interface OrcamentoListEnvelope {
  items?: Orcamento[];
  data?: Orcamento[];
  results?: Orcamento[];
  [key: string]: unknown;
}

// 👉 Se o endpoint no backend for diferente, ajustar APENAS esta linha.
const ORCAMENTOS_ENDPOINT = '/api/v1/orcamentos';

export async function fetchOrcamentos(): Promise<Orcamento[]> {
  try {
    const response = await api.get<Orcamento[] | OrcamentoListEnvelope>(
      ORCAMENTOS_ENDPOINT,
    );

    const data = response.data;

    // Caso a API retorne um array diretamente
    if (Array.isArray(data)) {
      return data;
    }

    // Caso venha em um envelope { items: [...] } / { data: [...] } / { results: [...] }
    if (Array.isArray((data as OrcamentoListEnvelope).items)) {
      return (data as OrcamentoListEnvelope).items as Orcamento[];
    }
    if (Array.isArray((data as OrcamentoListEnvelope).data)) {
      return (data as OrcamentoListEnvelope).data as Orcamento[];
    }
    if (Array.isArray((data as OrcamentoListEnvelope).results)) {
      return (data as OrcamentoListEnvelope).results as Orcamento[];
    }

    console.warn(
      '[Orçamentos] Resposta inesperada da API, retornando lista vazia:',
      data,
    );
    return [];
  } catch (error: any) {
    // Log detalhado para debug
    if (error?.response) {
      console.error(
        '[Orçamentos] Erro na API:',
        error.response.status,
        error.response.data,
      );
    } else {
      console.error('[Orçamentos] Erro ao chamar API:', error);
    }

    // Propaga o erro para o componente mostrar mensagem amigável
    throw error;
  }
}
