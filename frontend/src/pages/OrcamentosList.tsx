// src/pages/OrcamentosList.tsx
// Lista de orçamentos - consumindo API real e exibindo nome do cliente.

import React, { useEffect, useState } from 'react';
import { AppLayout } from '../components/layout/AppLayout';
import { fetchOrcamentos } from '../api/orcamentos';
import { fetchClientes } from '../api/clientes';
import type { Orcamento } from '../types/orcamento';
import type { Cliente } from '../types/cliente';
import { useAuth } from '../auth/useAuth';

export const OrcamentosList: React.FC = () => {
  const { user } = useAuth();
  const [orcamentos, setOrcamentos] = useState<Orcamento[]>([]);
  const [clientesMap, setClientesMap] = useState<Record<number, string>>({});
  const [loading, setLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);

  // Regras de papel: ADMIN / OPERACAO podem criar; VIEWER só visualiza
  const role = user?.role ?? 'VIEWER';
  const canCreate = role === 'ADMIN' || role === 'OPERACAO';

  // Monta um nome amigável do cliente com base nos possíveis campos
  const buildClienteNome = (cliente: Cliente): string => {
    return (
      cliente.nome_fantasia ||
      cliente.nome ||
      cliente.razao_social ||
      `Cliente #${cliente.id}`
    );
  };

  useEffect(() => {
    const carregar = async () => {
      try {
        setLoading(true);
        setError(null);

        const [orcData, cliData] = await Promise.all([
          fetchOrcamentos(),
          fetchClientes(),
        ]);

        setOrcamentos(orcData);

        const map: Record<number, string> = {};
        cliData.forEach((cli) => {
          map[cli.id] = buildClienteNome(cli);
        });
        setClientesMap(map);
      } catch (err) {
        console.error('[Orçamentos] Erro ao carregar', err);
        setError(
          'Não foi possível carregar os orçamentos. Tente novamente mais tarde.',
        );
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
    if (orc.cliente_id && clientesMap[orc.cliente_id]) {
      return clientesMap[orc.cliente_id];
    }
    if (orc.cliente_id) {
      return `Cliente #${orc.cliente_id}`;
    }
    return '—';
  };

  const formatValor = (orc: Orcamento): string => {
    const valor = orc.total ?? orc.subtotal ?? 0;
    return `R$ ${valor.toLocaleString('pt-BR', {
      minimumFractionDigits: 2,
      maximumFractionDigits: 2,
    })}`;
  };

  const formatData = (dateStr: string | undefined): string => {
    if (!dateStr) return '—';
    return dateStr.split('T')[0];
  };

  const formatStatus = (orc: Orcamento): string => {
    return (orc.status ?? 'N/D').toString().toUpperCase();
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
                          {formatData(orc.created_at)}
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
