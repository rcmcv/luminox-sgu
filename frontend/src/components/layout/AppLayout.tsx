// src/components/layout/AppLayout.tsx
// Layout principal da área logada: topo, menu e área de conteúdo.

import React from 'react';
import { NavLink, useNavigate } from 'react-router-dom';
import { useAuth } from '../../auth/useAuth';

interface AppLayoutProps {
  title?: string;
  children: React.ReactNode;
}

export const AppLayout: React.FC<AppLayoutProps> = ({ title, children }) => {
  const { user, logout } = useAuth();
  const navigate = useNavigate();

  const displayName =
    user?.name ?? user?.email ?? 'Usuário autenticado';

  const displayRole = user?.role ?? 'N/D';

  const handleLogout = () => {
    logout();
    navigate('/login', { replace: true });
  };

  return (
    <div className="flex min-h-screen flex-col bg-slate-100">
      {/* Topo */}
      <header className="flex items-center justify-between bg-primary-700 px-6 py-4 text-white shadow">
        <div className="flex items-center gap-3">
          <div className="flex h-10 w-10 items-center justify-center rounded-full bg-white/10">
            <span className="text-xl font-bold">L</span>
          </div>
          <div>
            <h1 className="text-lg font-semibold leading-tight">
              Luminox SGU
            </h1>
            <p className="text-xs text-primary-100">
              Sistema de Gestão de Usinagem
            </p>
          </div>
        </div>

        {/* Menu de navegação */}
        <nav className="flex items-center gap-2 text-sm">
          <NavLink
            to="/dashboard"
            className={({ isActive }) =>
              [
                'rounded-md px-3 py-1.5 font-medium transition',
                isActive ? 'bg-white text-primary-700 shadow-sm' : 'text-primary-100 hover:bg-primary-600/60',
              ].join(' ')
            }
          >
            Dashboard
          </NavLink>

          <NavLink
            to="/orcamentos"
            className={({ isActive }) =>
              [
                'rounded-md px-3 py-1.5 font-medium transition',
                isActive ? 'bg-white text-primary-700 shadow-sm' : 'text-primary-100 hover:bg-primary-600/60',
              ].join(' ')
            }
          >
            Orçamentos
          </NavLink>
        </nav>

        {/* Usuário + Sair */}
        <div className="flex items-center gap-4 text-sm">
          <div className="text-right">
            <p className="font-medium">{displayName}</p>
            <p className="text-xs text-primary-100">
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

      {/* Conteúdo */}
      <main className="flex flex-1 items-start justify-center px-4 py-6">
        <div className="w-full max-w-6xl">
          {title && (
            <h2 className="mb-4 text-xl font-semibold text-slate-800">
              {title}
            </h2>
          )}
          {children}
        </div>
      </main>
    </div>
  );
};
