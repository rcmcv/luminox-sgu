// src/types/orcamento.ts
// Tipos relacionados a Orçamentos.
// OBS: alguns campos são opcionais para se adaptar ao backend sem quebrar.

export type OrcamentoStatus = 'ABERTO' | 'APROVADO' | 'CANCELADO' | string;

export interface Orcamento {
  id: number;

  // Identificação
  codigo?: string;       // ex: "ORC-001"
  numero?: string;       // se backend usar "numero" em vez de "codigo"

  // Cliente
  cliente?: string;      // nome simples
  cliente_nome?: string; // alternativa comum
  // ou se o backend retornar objeto:
  // cliente: { id: number; nome: string; ... }

  // Valores
  valor_total?: number;
  valor?: number;

  // Status
  status?: OrcamentoStatus;

  // Datas
  criado_em?: string;    // ex: "2025-01-10T12:34:56"
  created_at?: string;

  // Campos extras que o backend possa enviar
  [key: string]: unknown;
}
