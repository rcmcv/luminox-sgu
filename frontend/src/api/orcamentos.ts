// src/api/orcamentos.ts
// Funções de acesso à API de Orçamentos.

import api from './client';
import type {
  Orcamento,
  OrcamentoStatus,
  OrcamentoTipo,
} from '../types/orcamento';

// Envelope que o helper `created(...)` usa
interface CreatedEnvelope {
  data?: Orcamento;
  message?: string;
  [key: string]: unknown;
}

export interface OrcamentoListEnvelope {
  items?: Orcamento[];
  data?: Orcamento[];
  results?: Orcamento[];
  [key: string]: unknown;
}

// 👉 Já ajustado anteriormente; se mudar no backend, é só alterar aqui.
export const ORCAMENTOS_ENDPOINT = '/api/v1/orcamentos';

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
    if (error?.response) {
      console.error(
        '[Orçamentos] Erro na API:',
        error.response.status,
        error.response.data,
      );
    } else {
      console.error('[Orçamentos] Erro ao chamar API:', error);
    }

    throw error;
  }
}

export async function fetchOrcamentoById(id: number): Promise<Orcamento> {
  try {
    const response = await api.get<Orcamento>(
      `${ORCAMENTOS_ENDPOINT}/${id}`,
    );
    return response.data;
  } catch (error: any) {
    if (error?.response) {
      console.error(
        '[Orçamentos] Erro ao buscar orçamento por id:',
        id,
        error.response.status,
        error.response.data,
      );
    } else {
      console.error(
        '[Orçamentos] Erro ao chamar API de orçamento por id:',
        id,
        error,
      );
    }
    throw error;
  }
}

// Payload para criação de orçamento.
// Alinhado ao OrcamentoOut, mas campos numéricos podem ser opcionais
// (backend pode assumir 0 ou recalcular).
export interface OrcamentoCreateInput {
  cliente_id: number;
  tipo: OrcamentoTipo;
  status: OrcamentoStatus;
  contrato_id?: number | null;
  moeda: string;
  titulo?: string | null;
  observacoes?: string | null;
  subtotal?: number;
  desconto?: number;
  acrescimo?: number;
  total?: number;
}

export async function createOrcamento(
  payload: OrcamentoCreateInput,
): Promise<Orcamento> {
  try {
    const response = await api.post<Orcamento | CreatedEnvelope>(
      ORCAMENTOS_ENDPOINT,
      payload,
    );

    const data = response.data as Orcamento | CreatedEnvelope;

    // Se vier como { data: {...}, message: "..." }
    if ((data as CreatedEnvelope).data) {
      return (data as CreatedEnvelope).data as Orcamento;
    }

    // Se no futuro você mudar o backend pra devolver o objeto direto:
    return data as Orcamento;
  } catch (error: any) {
    if (error?.response) {
      console.error(
        '[Orçamentos] Erro ao criar orçamento:',
        error.response.status,
        error.response.data,
      );
    } else {
      console.error('[Orçamentos] Erro ao chamar API de criação:', error);
    }
    throw error;
  }
}
