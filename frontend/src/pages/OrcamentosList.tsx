// src/pages/OrcamentosList.tsx
// Lista de orçamentos - agora consumindo API real.

import React, { useEffect, useState } from 'react';
import { AppLayout } from '../components/layout/AppLayout';
import { fetchOrcamentos } from '../api/orcamentos';
import type { Orcamento } from '../types/orcamento';
import { useAuth } from '../auth/useAuth';

export const OrcamentosList: React.FC = () => {
  const { user } = useAuth();
  const [orcamentos, setOrcamentos] = useState<Orcamento[]>([]);
  const [loading, setLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);

  // Regras de papel: ADMIN / OPERACAO podem criar; VIEWER só visualiza
  const role = user?.role ?? 'VIEWER';
  const canCreate = role === 'ADMIN' || role === 'OPERACAO';

  useEffect(() => {
    const carregar = async () => {
      try {
        setLoading(true);
        setError(null);
        const data = await fetchOrcamentos();
        setOrcamentos(data);
      } catch (err) {
        console.error('[Orçamentos] Erro ao carregar', err);
        setError('Não foi possível carregar os orçamentos. Tente novamente mais tarde.');
      } finally {
        setLoading(false);
      }
    };

    carregar();
  }, []);

  const formatCodigo = (orc: Orcamento): string => {
    if (orc.codigo) return orc.codigo;
    if (orc.numero) return orc.numero;
    return `#${orc.id}`;
  };

  const formatCliente = (orc: Orcamento): string => {
    // Se vier como string direta
    if (typeof orc.cliente === 'string') return orc.cliente;
    // Se vier em campo cliente_nome
    if (orc.cliente_nome) return orc.cliente_nome;
    // Se vier como objeto (cliente: { nome: '...' })
    if (orc.cliente && typeof orc.cliente === 'object') {
      const anyCliente = orc.cliente as { nome?: string; name?: string };
      return anyCliente.nome ?? anyCliente.name ?? '—';
    }
    return '—';
  };

  const formatValor = (orc: Orcamento): string => {
    const valor = orc.valor_total ?? orc.valor ?? 0;
    return `R$ ${valor.toLocaleString('pt-BR', {
      minimumFractionDigits: 2,
      maximumFractionDigits: 2,
    })}`;
  };

  const formatData = (orc: Orcamento): string => {
    const raw = orc.criado_em ?? orc.created_at;
    if (!raw || typeof raw !== 'string') return '—';
    // Mostra só a parte da data, se vier em formato ISO
    return raw.split('T')[0];
  };

  const formatStatus = (orc: Orcamento): string => {
    return (orc.status ?? 'N/D').toString().toUpperCase();
  };

  const getStatusClasses = (status: string): string => {
    if (status === 'ABERTO') {
      return 'bg-amber-100 text-amber-700';
    }
    if (status === 'APROVADO') {
      return 'bg-emerald-100 text-emerald-700';
    }
    if (status === 'CANCELADO') {
      return 'bg-rose-100 text-rose-700';
    }
    return 'bg-slate-100 text-slate-700';
  };

  return (
    <AppLayout title="Orçamentos">
      <div className="rounded-xl bg-white p-6 shadow-md">
        <div className="mb-4 flex flex-col gap-3 sm:flex-row sm:items-center sm:justify-between">
          <div>
            <h3 className="text-lg font-semibold text-slate-800">
              Lista de orçamentos
            </h3>
            <p className="text-xs text-slate-500">
              Nesta tela você poderá visualizar e gerenciar os orçamentos da usinagem.
            </p>
          </div>

          {canCreate && (
            <button className="mt-2 inline-flex items-center justify-center rounded-md bg-primary-600 px-4 py-2 text-xs font-semibold text-white shadow-sm transition hover:bg-primary-700 sm:mt-0">
              + Novo orçamento
            </button>
          )}
        </div>

        {/* Mensagens de loading / erro */}
        {loading && (
          <p className="mb-3 text-sm text-slate-500">
            Carregando orçamentos...
          </p>
        )}

        {error && (
          <div className="mb-3 rounded-md border border-red-200 bg-red-50 px-3 py-2 text-sm text-red-700">
            {error}
          </div>
        )}

        <div className="overflow-x-auto">
          <table className="min-w-full border-collapse text-sm">
            <thead>
              <tr className="bg-slate-50">
                <th className="border-b border-slate-200 px-3 py-2 text-left font-semibold text-slate-700">
                  Código
                </th>
                <th className="border-b border-slate-200 px-3 py-2 text-left font-semibold text-slate-700">
                  Cliente
                </th>
                <th className="border-b border-slate-200 px-3 py-2 text-right font-semibold text-slate-700">
                  Valor total
                </th>
                <th className="border-b border-slate-200 px-3 py-2 text-center font-semibold text-slate-700">
                  Status
                </th>
                <th className="border-b border-slate-200 px-3 py-2 text-center font-semibold text-slate-700">
                  Criado em
                </th>
                <th className="border-b border-slate-200 px-3 py-2 text-right font-semibold text-slate-700">
                  Ações
                </th>
              </tr>
            </thead>
            <tbody>
              {!loading &&
                orcamentos.map((orc) => {
                  const status = formatStatus(orc);
                  return (
                    <tr
                      key={orc.id}
                      className="hover:bg-slate-50"
                    >
                      <td className="border-b border-slate-100 px-3 py-2 align-middle">
                        <span className="font-medium text-slate-800">
                          {formatCodigo(orc)}
                        </span>
                      </td>
                      <td className="border-b border-slate-100 px-3 py-2 align-middle">
                        <span className="text-slate-700">
                          {formatCliente(orc)}
                        </span>
                      </td>
                      <td className="border-b border-slate-100 px-3 py-2 text-right align-middle">
                        {formatValor(orc)}
                      </td>
                      <td className="border-b border-slate-100 px-3 py-2 text-center align-middle">
                        <span
                          className={[
                            'inline-flex rounded-full px-2 py-0.5 text-xs font-semibold',
                            getStatusClasses(status),
                          ].join(' ')}
                        >
                          {status}
                        </span>
                      </td>
                      <td className="border-b border-slate-100 px-3 py-2 text-center align-middle">
                        <span className="text-xs text-slate-600">
                          {formatData(orc)}
                        </span>
                      </td>
                      <td className="border-b border-slate-100 px-3 py-2 text-right align-middle">
                        <button className="text-xs font-semibold text-primary-600 hover:text-primary-700">
                          Detalhes
                        </button>
                      </td>
                    </tr>
                  );
                })}

              {!loading && !error && orcamentos.length === 0 && (
                <tr>
                  <td
                    colSpan={6}
                    className="px-3 py-4 text-center text-sm text-slate-500"
                  >
                    Nenhum orçamento encontrado.
                  </td>
                </tr>
              )}
            </tbody>
          </table>
        </div>
      </div>
    </AppLayout>
  );
};
