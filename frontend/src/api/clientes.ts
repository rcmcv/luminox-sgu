// src/api/clientes.ts
// Funções de acesso à API de Clientes.

import api from './client';
import type { Cliente } from '../types/cliente';

export interface ClienteListEnvelope {
  items?: Cliente[];
  data?: Cliente[];
  results?: Cliente[];
  [key: string]: unknown;
}

// Ajuste a URL abaixo se sua API usar outro caminho para clientes
const CLIENTES_ENDPOINT = '/api/v1/clientes';

export async function fetchClientes(): Promise<Cliente[]> {
  try {
    const response = await api.get<Cliente[] | ClienteListEnvelope>(
      CLIENTES_ENDPOINT,
    );

    const data = response.data;

    // Se a API retornar diretamente um array
    if (Array.isArray(data)) {
      return data;
    }

    // Alguns formatos comuns de envelope
    if (Array.isArray(data.items)) return data.items;
    if (Array.isArray(data.data)) return data.data;
    if (Array.isArray(data.results)) return data.results;

    return [];
  } catch (error) {
    console.warn('[Clientes] Erro ao buscar clientes, retornando lista vazia:', error);
    // Importante: não propaga o erro, devolve lista vazia
    return [];
  }
}
