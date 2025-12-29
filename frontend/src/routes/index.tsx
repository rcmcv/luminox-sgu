// src/routes/index.tsx
// Rotas principais.

import React from 'react';
import { Navigate, Route, Routes } from 'react-router-dom';
import { Login } from '../pages/Login';
import { Dashboard } from '../pages/Dashboard';
import { OrcamentosList } from '../pages/OrcamentosList';
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

      {/* Redireciona raiz */}
      <Route path="/" element={<Navigate to="/dashboard" replace />} />

      {/* Qualquer rota desconhecida */}
      <Route path="*" element={<Navigate to="/dashboard" replace />} />
    </Routes>
  );
};
