// src/routes/index.tsx
// Rotas principais.

import React from 'react';
import { Navigate, Route, Routes } from 'react-router-dom';
import { Login } from '../pages/Login';
import { Dashboard } from '../pages/Dashboard';
import { OrcamentosList } from '../pages/OrcamentosList';
import { OrcamentoDetalhe } from '../pages/OrcamentoDetalhe';
import { OrcamentoForm } from '../pages/OrcamentoForm';
import { RequireAuth } from '../auth/RequireAuth';

export const AppRoutes: React.FC = () => {
  return (
    <Routes>
      {/* Pública */}
      <Route path="/login" element={<Login />} />

      {/* Protegidas */}
      <Route
        path="/dashboard"
        element={
          <RequireAuth>
            <Dashboard />
          </RequireAuth>
        }
      />

      <Route
        path="/orcamentos"
        element={
          <RequireAuth>
            <OrcamentosList />
          </RequireAuth>
        }
      />

      <Route
        path="/orcamentos/novo"
        element={
          <RequireAuth>
            <OrcamentoForm />
          </RequireAuth>
        }
      />

      <Route
        path="/orcamentos/:id"
        element={
          <RequireAuth>
            <OrcamentoDetalhe />
          </RequireAuth>
        }
      />

      {/* Redireciona raiz */}
      <Route path="/" element={<Navigate to="/dashboard" replace />} />

      {/* Qualquer rota desconhecida */}
      <Route path="*" element={<Navigate to="/dashboard" replace />} />
    </Routes>
  );
};
