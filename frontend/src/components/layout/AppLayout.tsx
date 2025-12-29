// src/components/layout/AppLayout.tsx
// Layout principal da área logada com sidebar lateral responsiva.

import React, { useState } from 'react';
import { NavLink, useNavigate } from 'react-router-dom';
import { useAuth } from '../../auth/useAuth';

interface AppLayoutProps {
  title?: string;
  children: React.ReactNode;
}

export const AppLayout: React.FC<AppLayoutProps> = ({ title, children }) => {
  const { user, logout } = useAuth();
  const navigate = useNavigate();
  const [sidebarOpen, setSidebarOpen] = useState(false);

  const displayName =
    user?.name ?? user?.email ?? 'Usuário autenticado';

  const displayRole = user?.role ?? 'N/D';

  const handleLogout = () => {
    logout();
    navigate('/login', { replace: true });
  };

  const closeSidebar = () => setSidebarOpen(false);

  return (
    <div className="flex min-h-screen bg-slate-100">
      {/* Overlay para mobile quando sidebar aberta */}
      {sidebarOpen && (
        <div
          className="fixed inset-0 z-20 bg-black/30 md:hidden"
          onClick={closeSidebar}
        />
      )}

      {/* Sidebar */}
      <aside
        className={[
          'fixed inset-y-0 left-0 z-30 flex w-64 flex-col bg-primary-800 text-white shadow-lg transition-transform md:static md:translate-x-0',
          sidebarOpen ? 'translate-x-0' : '-translate-x-full md:translate-x-0',
        ].join(' ')}
      >
        {/* Logo + título */}
        <div className="flex items-center gap-3 border-b border-primary-700 px-5 py-4">
          <div className="flex h-10 w-10 items-center justify-center rounded-full bg-white/10">
            <span className="text-xl font-bold">L</span>
          </div>
          <div>
            <h1 className="text-sm font-semibold leading-tight">
              Luminox SGU
            </h1>
            <p className="text-[11px] text-primary-100">
              Gestão de Usinagem
            </p>
          </div>
        </div>

        {/* Navegação */}
        <nav className="flex-1 space-y-1 px-3 py-4 text-sm">
          <p className="mb-2 px-2 text-[11px] font-semibold uppercase tracking-wide text-primary-200">
            Navegação
          </p>

          <NavLink
            to="/dashboard"
            className={({ isActive }) =>
              [
                'flex items-center gap-2 rounded-md px-3 py-2 font-medium transition',
                isActive
                  ? 'bg-white text-primary-800 shadow-sm'
                  : 'text-primary-100 hover:bg-primary-700/70',
              ].join(' ')
            }
            onClick={closeSidebar}
          >
            <span>Dashboard</span>
          </NavLink>

          <NavLink
            to="/orcamentos"
            className={({ isActive }) =>
              [
                'flex items-center gap-2 rounded-md px-3 py-2 font-medium transition',
                isActive
                  ? 'bg-white text-primary-800 shadow-sm'
                  : 'text-primary-100 hover:bg-primary-700/70',
              ].join(' ')
            }
            onClick={closeSidebar}
          >
            <span>Orçamentos</span>
          </NavLink>
        </nav>

        {/* Info do usuário no rodapé da sidebar (desktop) */}
        <div className="hidden border-t border-primary-700 px-4 py-3 text-xs text-primary-100 md:block">
          <p className="truncate font-medium">{displayName}</p>
          <p className="text-[11px] text-primary-200">Papel: {displayRole}</p>
        </div>
      </aside>

      {/* Área principal */}
      <div className="flex flex-1 flex-col">
        {/* Top bar */}
        <header className="flex items-center justify-between bg-white px-4 py-3 shadow-sm">
          <div className="flex items-center gap-3">
            {/* Botão menu (só no mobile) */}
            <button
              type="button"
              className="inline-flex items-center justify-center rounded-md border border-slate-200 bg-white p-1.5 text-slate-600 shadow-sm hover:bg-slate-50 md:hidden"
              onClick={() => setSidebarOpen((prev) => !prev)}
            >
              <span className="sr-only">Abrir menu</span>
              {/* ícone hambúrguer simples */}
              <div className="space-y-0.5">
                <span className="block h-0.5 w-4 rounded bg-slate-600" />
                <span className="block h-0.5 w-4 rounded bg-slate-600" />
                <span className="block h-0.5 w-3 rounded bg-slate-600" />
              </div>
            </button>

            <div>
              <p className="text-xs uppercase tracking-wide text-slate-400">
                Luminox SGU
              </p>
              <h2 className="text-sm font-semibold text-slate-800 md:text-base">
                {title ?? 'Painel'}
              </h2>
            </div>
          </div>

          {/* Usuário + sair (no topo, sempre visível) */}
          <div className="flex items-center gap-3 text-xs md:text-sm">
            <div className="hidden text-right md:block">
              <p className="font-medium text-slate-800">{displayName}</p>
              <p className="text-[11px] text-slate-500">
                Papel: {displayRole}
              </p>
            </div>
            <button
              onClick={handleLogout}
              className="rounded-md bg-primary-600 px-3 py-1 text-xs font-semibold text-white shadow-sm transition hover:bg-primary-700"
            >
              Sair
            </button>
          </div>
        </header>

        {/* Conteúdo */}
        <main className="flex-1 px-4 py-4 md:px-6 md:py-6">
          <div className="mx-auto max-w-6xl">{children}</div>
        </main>
      </div>
    </div>
  );
};
