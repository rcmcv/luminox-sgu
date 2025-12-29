// src/pages/Dashboard.tsx

import React from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../auth/useAuth';

export const Dashboard: React.FC = () => {
  const { user, logout } = useAuth();
  const navigate = useNavigate();

  const displayName =
    user?.name ?? user?.email ?? 'Usuário autenticado';

  const displayRole = user?.role ?? 'N/D';

  const handleLogout = () => {
    // Limpa tokens e estado de usuário
    logout();
    // Redireciona explicitamente para /login
    navigate('/login', { replace: true });
  };

  return (
    <div className="flex min-h-screen flex-col bg-slate-100">
      <header className="flex items-center justify-between bg-primary-700 px-6 py-4 text-white">
        <h1 className="text-lg font-semibold">Dashboard - Luminox SGU</h1>
        <div className="flex items-center gap-4 text-sm">
          <div className="text-right">
            <p className="font-medium">{displayName}</p>
            <p className="text-xs text-primary-200">
              Papel: {displayRole}
            </p>
          </div>
          <button
            onClick={handleLogout}
            className="rounded-md bg-white/10 px-3 py-1 text-xs font-semibold hover:bg-white/20"
          >
            Sair
          </button>
        </div>
      </header>

      <main className="flex flex-1 items-start justify-center px-4 py-8">
        <div className="w-full max-w-4xl rounded-xl bg-white p-6 shadow-md">
          <h2 className="mb-4 text-xl font-semibold text-slate-800">
            Bem-vindo ao painel da Usinagem
          </h2>
          <p className="text-sm text-slate-600">
            Aqui futuramente vamos listar orçamentos, projetos, indicadores, etc.
          </p>
        </div>
      </main>
    </div>
  );
};
