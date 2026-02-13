// src/pages/OrcamentoDetalhe.tsx
import React, { useEffect, useState, type FormEvent } from 'react';
import { useLocation, useNavigate, useParams } from 'react-router-dom';
import { AppLayout } from '../components/layout/AppLayout';
import { useAuth } from '../auth/useAuth';
import { fetchOrcamentoById } from '../api/orcamentos';
import {
  fetchOrcamentoItens,
  createOrcamentoItem,
  deleteOrcamentoItem,
  updateOrcamentoItem,
} from '../api/orcamentoItens';
import client from '../api/client';
import type { Orcamento } from '../types/orcamento';
import type {
  OrcamentoItem,
  OrcamentoItemCreateInput,
} from '../types/orcamentoItem';

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

  // ✅ Download PDF
  const [pdfLoading, setPdfLoading] = useState(false);
  const [pdfError, setPdfError] = useState<string | null>(null);

  // Fluxo de inclusão em lote (itens LIVRE)
  const [mostrarFormNovoItem, setMostrarFormNovoItem] = useState(false);
  const [novoItemDescricao, setNovoItemDescricao] = useState('');
  const [novoItemQuantidade, setNovoItemQuantidade] = useState('1');
  const [novoItemPrecoUnitario, setNovoItemPrecoUnitario] = useState('');
  const [novoItemError, setNovoItemError] = useState<string | null>(null);
  const [novoItemLoading, setNovoItemLoading] = useState(false);
  const [novosItens, setNovosItens] = useState<OrcamentoItemCreateInput[]>([]);

  // Exclusão de item já salvo
  const [deleteError, setDeleteError] = useState<string | null>(null);
  const [deleteLoadingId, setDeleteLoadingId] = useState<number | null>(null);

  // Edição de item LIVRE já salvo
  const [editItemId, setEditItemId] = useState<number | null>(null);
  const [editDescricao, setEditDescricao] = useState('');
  const [editQuantidade, setEditQuantidade] = useState('');
  const [editPrecoUnitario, setEditPrecoUnitario] = useState('');
  const [editError, setEditError] = useState<string | null>(null);
  const [editLoadingId, setEditLoadingId] = useState<number | null>(null);

  // Helper para traduzir mensagens técnicas do backend em algo amigável
  const mapPermissionMessage = (detail: unknown, fallback: string): string => {
    if (typeof detail === 'string') {
      if (detail === 'Not enough permissions') {
        return 'Você não tem permissão para realizar esta ação.';
      }
      return detail;
    }
    return fallback;
  };

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
        setDeleteError(null);
        setEditError(null);
        setPdfError(null);

        const orcamentoId = Number(id);
        if (Number.isNaN(orcamentoId)) {
          throw new Error('ID de orçamento inválido.');
        }

        // 1) Carrega o orçamento
        const data = await fetchOrcamentoById(orcamentoId);
        if (!canceled) {
          setOrcamento(data);
        }

        // 2) Carrega itens
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

  // ✅ Extrai filename do Content-Disposition (se existir)
  const getFilenameFromContentDisposition = (value?: string | null) => {
    if (!value) return null;

    // Ex.: attachment; filename="orcamento_1.pdf"
    const match = /filename\*?=(?:UTF-8''|")?([^\";]+)"?/i.exec(value);
    if (!match?.[1]) return null;

    try {
      return decodeURIComponent(match[1]);
    } catch {
      return match[1];
    }
  };

  // ✅ Baixar PDF do orçamento
  const handleBaixarPdf = async () => {
    setPdfError(null);

    if (!id) {
      setPdfError('ID de orçamento inválido.');
      return;
    }

    try {
      setPdfLoading(true);

      const orcamentoId = Number(id);
      if (Number.isNaN(orcamentoId)) {
        setPdfError('ID de orçamento inválido.');
        return;
      }

      const response = await client.get(`/api/v1/orcamentos/${orcamentoId}/pdf`, {
        responseType: 'blob',
      });

      const contentDisposition =
        (response.headers?.['content-disposition'] as string | undefined) ?? null;

      const filenameFromHeader =
        getFilenameFromContentDisposition(contentDisposition);

      const filename = filenameFromHeader || `orcamento_${orcamentoId}.pdf`;

      const blob = new Blob([response.data], { type: 'application/pdf' });
      const url = window.URL.createObjectURL(blob);

      const a = document.createElement('a');
      a.href = url;
      a.download = filename;
      document.body.appendChild(a);
      a.click();
      a.remove();

      window.URL.revokeObjectURL(url);
    } catch (error: any) {
      console.error('[Orçamentos] Erro ao baixar PDF:', error);

      // Quando usamos responseType: "blob", erros do backend podem vir como Blob
      let detail: string | null = null;

      const resp = error?.response;

      try {
        if (resp?.data instanceof Blob) {
          const text = await resp.data.text();
          // tenta JSON -> pega detail/message
          try {
            const json = JSON.parse(text);
            detail = json?.detail || json?.message || text;
          } catch {
            // se não for JSON, usa o texto bruto
            detail = text || null;
          }
        } else {
          detail = resp?.data?.detail || resp?.data?.message || null;
        }
      } catch {
        // se der qualquer erro ao ler/parsing, segue para fallback
        detail = null;
      }

      const message = mapPermissionMessage(
        detail,
        'Não foi possível baixar o PDF agora. Tente novamente em instantes.',
      );

      setPdfError(message);
    } finally {
      setPdfLoading(false);
    }
  };

  // --------- Inclusão em lote de itens LIVRE ---------

  const handleToggleNovoItem = () => {
    setNovoItemError(null);
    setMostrarFormNovoItem((prev) => !prev);
  };

  const handleCancelarNovoItem = () => {
    setNovoItemError(null);
    setNovoItemDescricao('');
    setNovoItemQuantidade('1');
    setNovoItemPrecoUnitario('');
    setNovosItens([]);
    setMostrarFormNovoItem(false);
  };

  const handleAdicionarItem = (event: FormEvent<HTMLFormElement>) => {
    event.preventDefault();
    setNovoItemError(null);

    if (!orcamento || !id) {
      setNovoItemError('Orçamento inválido.');
      return;
    }

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

    const novo: OrcamentoItemCreateInput = {
      item_tipo: 'LIVRE',
      descricao: novoItemDescricao.trim(),
      quantidade: quantidadeNum,
      preco_unitario: precoNum,
    };

    setNovosItens((prev) => [...prev, novo]);

    setNovoItemDescricao('');
    setNovoItemQuantidade('1');
    setNovoItemPrecoUnitario('');
  };

  const handleSalvarItens = async () => {
    setNovoItemError(null);

    if (!orcamento || !id) {
      setNovoItemError('Orçamento inválido.');
      return;
    }

    if (novosItens.length === 0) {
      setNovoItemError('Adicione pelo menos um item antes de salvar.');
      return;
    }

    try {
      setNovoItemLoading(true);

      const orcamentoId = Number(id);

      for (const item of novosItens) {
        await createOrcamentoItem(orcamentoId, item);
      }

      const [novoOrcamento, itensAtualizados] = await Promise.all([
        fetchOrcamentoById(orcamentoId),
        fetchOrcamentoItens(orcamentoId),
      ]);

      setOrcamento(novoOrcamento);
      setItens(itensAtualizados);

      setNovosItens([]);
      setNovoItemDescricao('');
      setNovoItemQuantidade('1');
      setNovoItemPrecoUnitario('');
      setMostrarFormNovoItem(false);
    } catch (error: any) {
      console.error('[Orçamentos] Erro ao salvar itens do orçamento:', error);

      const detail =
        error?.response?.data?.detail ||
        error?.response?.data?.message ||
        null;

      const message = mapPermissionMessage(
        detail,
        'Não foi possível salvar os itens. Verifique os dados e tente novamente.',
      );
      setNovoItemError(message);
    } finally {
      setNovoItemLoading(false);
    }
  };

  // --------- Exclusão de item salvo ---------

  const handleExcluirItem = async (itemId: number) => {
    setDeleteError(null);

    if (!orcamento || !id) {
      setDeleteError('Orçamento inválido.');
      return;
    }

    const confirmado = window.confirm(
      'Tem certeza que deseja excluir este item do orçamento?',
    );
    if (!confirmado) {
      return;
    }

    try {
      setDeleteLoadingId(itemId);

      const orcamentoId = Number(id);

      await deleteOrcamentoItem(orcamentoId, itemId);

      const [novoOrcamento, itensAtualizados] = await Promise.all([
        fetchOrcamentoById(orcamentoId),
        fetchOrcamentoItens(orcamentoId),
      ]);

      setOrcamento(novoOrcamento);
      setItens(itensAtualizados);
    } catch (error: any) {
      console.error('[Orçamentos] Erro ao excluir item do orçamento:', error);

      const detail =
        error?.response?.data?.detail ||
        error?.response?.data?.message ||
        null;

      const message = mapPermissionMessage(
        detail,
        'Não foi possível excluir o item. Tente novamente em instantes.',
      );
      setDeleteError(message);
    } finally {
      setDeleteLoadingId(null);
    }
  };

  // --------- Edição de item LIVRE salvo ---------

  const iniciarEdicaoItem = (item: OrcamentoItem) => {
    setEditError(null);
    setEditItemId(item.id);
    setEditDescricao(item.descricao ?? '');
    setEditQuantidade(String(item.quantidade ?? 1));
    setEditPrecoUnitario(
      item.preco_unitario != null ? String(item.preco_unitario) : '',
    );
  };

  const cancelarEdicaoItem = () => {
    setEditError(null);
    setEditItemId(null);
    setEditDescricao('');
    setEditQuantidade('');
    setEditPrecoUnitario('');
  };

  const salvarEdicaoItem = async (itemId: number) => {
    setEditError(null);

    if (!orcamento || !id) {
      setEditError('Orçamento inválido.');
      return;
    }

    if (!editDescricao.trim()) {
      setEditError('Informe a descrição do item.');
      return;
    }

    const quantidadeNum = Number(editQuantidade.replace(',', '.'));
    if (!Number.isFinite(quantidadeNum) || quantidadeNum <= 0) {
      setEditError('Informe uma quantidade válida (maior que zero).');
      return;
    }

    const precoNum = Number(editPrecoUnitario.replace(',', '.'));
    if (!Number.isFinite(precoNum) || precoNum < 0) {
      setEditError('Informe um preço unitário válido (zero ou maior).');
      return;
    }

    try {
      setEditLoadingId(itemId);

      const orcamentoId = Number(id);

      const payload: Partial<OrcamentoItemCreateInput> = {
        descricao: editDescricao.trim(),
        quantidade: quantidadeNum,
        preco_unitario: precoNum,
      };

      await updateOrcamentoItem(orcamentoId, itemId, payload);

      const [novoOrcamento, itensAtualizados] = await Promise.all([
        fetchOrcamentoById(orcamentoId),
        fetchOrcamentoItens(orcamentoId),
      ]);

      setOrcamento(novoOrcamento);
      setItens(itensAtualizados);

      cancelarEdicaoItem();
    } catch (error: any) {
      console.error('[Orçamentos] Erro ao editar item do orçamento:', error);

      const detail =
        error?.response?.data?.detail ||
        error?.response?.data?.message ||
        null;

      const message = mapPermissionMessage(
        detail,
        'Não foi possível salvar as alterações do item. Tente novamente.',
      );
      setEditError(message);
    } finally {
      setEditLoadingId(null);
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
            {/* ✅ Botão baixar PDF */}
            <button
              type="button"
              onClick={handleBaixarPdf}
              disabled={pdfLoading || loadingOrcamento || !!orcamentoError}
              className="inline-flex items-center rounded-md border border-primary-300 bg-primary-50 px-3 py-1.5 text-xs font-semibold text-primary-700 shadow-sm hover:bg-primary-100 disabled:opacity-60"
              title="Baixar PDF do orçamento"
            >
              {pdfLoading ? 'Baixando PDF...' : 'Baixar PDF'}
            </button>

            <button
              type="button"
              onClick={handleVoltar}
              className="inline-flex items-center rounded-md border border-slate-300 px-3 py-1.5 text-xs font-semibold text-slate-700 shadow-sm hover:bg-slate-50"
            >
              Voltar
            </button>
          </div>
        </div>

        {/* ✅ Erro do PDF */}
        {pdfError && (
          <div className="rounded-md border border-red-200 bg-red-50 px-3 py-2 text-xs text-red-700 shadow-sm">
            {pdfError}
          </div>
        )}

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
                  {mostrarFormNovoItem ? 'Fechar itens novos' : '+ Novo item'}
                </button>
              </div>

              {/* Erros relacionados a itens */}
              {deleteError && (
                <div className="mb-2 rounded-md border border-red-200 bg-red-50 px-3 py-1.5 text-xs text-red-700">
                  {deleteError}
                </div>
              )}
              {editError && (
                <div className="mb-2 rounded-md border border-red-200 bg-red-50 px-3 py-1.5 text-xs text-red-700">
                  {editError}
                </div>
              )}

              {/* Formulário de inclusão em lote (itens LIVRE) */}
              {mostrarFormNovoItem && (
                <form
                  onSubmit={handleAdicionarItem}
                  className="mb-4 rounded-md border border-slate-200 bg-slate-50 p-3 text-sm"
                >
                  <p className="mb-2 text-xs font-semibold uppercase tracking-wide text-slate-500">
                    Itens novos (tipo LIVRE)
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

                  <div className="mt-3 flex flex-col gap-2 sm:flex-row sm:items-center sm:justify-between">
                    <div className="flex flex-wrap gap-2">
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
                        className="inline-flex items-center justify-center rounded-md bg-emerald-600 px-3 py-1.5 text-xs font-semibold text-white shadow-sm hover:bg-emerald-700"
                        disabled={novoItemLoading}
                      >
                        Adicionar item
                      </button>
                    </div>

                    <button
                      type="button"
                      onClick={handleSalvarItens}
                      className="inline-flex items-center justify-center rounded-md bg-primary-600 px-3 py-1.5 text-xs font-semibold text-white shadow-sm hover:bg-primary-700 disabled:opacity-60"
                      disabled={novoItemLoading || novosItens.length === 0}
                    >
                      {novoItemLoading ? 'Salvando itens...' : 'Salvar itens'}
                    </button>
                  </div>

                  {novosItens.length > 0 && (
                    <p className="mt-2 text-xs text-slate-500">
                      {novosItens.length} item(ns) novo(s) pronto(s) para salvar.
                    </p>
                  )}
                </form>
              )}

              {/* Lista de itens */}
              {loadingItens ? (
                <p className="text-sm text-slate-600">
                  Carregando itens do orçamento...
                </p>
              ) : itensError ? (
                <p className="text-sm text-red-700">{itensError}</p>
              ) : itens.length === 0 && novosItens.length === 0 ? (
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
                        <th className="px-3 py-2 text-right">Ações</th>
                      </tr>
                    </thead>
                    <tbody>
                      {/* Itens já salvos no backend */}
                      {itens.map((item) => {
                        const isEditando =
                          editItemId === item.id && item.item_tipo === 'LIVRE';
                        const isDeleteLoading = deleteLoadingId === item.id;
                        const isEditLoading = editLoadingId === item.id;

                        return (
                          <tr
                            key={item.id}
                            className="border-b border-slate-100 hover:bg-slate-50"
                          >
                            <td className="px-3 py-2 text-slate-800">
                              {isEditando ? (
                                <input
                                  type="text"
                                  value={editDescricao}
                                  onChange={(e) =>
                                    setEditDescricao(e.target.value)
                                  }
                                  className="w-full rounded-md border border-slate-300 px-2 py-1 text-sm text-slate-800 shadow-sm outline-none focus:border-primary-500 focus:ring-1 focus:ring-primary-500"
                                />
                              ) : (
                                item.descricao ||
                                (item.item_tipo === 'HH'
                                  ? 'Hora-homem'
                                  : item.item_tipo === 'MATERIAL'
                                  ? 'Material'
                                  : 'Item')
                              )}
                            </td>
                            <td className="px-3 py-2 text-right text-slate-700">
                              {isEditando ? (
                                <input
                                  type="number"
                                  min={0}
                                  step={0.01}
                                  value={editQuantidade}
                                  onChange={(e) =>
                                    setEditQuantidade(e.target.value)
                                  }
                                  className="w-24 rounded-md border border-slate-300 px-2 py-1 text-sm text-slate-800 shadow-sm outline-none focus:border-primary-500 focus:ring-1 focus:ring-primary-500"
                                />
                              ) : (
                                item.quantidade
                              )}
                            </td>
                            <td className="px-3 py-2 text-slate-700">
                              {item.item_tipo}
                            </td>
                            <td className="px-3 py-2 text-slate-700">
                              {item.uom_id ?? '-'}
                            </td>
                            <td className="px-3 py-2 text-right text-slate-700">
                              {isEditando ? (
                                <input
                                  type="number"
                                  min={0}
                                  step={0.01}
                                  value={editPrecoUnitario}
                                  onChange={(e) =>
                                    setEditPrecoUnitario(e.target.value)
                                  }
                                  className="w-28 rounded-md border border-slate-300 px-2 py-1 text-sm text-slate-800 shadow-sm outline-none focus:border-primary-500 focus:ring-1 focus:ring-primary-500"
                                />
                              ) : item.preco_unitario != null ? (
                                formatCurrency(
                                  item.preco_unitario,
                                  orcamento.moeda,
                                )
                              ) : (
                                '-'
                              )}
                            </td>
                            <td className="px-3 py-2 text-right font-medium text-slate-900">
                              {formatCurrency(item.total_item, orcamento.moeda)}
                            </td>
                            <td className="px-3 py-2 text-right">
                              {isEditando ? (
                                <div className="flex justify-end gap-2">
                                  <button
                                    type="button"
                                    onClick={cancelarEdicaoItem}
                                    className="inline-flex items-center justify-center rounded-md border border-slate-300 px-2 py-1 text-xs font-semibold text-slate-700 hover:bg-slate-100"
                                    disabled={isEditLoading}
                                  >
                                    Cancelar
                                  </button>
                                  <button
                                    type="button"
                                    onClick={() => salvarEdicaoItem(item.id)}
                                    className="inline-flex items-center justify-center rounded-md bg-emerald-600 px-2 py-1 text-xs font-semibold text-white hover:bg-emerald-700 disabled:opacity-60"
                                    disabled={isEditLoading}
                                  >
                                    {isEditLoading ? 'Salvando...' : 'Salvar'}
                                  </button>
                                </div>
                              ) : (
                                <div className="flex justify-end gap-2">
                                  {item.item_tipo === 'LIVRE' && (
                                    <button
                                      type="button"
                                      onClick={() => iniciarEdicaoItem(item)}
                                      className="inline-flex items-center justify-center rounded-md border border-slate-300 px-2 py-1 text-xs font-semibold text-slate-700 hover:bg-slate-100 disabled:opacity-60"
                                      disabled={
                                        isDeleteLoading || novoItemLoading
                                      }
                                    >
                                      Editar
                                    </button>
                                  )}
                                  <button
                                    type="button"
                                    onClick={() => handleExcluirItem(item.id)}
                                    className="inline-flex items-center justify-center rounded-md border border-red-300 px-2 py-1 text-xs font-semibold text-red-700 hover:bg-red-50 disabled:opacity-50"
                                    disabled={
                                      isDeleteLoading ||
                                      isEditLoading ||
                                      novoItemLoading
                                    }
                                  >
                                    {isDeleteLoading
                                      ? 'Excluindo...'
                                      : 'Excluir'}
                                  </button>
                                </div>
                              )}
                            </td>
                          </tr>
                        );
                      })}

                      {/* Itens novos (ainda não salvos no backend) */}
                      {novosItens.map((item, index) => (
                        <tr
                          key={`novo-${index}`}
                          className="border-b border-emerald-100 bg-emerald-50/40"
                        >
                          <td className="px-3 py-2 text-slate-800">
                            {item.descricao || 'Item livre'}
                          </td>
                          <td className="px-3 py-2 text-right text-slate-700">
                            {item.quantidade}
                          </td>
                          <td className="px-3 py-2 text-slate-700">LIVRE</td>
                          <td className="px-3 py-2 text-slate-700">-</td>
                          <td className="px-3 py-2 text-right text-slate-700">
                            {item.preco_unitario != null
                              ? formatCurrency(
                                  item.preco_unitario,
                                  orcamento.moeda,
                                )
                              : '-'}
                          </td>
                          <td className="px-3 py-2 text-right font-medium text-slate-900">
                            {formatCurrency(
                              item.quantidade * (item.preco_unitario ?? 0),
                              orcamento.moeda,
                            )}
                          </td>
                          <td className="px-3 py-2 text-right text-xs text-slate-500">
                            (não salvo)
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
