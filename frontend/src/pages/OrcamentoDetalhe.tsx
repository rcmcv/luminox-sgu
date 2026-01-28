// src/pages/OrcamentoDetalhe.tsx
import React, { useEffect, useState } from 'react';
import { useLocation, useNavigate, useParams } from 'react-router-dom';
import { AppLayout } from '../components/layout/AppLayout';
import { useAuth } from '../auth/useAuth';
import { fetchOrcamentoById } from '../api/orcamentos';
import { fetchOrcamentoItens } from '../api/orcamentoItens';
import type { Orcamento } from '../types/orcamento';
import type { OrcamentoItem } from '../types/orcamentoItem';

interface LocationState {
  clienteNome?: string;
}

export const OrcamentoDetalhe: React.FC = () => {
  const { id } = useParams();
  const navigate = useNavigate();
  const location = useLocation();
  const { user } = useAuth();

  const locationState = (location.state || {}) as LocationState;
  const clienteNomeFromState = locationState.clienteNome;

  const [orcamento, setOrcamento] = useState<Orcamento | null>(null);
  const [loadingOrcamento, setLoadingOrcamento] = useState<boolean>(true);
  const [orcamentoError, setOrcamentoError] = useState<string | null>(null);

  const [itens, setItens] = useState<OrcamentoItem[]>([]);
  const [loadingItens, setLoadingItens] = useState<boolean>(false);
  const [itensError, setItensError] = useState<string | null>(null);

  useEffect(() => {
    if (!id) {
      setOrcamentoError('ID de orçamento inválido.');
      setLoadingOrcamento(false);
      return;
    }

    let canceled = false;

    const carregarDados = async () => {
      try {
        setLoadingOrcamento(true);
        setOrcamentoError(null);

        const orcamentoId = Number(id);
        if (Number.isNaN(orcamentoId)) {
          throw new Error('ID de orçamento inválido.');
        }

        // 1) Carrega o orçamento
        const data = await fetchOrcamentoById(orcamentoId);
        if (!canceled) {
          setOrcamento(data);
        }

        // 2) Carrega itens em um try/catch separado
        setLoadingItens(true);
        setItensError(null);

        try {
          const itensData = await fetchOrcamentoItens(orcamentoId);
          if (!canceled) {
            setItens(itensData);
          }
        } catch (err) {
          console.error(
            '[Orçamentos] Erro ao carregar itens do orçamento:',
            err,
          );
          if (!canceled) {
            setItensError('Não foi possível carregar os itens deste orçamento.');
          }
        }
      } catch (error) {
        console.error('[Orçamentos] Erro ao carregar orçamento/detalhes:', error);
        if (!canceled) {
          setOrcamentoError('Não foi possível carregar o orçamento.');
        }
      } finally {
        if (!canceled) {
          setLoadingOrcamento(false);
          setLoadingItens(false);
        }
      }
    };

    carregarDados();

    return () => {
      canceled = true;
    };
  }, [id]);

  const handleVoltar = () => {
    navigate('/orcamentos');
  };

  const formatCurrency = (value: number, moeda?: string | null) => {
    const currency = moeda || 'BRL';
    try {
      return value.toLocaleString('pt-BR', {
        style: 'currency',
        currency,
      });
    } catch {
      return value.toFixed(2);
    }
  };

  const clienteLabel =
    clienteNomeFromState ||
    (orcamento?.cliente_id ? `Cliente #${orcamento.cliente_id}` : 'Cliente N/D');

  return (
    <AppLayout title="Detalhes do orçamento">
      <div className="flex flex-col gap-4 p-4 md:p-6">
        {/* Cabeçalho */}
        <div className="flex flex-col justify-between gap-3 sm:flex-row sm:items-center">
          <div>
            <h1 className="text-xl font-semibold text-slate-900">
              Orçamento #{id}
            </h1>
            <p className="text-sm text-slate-500">
              {clienteLabel}
              {user?.role ? ` • Papel: ${user.role}` : ''}
            </p>
          </div>

          <div className="flex flex-wrap items-center gap-2">
            <button
              type="button"
              onClick={handleVoltar}
              className="inline-flex items-center rounded-md border border-slate-300 px-3 py-1.5 text-xs font-semibold text-slate-700 shadow-sm hover:bg-slate-50"
            >
              Voltar
            </button>
          </div>
        </div>

        {/* Corpo */}
        {loadingOrcamento ? (
          <div className="rounded-lg border border-slate-200 bg-white p-4 text-sm text-slate-600 shadow-sm">
            Carregando orçamento...
          </div>
        ) : orcamentoError || !orcamento ? (
          <div className="rounded-lg border border-red-200 bg-red-50 p-4 text-sm text-red-700 shadow-sm">
            {orcamentoError ?? 'Orçamento não encontrado.'}
          </div>
        ) : (
          <>
            {/* Linha de cards: dados + totais */}
            <div className="grid gap-4 md:grid-cols-2">
              {/* Dados gerais */}
              <div className="rounded-lg border border-slate-200 bg-white p-4 shadow-sm">
                <h2 className="mb-3 text-sm font-semibold text-slate-800">
                  Dados do orçamento
                </h2>
                <dl className="space-y-1 text-sm text-slate-700">
                  <div className="flex justify-between gap-2">
                    <dt className="text-slate-500">Cliente</dt>
                    <dd className="font-medium text-right">{clienteLabel}</dd>
                  </div>

                  <div className="flex justify-between gap-2">
                    <dt className="text-slate-500">Tipo</dt>
                    <dd className="font-medium text-right">{orcamento.tipo}</dd>
                  </div>

                  <div className="flex justify-between gap-2">
                    <dt className="text-slate-500">Status</dt>
                    <dd className="font-medium text-right">{orcamento.status}</dd>
                  </div>

                  <div className="flex justify-between gap-2">
                    <dt className="text-slate-500">Moeda</dt>
                    <dd className="font-medium text-right">{orcamento.moeda}</dd>
                  </div>

                  {orcamento.titulo && (
                    <div className="mt-2">
                      <dt className="text-slate-500">Título</dt>
                      <dd className="font-medium text-slate-800">
                        {orcamento.titulo}
                      </dd>
                    </div>
                  )}

                  {orcamento.observacoes && (
                    <div className="mt-2">
                      <dt className="text-slate-500">Observações</dt>
                      <dd className="whitespace-pre-line text-slate-700">
                        {orcamento.observacoes}
                      </dd>
                    </div>
                  )}
                </dl>
              </div>

              {/* Totais */}
              <div className="rounded-lg border border-slate-200 bg-white p-4 shadow-sm">
                <h2 className="mb-3 text-sm font-semibold text-slate-800">
                  Totais
                </h2>
                <dl className="space-y-1 text-sm text-slate-700">
                  <div className="flex justify-between gap-2">
                    <dt className="text-slate-500">Subtotal</dt>
                    <dd className="font-medium">
                      {formatCurrency(orcamento.subtotal, orcamento.moeda)}
                    </dd>
                  </div>

                  <div className="flex justify-between gap-2">
                    <dt className="text-slate-500">Desconto</dt>
                    <dd className="font-medium">
                      {formatCurrency(orcamento.desconto, orcamento.moeda)}
                    </dd>
                  </div>

                  <div className="flex justify-between gap-2">
                    <dt className="text-slate-500">Acréscimo</dt>
                    <dd className="font-medium">
                      {formatCurrency(orcamento.acrescimo, orcamento.moeda)}
                    </dd>
                  </div>

                  <div className="mt-2 flex justify-between gap-2 border-t border-slate-200 pt-2 text-base">
                    <dt className="font-semibold text-slate-700">Total</dt>
                    <dd className="font-semibold text-emerald-700">
                      {formatCurrency(orcamento.total, orcamento.moeda)}
                    </dd>
                  </div>
                </dl>
              </div>
            </div>

            {/* Itens do orçamento */}
            <div className="mt-4 rounded-lg border border-slate-200 bg-white p-4 shadow-sm">
              <div className="mb-3 flex items-center justify-between gap-2">
                <h2 className="text-sm font-semibold text-slate-800">
                  Itens do orçamento
                </h2>

                {/* Próximo passo: habilitar este botão pra abrir formulário de novo item */}
                <button
                  type="button"
                  className="inline-flex items-center rounded-md bg-primary-600 px-3 py-1.5 text-xs font-semibold text-white shadow-sm transition hover:bg-primary-700 disabled:opacity-50"
                  disabled
                  title="No próximo passo vamos habilitar a inclusão de itens"
                >
                  + Novo item (em breve)
                </button>
              </div>

              {loadingItens ? (
                <p className="text-sm text-slate-600">
                  Carregando itens do orçamento...
                </p>
              ) : itensError ? (
                <p className="text-sm text-red-700">
                  {itensError}
                </p>
              ) : itens.length === 0 ? (
                <p className="text-sm text-slate-500">
                  Nenhum item cadastrado para este orçamento.
                </p>
              ) : (
                <div className="overflow-x-auto">
                  <table className="min-w-full text-left text-sm">
                    <thead>
                      <tr className="border-b border-slate-200 bg-slate-50 text-xs uppercase tracking-wide text-slate-500">
                        <th className="px-3 py-2">Descrição</th>
                        <th className="px-3 py-2 text-right">Qtd</th>
                        <th className="px-3 py-2">Tipo</th>
                        <th className="px-3 py-2">U.M.</th>
                        <th className="px-3 py-2 text-right">
                          Preço unitário
                        </th>
                        <th className="px-3 py-2 text-right">Total</th>
                      </tr>
                    </thead>
                    <tbody>
                      {itens.map((item) => (
                        <tr
                          key={item.id}
                          className="border-b border-slate-100 hover:bg-slate-50"
                        >
                          <td className="px-3 py-2 text-slate-800">
                            {item.descricao ||
                              (item.item_tipo === 'HH'
                                ? 'Hora-homem'
                                : item.item_tipo === 'MATERIAL'
                                ? 'Material'
                                : 'Item')}
                          </td>
                          <td className="px-3 py-2 text-right text-slate-700">
                            {item.quantidade}
                          </td>
                          <td className="px-3 py-2 text-slate-700">
                            {item.item_tipo}
                          </td>
                          <td className="px-3 py-2 text-slate-700">
                            {item.uom_id ?? '-'}
                          </td>
                          <td className="px-3 py-2 text-right text-slate-700">
                            {item.preco_unitario != null
                              ? formatCurrency(
                                  item.preco_unitario,
                                  orcamento.moeda,
                                )
                              : '-'}
                          </td>
                          <td className="px-3 py-2 text-right font-medium text-slate-900">
                            {formatCurrency(item.total_item, orcamento.moeda)}
                          </td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              )}
            </div>
          </>
        )}
      </div>
    </AppLayout>
  );
};
