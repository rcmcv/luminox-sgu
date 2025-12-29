// src/pages/Dashboard.tsx

import React from 'react';
import { AppLayout } from '../components/layout/AppLayout';

export const Dashboard: React.FC = () => {
  return (
    <AppLayout title="Dashboard">
      <div className="rounded-xl bg-white p-6 shadow-md">
        <h3 className="mb-3 text-lg font-semibold text-slate-800">
          Visão geral
        </h3>
        <p className="text-sm text-slate-600">
          Aqui futuramente vamos listar indicadores, cards de resumo,
          atalhos para orçamentos, projetos e outras informações da usinagem.
        </p>
      </div>
    </AppLayout>
  );
};
