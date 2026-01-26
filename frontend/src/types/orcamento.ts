// src/types/orcamento.ts
// Tipos relacionados a Orçamentos, alinhados com OrcamentoOut do backend.
//
// Campos do backend (OrcamentoOut):
// - id, cliente_id, tipo, status, contrato_id, moeda, titulo, observacoes,
//   subtotal, desconto, acrescimo, total, created_at, updated_at
//
// Adicionamos campos opcionais "codigo" e "numero" pensando em evoluções futuras.

export type OrcamentoTipo = 'CONTRATO' | 'SPOT' | string;
export type OrcamentoStatus =
  | 'RASCUNHO'
  | 'ENVIADO'
  | 'ACEITO'
  | 'CANCELADO'
  | string;

export interface Orcamento {
  id: number;

  // Identificadores
  codigo?: string | null;
  numero?: string | null;

  // Relacionamento
  cliente_id: number;

  // Metadados
  tipo: OrcamentoTipo;
  status: OrcamentoStatus;
  contrato_id?: number | null;

  moeda: string;
  titulo?: string | null;
  observacoes?: string | null;

  // Totais
  subtotal: number;
  desconto: number;
  acrescimo: number;
  total: number;

  // Datas
  created_at: string;
  updated_at: string;

  // Campos extras que o backend possa enviar no futuro
  [key: string]: unknown;
}
