// src/pages/OrcamentosList.tsx
// Lista de orçamentos - por enquanto com dados mockados.

import React from 'react';
import { AppLayout } from '../components/layout/AppLayout';

type OrcamentoStatus = 'ABERTO' | 'APROVADO' | 'CANCELADO';

interface Orcamento {
  id: number;
  codigo: string;
  cliente: string;
  valor_total: number;
  status: OrcamentoStatus;
  criado_em: string;
}

const mockOrcamentos: Orcamento[] = [
  {
    id: 1,
    codigo: 'ORC-001',
    cliente: 'Cliente Exemplo 1',
    valor_total: 12500.5,
    status: 'ABERTO',
    criado_em: '2025-01-10',
  },
  {
    id: 2,
    codigo: 'ORC-002',
    cliente: 'Cliente Exemplo 2',
    valor_total: 8420.0,
    status: 'APROVADO',
    criado_em: '2025-01-12',
  },
  {
    id: 3,
    codigo: 'ORC-003',
    cliente: 'Cliente Exemplo 3',
    valor_total: 3100.75,
    status: 'CANCELADO',
    criado_em: '2025-01-15',
  },
];

export const OrcamentosList: React.FC = () => {
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
          <button className="mt-2 inline-flex items-center justify-center rounded-md bg-primary-600 px-4 py-2 text-xs font-semibold text-white shadow-sm transition hover:bg-primary-700 sm:mt-0">
            + Novo orçamento
          </button>
        </div>

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
              {mockOrcamentos.map((orc) => (
                <tr
                  key={orc.id}
                  className="hover:bg-slate-50"
                >
                  <td className="border-b border-slate-100 px-3 py-2 align-middle">
                    <span className="font-medium text-slate-800">
                      {orc.codigo}
                    </span>
                  </td>
                  <td className="border-b border-slate-100 px-3 py-2 align-middle">
                    <span className="text-slate-700">{orc.cliente}</span>
                  </td>
                  <td className="border-b border-slate-100 px-3 py-2 text-right align-middle">
                    R$ {orc.valor_total.toLocaleString('pt-BR', { minimumFractionDigits: 2 })}
                  </td>
                  <td className="border-b border-slate-100 px-3 py-2 text-center align-middle">
                    <span
                      className={
                        [
                          'inline-flex rounded-full px-2 py-0.5 text-xs font-semibold',
                          orc.status === 'ABERTO' && 'bg-amber-100 text-amber-700',
                          orc.status === 'APROVADO' && 'bg-emerald-100 text-emerald-700',
                          orc.status === 'CANCELADO' && 'bg-rose-100 text-rose-700',
                        ]
                          .filter(Boolean)
                          .join(' ')
                      }
                    >
                      {orc.status}
                    </span>
                  </td>
                  <td className="border-b border-slate-100 px-3 py-2 text-center align-middle">
                    <span className="text-xs text-slate-600">
                      {orc.criado_em}
                    </span>
                  </td>
                  <td className="border-b border-slate-100 px-3 py-2 text-right align-middle">
                    <button className="text-xs font-semibold text-primary-600 hover:text-primary-700">
                      Detalhes
                    </button>
                  </td>
                </tr>
              ))}

              {mockOrcamentos.length === 0 && (
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
