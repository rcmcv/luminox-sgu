// src/pages/OrcamentoDetalhe.tsx
// Detalhe de um orçamento específico (/orcamentos/:id)

import React, { useEffect, useState } from 'react';
import { useNavigate, useParams, useLocation } from 'react-router-dom';
import { AppLayout } from '../components/layout/AppLayout';
import { fetchOrcamentoById } from '../api/orcamentos';
import { fetchOrcamentoItens } from '../api/orcamentoItens';
import type { Orcamento } from '../types/orcamento';
import type { OrcamentoItem } from '../types/orcamentoItem';

interface LocationState {
  clienteNome?: string;
}

export const OrcamentoDetalhe: React.FC = () => {
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();
  const location = useLocation();
  const state = location.state as LocationState | null;

  const [orcamento, setOrcamento] = useState<Orcamento | null>(null);
  const [loading, setLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);

  const [itens, setItens] = useState<OrcamentoItem[]>([]);
  const [loadingItens, setLoadingItens] = useState<boolean>(false);
  const [erroItens, setErroItens] = useState<string | null>(null);

  useEffect(() => {
    if (!id) {
      setError('ID de orçamento inválido.');
      setLoading(false);
      return;
    }

    const numericId = Number(id);
    if (Number.isNaN(numericId)) {
      setError('ID de orçamento inválido.');
      setLoading(false);
      return;
    }

    const carregar = async () => {
      try {
        setLoading(true);
        setError(null);
        const data = await fetchOrcamentoById(numericId);
        setOrcamento(data);
      } catch (err) {
        console.error('[Orçamentos] Erro ao carregar orçamento detalhado:', err);
        setError('Não foi possível carregar os dados do orçamento.');
      } finally {
        setLoading(false);
      }
    };

    carregar();
  }, [id]);

  // Carrega itens assim que tivermos o orçamento carregado com sucesso
  useEffect(() => {
    if (!orcamento) return;

    const carregarItens = async () => {
      try {
        setLoadingItens(true);
        setErroItens(null);
        const data = await fetchOrcamentoItens(orcamento.id);
        setItens(data);
      } catch (err) {
        // Em teoria não cai aqui, pois o client já trata erro retornando []
        console.error('[Orçamentos] Erro ao carregar itens do orçamento:', err);
        setErroItens('Não foi possível carregar os itens deste orçamento.');
      } finally {
        setLoadingItens(false);
      }
    };

    carregarItens();
  }, [orcamento]);

  const handleVoltar = () => {
    navigate('/orcamentos');
  };

  const formatCodigo = (orc: Orcamento): string => {
    if (orc.codigo) return orc.codigo;
    if (orc.numero) return orc.numero;
    return `#${orc.id}`;
  };

  const formatCliente = (orc: Orcamento | null): string => {
    // Se recebemos o nome via state (da lista), prioriza ele
    if (state?.clienteNome) {
      return state.clienteNome;
    }

    if (orc?.cliente_id) {
      return `Cliente #${orc.cliente_id}`;
    }
    return '—';
  };

  const formatValor = (valor: number | undefined): string => {
    const v = valor ?? 0;
    return `R$ ${v.toLocaleString('pt-BR', {
      minimumFractionDigits: 2,
      maximumFractionDigits: 2,
    })}`;
  };

  const formatData = (dateStr: string | undefined): string => {
    if (!dateStr) return '—';
    return dateStr.split('T')[0];
  };

  const formatStatus = (orc: Orcamento | null): string => {
    if (!orc?.status) return 'N/D';
    return orc.status.toUpperCase();
  };

  const getStatusClasses = (status: string): string => {
    if (status === 'RASCUNHO') {
      return 'bg-slate-100 text-slate-700';
    }
    if (status === 'ENVIADO') {
      return 'bg-sky-100 text-sky-700';
    }
    if (status === 'ACEITO') {
      return 'bg-emerald-100 text-emerald-700';
    }
    if (status === 'CANCELADO') {
      return 'bg-rose-100 text-rose-700';
    }
    return 'bg-slate-100 text-slate-700';
  };

  const pageTitle = orcamento
    ? `Orçamento ${formatCodigo(orcamento)}`
    : 'Detalhes do orçamento';

  const formatDescricaoItem = (item: OrcamentoItem): string => {
    return (
      item.descricao ||
      item.detalhamento ||
      `Item #${item.id}`
    );
  };

  const formatQuantidade = (item: OrcamentoItem): string => {
    const qtd = item.quantidade ?? 0;
    const unidade = item.unidade ?? '';
    if (!unidade) {
      return qtd.toLocaleString('pt-BR', {
        minimumFractionDigits: 2,
        maximumFractionDigits: 2,
      });
    }
    return `${qtd.toLocaleString('pt-BR', {
      minimumFractionDigits: 2,
      maximumFractionDigits: 2,
    })} ${unidade}`;
  };

  const formatValorUnitario = (item: OrcamentoItem): string => {
    const v = item.valor_unitario ?? item.preco_unitario ?? 0;
    return formatValor(v);
  };

  const formatTotalItem = (item: OrcamentoItem): string => {
    const v = item.total ?? item.subtotal ?? 0;
    return formatValor(v);
  };

  return (
    <AppLayout title={pageTitle}>
      <div className="space-y-4">
        <div className="flex items-center justify-between">
          <button
            onClick={handleVoltar}
            className="inline-flex items-center gap-2 text-xs font-semibold text-slate-600 hover:text-slate-800"
          >
            <span className="inline-block h-2 w-2 -rotate-45 border-l-2 border-b-2 border-slate-600" />
            Voltar para a lista
          </button>
        </div>

        {loading && (
          <div className="rounded-md border border-slate-200 bg-slate-50 px-4 py-3 text-sm text-slate-600">
            Carregando dados do orçamento...
          </div>
        )}

        {error && !loading && (
          <div className="rounded-md border border-red-200 bg-red-50 px-4 py-3 text-sm text-red-700">
            {error}
          </div>
        )}

        {!loading && !error && orcamento && (
          <>
            {/* Card principal com resumo */}
            <div className="rounded-xl bg-white p-6 shadow-md">
              <div className="mb-4 flex flex-col gap-3 sm:flex-row sm:items-start sm:justify-between">
                <div>
                  <h3 className="text-lg font-semibold text-slate-800">
                    {formatCodigo(orcamento)}
                  </h3>
                  <p className="text-sm text-slate-600">
                    {orcamento.titulo || 'Orçamento sem título'}
                  </p>
                  <p className="mt-2 text-xs text-slate-500">
                    Cliente:{' '}
                    <span className="font-medium text-slate-700">
                      {formatCliente(orcamento)}
                    </span>
                  </p>
                </div>

                <div className="text-right text-sm">
                  <p className="text-xs text-slate-500">Status</p>
                  <span
                    className={[
                      'inline-flex rounded-full px-3 py-1 text-xs font-semibold',
                      getStatusClasses(formatStatus(orcamento)),
                    ].join(' ')}
                  >
                    {formatStatus(orcamento)}
                  </span>
                  <p className="mt-2 text-xs text-slate-500">
                    Tipo:{' '}
                    <span className="font-medium text-slate-700">
                      {orcamento.tipo}
                    </span>
                  </p>
                  <p className="mt-1 text-xs text-slate-500">
                    Moeda:{' '}
                    <span className="font-medium text-slate-700">
                      {orcamento.moeda}
                    </span>
                  </p>
                </div>
              </div>

              <div className="grid gap-4 rounded-lg border border-slate-100 bg-slate-50 p-4 text-sm sm:grid-cols-2 lg:grid-cols-4">
                <div>
                  <p className="text-xs uppercase tracking-wide text-slate-500">
                    Subtotal
                  </p>
                  <p className="text-base font-semibold text-slate-800">
                    {formatValor(orcamento.subtotal)}
                  </p>
                </div>
                <div>
                  <p className="text-xs uppercase tracking-wide text-slate-500">
                    Desconto
                  </p>
                  <p className="text-base font-semibold text-slate-800">
                    {formatValor(orcamento.desconto)}
                  </p>
                </div>
                <div>
                  <p className="text-xs uppercase tracking-wide text-slate-500">
                    Acréscimo
                  </p>
                  <p className="text-base font-semibold text-slate-800">
                    {formatValor(orcamento.acrescimo)}
                  </p>
                </div>
                <div>
                  <p className="text-xs uppercase tracking-wide text-slate-500">
                    Total
                  </p>
                  <p className="text-base font-semibold text-primary-700">
                    {formatValor(orcamento.total)}
                  </p>
                </div>
              </div>

              <div className="mt-4 grid gap-4 text-xs text-slate-500 sm:grid-cols-2">
                <p>
                  Criado em:{' '}
                  <span className="font-medium text-slate-700">
                    {formatData(orcamento.created_at)}
                  </span>
                </p>
                <p>
                  Atualizado em:{' '}
                  <span className="font-medium text-slate-700">
                    {formatData(orcamento.updated_at)}
                  </span>
                </p>
              </div>

              {orcamento.observacoes && (
                <div className="mt-4 rounded-md border border-slate-100 bg-slate-50 p-3 text-xs text-slate-700">
                  <p className="mb-1 font-semibold text-slate-800">
                    Observações
                  </p>
                  <p className="whitespace-pre-line">
                    {orcamento.observacoes}
                  </p>
                </div>
              )}
            </div>

            {/* Itens do orçamento */}
            <div className="rounded-xl bg-white p-6 shadow-md">
              <div className="mb-3 flex items-center justify-between">
                <p className="text-sm font-semibold text-slate-800">
                  Itens do orçamento
                </p>
              </div>

              {loadingItens && (
                <p className="mb-2 text-xs text-slate-500">
                  Carregando itens...
                </p>
              )}

              {erroItens && (
                <div className="mb-2 rounded-md border border-amber-200 bg-amber-50 px-3 py-2 text-xs text-amber-700">
                  {erroItens}
                </div>
              )}

              <div className="overflow-x-auto">
                <table className="min-w-full border-collapse text-xs sm:text-sm">
                  <thead>
                    <tr className="bg-slate-50">
                      <th className="border-b border-slate-200 px-3 py-2 text-left font-semibold text-slate-700">
                        Descrição
                      </th>
                      <th className="border-b border-slate-200 px-3 py-2 text-right font-semibold text-slate-700">
                        Quantidade
                      </th>
                      <th className="border-b border-slate-200 px-3 py-2 text-right font-semibold text-slate-700">
                        Valor unitário
                      </th>
                      <th className="border-b border-slate-200 px-3 py-2 text-right font-semibold text-slate-700">
                        Total
                      </th>
                    </tr>
                  </thead>
                  <tbody>
                    {itens.map((item) => (
                      <tr
                        key={item.id}
                        className="hover:bg-slate-50"
                      >
                        <td className="border-b border-slate-100 px-3 py-2 align-middle">
                          <span className="text-slate-800">
                            {formatDescricaoItem(item)}
                          </span>
                        </td>
                        <td className="border-b border-slate-100 px-3 py-2 text-right align-middle">
                          {formatQuantidade(item)}
                        </td>
                        <td className="border-b border-slate-100 px-3 py-2 text-right align-middle">
                          {formatValorUnitario(item)}
                        </td>
                        <td className="border-b border-slate-100 px-3 py-2 text-right align-middle">
                          {formatTotalItem(item)}
                        </td>
                      </tr>
                    ))}

                    {!loadingItens && itens.length === 0 && (
                      <tr>
                        <td
                          colSpan={4}
                          className="px-3 py-4 text-center text-xs text-slate-500"
                        >
                          Nenhum item encontrado para este orçamento.
                        </td>
                      </tr>
                    )}
                  </tbody>
                </table>
              </div>
            </div>
          </>
        )}
      </div>
    </AppLayout>
  );
};
