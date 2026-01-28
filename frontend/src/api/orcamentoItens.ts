// src/api/orcamentoItens.ts
// Cliente de API para itens de orçamento, alinhado com o backend.

import api from './client';
import { ORCAMENTOS_ENDPOINT } from './orcamentos';
import type {
  OrcamentoItem,
  OrcamentoItemCreateInput,
} from '../types/orcamentoItem';

interface ApiListResponse<T> {
  data: T[];
  message?: string | null;
  meta?: {
    page?: number;
    size?: number;
    count?: number;
  } | null;
}

interface ApiSingleResponse<T> {
  data: T;
  message?: string | null;
}

/**
 * Lista os itens de um orçamento específico.
 * GET /orcamentos/{orcamento_id}/itens
 */
export async function fetchOrcamentoItens(
  orcamentoId: number,
): Promise<OrcamentoItem[]> {
  const res = await api.get<ApiListResponse<OrcamentoItem>>(
    `${ORCAMENTOS_ENDPOINT}/${orcamentoId}/itens`,
  );
  return res.data?.data ?? [];
}

/**
 * Busca um único item de orçamento.
 * GET /orcamentos/{orcamento_id}/itens/{item_id}
 */
export async function fetchOrcamentoItemById(
  orcamentoId: number,
  itemId: number,
): Promise<OrcamentoItem> {
  const res = await api.get<ApiSingleResponse<OrcamentoItem>>(
    `/orcamentos/${orcamentoId}/itens/${itemId}`,
  );
  return res.data.data;
}

/**
 * Cria um item em um orçamento.
 * POST /orcamentos/{orcamento_id}/itens
 */
export async function createOrcamentoItem(
  orcamentoId: number,
  payload: OrcamentoItemCreateInput,
): Promise<OrcamentoItem> {
  const res = await api.post<ApiSingleResponse<OrcamentoItem>>(
    `${ORCAMENTOS_ENDPOINT}/${orcamentoId}/itens`,
    payload,
  );
  return res.data.data;
}

/**
 * Atualiza um item de orçamento.
 * PUT /orcamentos/{orcamento_id}/itens/{item_id}
 */
export async function updateOrcamentoItem(
  orcamentoId: number,
  itemId: number,
  payload: Partial<OrcamentoItemCreateInput>,
): Promise<OrcamentoItem> {
  const res = await api.put<ApiSingleResponse<OrcamentoItem>>(
    `${ORCAMENTOS_ENDPOINT}/${orcamentoId}/itens/${itemId}`,
    payload,
  );
  return res.data.data;
}

/**
 * Remove um item de orçamento.
 * DELETE /orcamentos/{orcamento_id}/itens/{item_id}
 */
export async function deleteOrcamentoItem(
  orcamentoId: number,
  itemId: number,
): Promise<void> {
  await api.delete(
    `${ORCAMENTOS_ENDPOINT}/${orcamentoId}/itens/${itemId}`,
  );
}
