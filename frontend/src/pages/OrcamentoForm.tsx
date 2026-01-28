// src/pages/OrcamentoForm.tsx
// Formulário para criação de um novo orçamento (/orcamentos/novo).
// Futuramente, podemos reutilizar este componente para edição.

import React, { useEffect, useState } from 'react';
import type { FormEvent } from 'react';
import { useNavigate } from 'react-router-dom';
import { AppLayout } from '../components/layout/AppLayout';
import { fetchClientes } from '../api/clientes';
import type { Cliente } from '../types/cliente';
import {
  createOrcamento,
  type OrcamentoCreateInput,
} from '../api/orcamentos';
import type { OrcamentoStatus, OrcamentoTipo } from '../types/orcamento';

export const OrcamentoForm: React.FC = () => {
  const navigate = useNavigate();

  const [clientes, setClientes] = useState<Cliente[]>([]);
  const [loadingClientes, setLoadingClientes] = useState<boolean>(false);

  const [clienteId, setClienteId] = useState<string>('');
  const [tipo, setTipo] = useState<OrcamentoTipo>('SPOT');
  const [status, setStatus] = useState<OrcamentoStatus>('RASCUNHO');
  const [moeda, setMoeda] = useState<string>('BRL');
  const [titulo, setTitulo] = useState<string>('');
  const [observacoes, setObservacoes] = useState<string>('');

  const [saving, setSaving] = useState<boolean>(false);
  const [formError, setFormError] = useState<string | null>(null);

  useEffect(() => {
    const carregarClientes = async () => {
      try {
        setLoadingClientes(true);
        const data = await fetchClientes();
        setClientes(data);
      } catch (err) {
        console.warn('[Orçamentos] Erro ao carregar clientes:', err);
      } finally {
        setLoadingClientes(false);
      }
    };

    carregarClientes();
  }, []);

  const buildClienteNome = (cliente: Cliente): string => {
    return (
      cliente.nome_fantasia ||
      cliente.nome ||
      cliente.razao_social ||
      `Cliente #${cliente.id}`
    );
  };

  const buildClienteNomeFromId = (id: number): string => {
    const cli = clientes.find((c) => c.id === id);
    if (!cli) return `Cliente #${id}`;
    return buildClienteNome(cli);
  };

  const handleCancelar = () => {
    navigate('/orcamentos');
  };

  const handleSubmit = async (event: FormEvent<HTMLFormElement>) => {
    event.preventDefault();
    setFormError(null);

    // Validações simples
    if (!clienteId) {
      setFormError('Selecione um cliente.');
      return;
    }

    if (!tipo) {
      setFormError('Selecione o tipo de orçamento.');
      return;
    }

    if (!moeda) {
      setFormError('Informe a moeda.');
      return;
    }

    const payload: OrcamentoCreateInput = {
      cliente_id: Number(clienteId),
      tipo,
      status,
      contrato_id: null,
      moeda,
      titulo: titulo || null,
      observacoes: observacoes || null,
      subtotal: 0,
      desconto: 0,
      acrescimo: 0,
      total: 0,
    };

    try {
      setSaving(true);
      const created = await createOrcamento(payload);

      // 👉 Fluxo ajustado:
      // Nada de mensagem aqui; vamos direto para o detalhe do orçamento recém-criado.
      navigate(`/orcamentos/${created.id}`, {
        state: { clienteNome: buildClienteNomeFromId(created.cliente_id) },
      });
    } catch (error: any) {
      console.error('[Orçamentos] Erro ao salvar novo orçamento:', error);

      const detail =
        error?.response?.data?.detail ||
        error?.response?.data?.message ||
        null;

      if (typeof detail === 'string') {
        setFormError(detail);
      } else {
        setFormError(
          'Não foi possível salvar o orçamento. Verifique os dados e tente novamente.',
        );
      }
    } finally {
      setSaving(false);
    }
  };

  return (
    <AppLayout title="Novo orçamento">
      <div className="mx-auto max-w-3xl rounded-xl bg-white p-6 shadow-md">
        <h2 className="mb-4 text-lg font-semibold text-slate-800">
          Cadastro de orçamento
        </h2>
        <p className="mb-4 text-sm text-slate-500">
          Preencha os dados básicos do orçamento. Os itens poderão ser
          configurados posteriormente.
        </p>

        {formError && (
          <div className="mb-3 rounded-md border border-red-200 bg-red-50 px-3 py-2 text-sm text-red-700">
            {formError}
          </div>
        )}

        <form
          onSubmit={handleSubmit}
          className="space-y-4 text-sm"
        >
          {/* Linha: Cliente */}
          <div className="grid gap-3 sm:grid-cols-2">
            <div className="sm:col-span-2">
              <label className="mb-1 block text-xs font-semibold uppercase tracking-wide text-slate-600">
                Cliente
              </label>
              <select
                value={clienteId}
                onChange={(e) => setClienteId(e.target.value)}
                className="w-full rounded-md border border-slate-300 px-3 py-2 text-sm text-slate-700 shadow-sm outline-none focus:border-primary-500 focus:ring-1 focus:ring-primary-500"
              >
                <option value="">
                  {loadingClientes
                    ? 'Carregando clientes...'
                    : 'Selecione um cliente'}
                </option>
                {clientes.map((cliente) => (
                  <option
                    key={cliente.id}
                    value={cliente.id}
                  >
                    {buildClienteNome(cliente)}
                  </option>
                ))}
              </select>
              <p className="mt-1 text-xs text-slate-400">
                Se o cliente não estiver na lista, cadastre-o primeiro no módulo de
                Clientes.
              </p>
            </div>
          </div>

          {/* Linha: Tipo, Status e Moeda */}
          <div className="grid gap-3 sm:grid-cols-3">
            <div>
              <label className="mb-1 block text-xs font-semibold uppercase tracking-wide text-slate-600">
                Tipo
              </label>
              <select
                value={tipo}
                onChange={(e) => setTipo(e.target.value as OrcamentoTipo)}
                className="w-full rounded-md border border-slate-300 px-3 py-2 text-sm text-slate-700 shadow-sm outline-none focus:border-primary-500 focus:ring-1 focus:ring-primary-500"
              >
                <option value="SPOT">SPOT</option>
                {/* Futuro:
                <option value="CONTRATO">CONTRATO</option>
                */}
              </select>
            </div>

            <div>
              <label className="mb-1 block text-xs font-semibold uppercase tracking-wide text-slate-600">
                Status
              </label>
              <select
                value={status}
                onChange={(e) => setStatus(e.target.value as OrcamentoStatus)}
                className="w-full rounded-md border border-slate-300 px-3 py-2 text-sm text-slate-700 shadow-sm outline-none focus:border-primary-500 focus:ring-1 focus:ring-primary-500"
              >
                <option value="RASCUNHO">RASCUNHO</option>
                <option value="ENVIADO">ENVIADO</option>
                <option value="ACEITO">ACEITO</option>
                <option value="CANCELADO">CANCELADO</option>
              </select>
            </div>

            <div>
              <label className="mb-1 block text-xs font-semibold uppercase tracking-wide text-slate-600">
                Moeda
              </label>
              <input
                type="text"
                value={moeda}
                onChange={(e) => setMoeda(e.target.value.toUpperCase())}
                className="w-full rounded-md border border-slate-300 px-3 py-2 text-sm text-slate-700 shadow-sm outline-none focus:border-primary-500 focus:ring-1 focus:ring-primary-500"
              />
            </div>
          </div>

          {/* Linha: Título */}
          <div>
            <label className="mb-1 block text-xs font-semibold uppercase tracking-wide text-slate-600">
              Título do orçamento
            </label>
            <input
              type="text"
              value={titulo}
              onChange={(e) => setTitulo(e.target.value)}
              placeholder="Ex.: Usinagem de peças para projeto X"
              className="w-full rounded-md border border-slate-300 px-3 py-2 text-sm text-slate-700 shadow-sm outline-none placeholder:text-slate-400 focus:border-primary-500 focus:ring-1 focus:ring-primary-500"
            />
          </div>

          {/* Linha: Observações */}
          <div>
            <label className="mb-1 block text-xs font-semibold uppercase tracking-wide text-slate-600">
              Observações
            </label>
            <textarea
              value={observacoes}
              onChange={(e) => setObservacoes(e.target.value)}
              rows={4}
              placeholder="Observações gerais sobre o orçamento, condições comerciais, prazos, etc."
              className="w-full rounded-md border border-slate-300 px-3 py-2 text-sm text-slate-700 shadow-sm outline-none placeholder:text-slate-400 focus:border-primary-500 focus:ring-1 focus:ring-primary-500"
            />
          </div>

          {/* Ações */}
          <div className="mt-4 flex flex-col gap-2 sm:flex-row sm:justify-end">
            <button
              type="button"
              onClick={handleCancelar}
              className="inline-flex items-center justify-center rounded-md border border-slate-300 px-4 py-2 text-xs font-semibold text-slate-700 shadow-sm transition hover:bg-slate-50"
              disabled={saving}
            >
              Cancelar
            </button>
            <button
              type="submit"
              className="inline-flex items-center justify-center rounded-md bg-primary-600 px-4 py-2 text-xs font-semibold text-white shadow-sm transition hover:bg-primary-700 disabled:opacity-60"
              disabled={saving}
            >
              {saving ? 'Salvando...' : 'Salvar orçamento'}
            </button>
          </div>
        </form>
      </div>
    </AppLayout>
  );
};
