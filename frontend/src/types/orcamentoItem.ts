// src/types/orcamentoItem.ts
// Tipos alinhados com os schemas do backend de itens de orçamento.

/**
 * Tipos de item suportados:
 * - "HH"       -> Hora-homem (vinculado a máquina / tipo de hora)
 * - "MATERIAL" -> Materiais de usinagem / insumos
 * - "LIVRE"    -> Item genérico com descrição e preço manual
 */
export type TipoItem = 'HH' | 'MATERIAL' | 'LIVRE';

/**
 * Tipos de hora-homem:
 * - REGULAR
 * - EXTRA
 * - FERIADO
 */
export type TipoHH = 'REGULAR' | 'EXTRA' | 'FERIADO';

export interface OrcamentoItemBase {
  item_tipo: TipoItem;

  // HH
  maquina_id?: number | null;
  tipo_hh?: TipoHH | null;

  // MATERIAL
  material_id?: number | null;

  // LIVRE / rótulo do item
  descricao?: string | null;

  // Unidade de medida (ex.: h, kg, un) via referência
  uom_id?: number | null;

  // Quantidade (padrão: 1)
  quantidade: number;

  // Preço unitário:
  // - obrigatório em SPOT para HH, MATERIAL e LIVRE
  // - em CONTRATO pode ser resolvido pelo backend
  preco_unitario?: number | null;
}

/**
 * Item completo retornado pelo backend
 * (equivalente ao OrcamentoItemOut no Pydantic).
 */
export interface OrcamentoItem extends OrcamentoItemBase {
  id: number;
  orcamento_id: number;
  total_item: number;
  created_at?: string | null;
  updated_at?: string | null;
}

/**
 * Payload para criação de item.
 * - orcamento_id vem na URL, não no corpo.
 * - total_item é calculado no backend.
 */
export interface OrcamentoItemCreateInput extends OrcamentoItemBase {
  // Em create, item_tipo é sempre obrigatório.
  item_tipo: TipoItem;
}
