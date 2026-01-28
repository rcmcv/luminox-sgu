// src/pages/OrcamentoDetalhe.tsx
import React, { useEffect, useState, type FormEvent } from 'react';
import { useLocation, useNavigate, useParams } from 'react-router-dom';
import { AppLayout } from '../components/layout/AppLayout';
import { useAuth } from '../auth/useAuth';
import { fetchOrcamentoById } from '../api/orcamentos';
import { fetchOrcamentoItens, createOrcamentoItem } from '../api/orcamentoItens';
import type { Orcamento } from '../types/orcamento';
import type { OrcamentoItem, OrcamentoItemCreateInput } from '../types/orcamentoItem';

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

  // Estados para novo item (tipo LIVRE)
  const [mostrarFormNovoItem, setMostrarFormNovoItem] = useState(false);
  const [novoItemDescricao, setNovoItemDescricao] = useState('');
  const [novoItemQuantidade, setNovoItemQuantidade] = useState('1');
  const [novoItemPrecoUnitario, setNovoItemPrecoUnitario] = useState('');
  const [novoItemLoading, setNovoItemLoading] = useState(false);
  const [novoItemError, setNovoItemError] = useState<string | null>(null);

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

  const handleToggleNovoItem = () => {
    setNovoItemError(null);
    setMostrarFormNovoItem((prev) => !prev);
  };

  const handleCancelarNovoItem = () => {
    setNovoItemError(null);
    setMostrarFormNovoItem(false);
    setNovoItemDescricao('');
    setNovoItemQuantidade('1');
    setNovoItemPrecoUnitario('');
  };

  const handleSubmitNovoItem = async (event: FormEvent<HTMLFormElement>) => {
    event.preventDefault();
    setNovoItemError(null);

    if (!orcamento || !id) {
      setNovoItemError('Orçamento inválido.');
      return;
    }

    // Validações simples
    if (!novoItemDescricao.trim()) {
      setNovoItemError('Informe a descrição do item.');
      return;
    }

    const quantidadeNum = Number(novoItemQuantidade.replace(',', '.'));
    if (!Number.isFinite(quantidadeNum) || quantidadeNum <= 0) {
      setNovoItemError('Informe uma quantidade válida (maior que zero).');
      return;
    }

    const precoNum = Number(novoItemPrecoUnitario.replace(',', '.'));
    if (!Number.isFinite(precoNum) || precoNum < 0) {
      setNovoItemError('Informe um preço unitário válido (zero ou maior).');
      return;
    }

    const payload: OrcamentoItemCreateInput = {
      item_tipo: 'LIVRE',
      descricao: novoItemDescricao.trim(),
      quantidade: quantidadeNum,
      preco_unitario: precoNum,
      // Demais campos permanecem nulos/undefined:
      // maquina_id, tipo_hh, material_id, uom_id...
    };

    try {
      setNovoItemLoading(true);

      const orcamentoId = Number(id);

      // Cria o item
      await createOrcamentoItem(orcamentoId, payload);

      // Recarrega itens e orçamento para atualizar total
      const [novoOrcamento, novosItens] = await Promise.all([
        fetchOrcamentoById(orcamentoId),
        fetchOrcamentoItens(orcamentoId),
      ]);

      setOrcamento(novoOrcamento);
      setItens(novosItens);

      // Limpa e fecha o formulário
      setNovoItemDescricao('');
      setNovoItemQuantidade('1');
      setNovoItemPrecoUnitario('');
      setMostrarFormNovoItem(false);
    } catch (error: any) {
      console.error('[Orçamentos] Erro ao criar item de orçamento:', error);

      const detail =
        error?.response?.data?.detail ||
        error?.response?.data?.message ||
        null;

      if (typeof detail === 'string') {
        setNovoItemError(detail);
      } else {
        setNovoItemError(
          'Não foi possível adicionar o item. Verifique os dados e tente novamente.',
        );
      }
    } finally {
      setNovoItemLoading(false);
    }
  };

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
                    <dd className="font-medium text-right">
                      {orcamento.status}
                    </dd>
                  </div>

                  <div className="flex justify-between gap-2">
                    <dt className="text-slate-500">Moeda</dt>
                    <dd className="font-medium text-right">
                      {orcamento.moeda}
                    </dd>
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
              <div className="mb-3 flex flex-col gap-2 sm:flex-row sm:items-center sm:justify-between">
                <h2 className="text-sm font-semibold text-slate-800">
                  Itens do orçamento
                </h2>

                <button
                  type="button"
                  onClick={handleToggleNovoItem}
                  className="inline-flex items-center justify-center rounded-md bg-primary-600 px-3 py-1.5 text-xs font-semibold text-white shadow-sm transition hover:bg-primary-700"
                >
                  {mostrarFormNovoItem ? 'Cancelar' : '+ Novo item'}
                </button>
              </div>

              {/* Formulário de novo item (tipo LIVRE) */}
              {mostrarFormNovoItem && (
                <form
                  onSubmit={handleSubmitNovoItem}
                  className="mb-4 rounded-md border border-slate-200 bg-slate-50 p-3 text-sm"
                >
                  <p className="mb-2 text-xs font-semibold uppercase tracking-wide text-slate-500">
                    Novo item (tipo LIVRE)
                  </p>

                  {novoItemError && (
                    <div className="mb-2 rounded-md border border-red-200 bg-red-50 px-3 py-1.5 text-xs text-red-700">
                      {novoItemError}
                    </div>
                  )}

                  <div className="grid gap-3 sm:grid-cols-3">
                    <div className="sm:col-span-2">
                      <label className="mb-1 block text-xs font-medium text-slate-600">
                        Descrição
                      </label>
                      <input
                        type="text"
                        value={novoItemDescricao}
                        onChange={(e) => setNovoItemDescricao(e.target.value)}
                        className="w-full rounded-md border border-slate-300 px-2 py-1.5 text-sm text-slate-800 shadow-sm outline-none focus:border-primary-500 focus:ring-1 focus:ring-primary-500"
                        placeholder="Ex.: Usinagem de eixo Ø50 x 300mm"
                      />
                    </div>

                    <div>
                      <label className="mb-1 block text-xs font-medium text-slate-600">
                        Quantidade
                      </label>
                      <input
                        type="number"
                        min={0}
                        step={0.01}
                        value={novoItemQuantidade}
                        onChange={(e) => setNovoItemQuantidade(e.target.value)}
                        className="w-full rounded-md border border-slate-300 px-2 py-1.5 text-sm text-slate-800 shadow-sm outline-none focus:border-primary-500 focus:ring-1 focus:ring-primary-500"
                      />
                    </div>
                  </div>

                  <div className="mt-3 grid gap-3 sm:grid-cols-3">
                    <div>
                      <label className="mb-1 block text-xs font-medium text-slate-600">
                        Preço unitário
                      </label>
                      <input
                        type="number"
                        min={0}
                        step={0.01}
                        value={novoItemPrecoUnitario}
                        onChange={(e) =>
                          setNovoItemPrecoUnitario(e.target.value)
                        }
                        className="w-full rounded-md border border-slate-300 px-2 py-1.5 text-sm text-slate-800 shadow-sm outline-none focus:border-primary-500 focus:ring-1 focus:ring-primary-500"
                      />
                    </div>
                  </div>

                  <div className="mt-3 flex flex-col gap-2 sm:flex-row sm:justify-end">
                    <button
                      type="button"
                      onClick={handleCancelarNovoItem}
                      className="inline-flex items-center justify-center rounded-md border border-slate-300 px-3 py-1.5 text-xs font-semibold text-slate-700 shadow-sm hover:bg-slate-100"
                      disabled={novoItemLoading}
                    >
                      Cancelar
                    </button>
                    <button
                      type="submit"
                      className="inline-flex items-center justify-center rounded-md bg-emerald-600 px-3 py-1.5 text-xs font-semibold text-white shadow-sm hover:bg-emerald-700 disabled:opacity-60"
                      disabled={novoItemLoading}
                    >
                      {novoItemLoading ? 'Salvando...' : 'Adicionar item'}
                    </button>
                  </div>
                </form>
              )}

              {/* Lista de itens */}
              {loadingItens ? (
                <p className="text-sm text-slate-600">
                  Carregando itens do orçamento...
                </p>
              ) : itensError ? (
                <p className="text-sm text-red-700">{itensError}</p>
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
