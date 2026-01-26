// src/types/orcamentoItem.ts
// Tipos relacionados aos itens de um orçamento.
// Flexível o suficiente para se adaptar ao backend.

export interface OrcamentoItem {
  id: number;
  orcamento_id: number;

  // Descrição do item/serviço/peça
  descricao?: string | null;
  detalhamento?: string | null;

  // Quantidade e unidade
  quantidade?: number;
  unidade?: string | null;

  // Valores
  valor_unitario?: number;
  preco_unitario?: number;
  total?: number;
  subtotal?: number;

  // Datas
  created_at?: string;
  updated_at?: string;

  // Campos extras que possam existir no backend
  [key: string]: unknown;
}
