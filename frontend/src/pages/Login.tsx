// src/pages/Login.tsx

import React, { useState } from 'react';
import { useNavigate, useLocation } from 'react-router-dom';
import { useAuth } from '../auth/useAuth';

interface LocationState {
  from?: string;
}

export const Login: React.FC = () => {
  console.log('Renderizando Login...'); // <- teste no console

  const { login } = useAuth();
  const navigate = useNavigate();
  const location = useLocation();
  const state = location.state as LocationState | null;

  const [email, setEmail] = useState<string>('');
  const [password, setPassword] = useState<string>('');
  const [submitting, setSubmitting] = useState<boolean>(false);
  const [error, setError] = useState<string | null>(null);
  const [remember, setRemember] = useState<boolean>(false);

  const handleSubmit = async (event: React.FormEvent) => {
    event.preventDefault();
    setSubmitting(true);
    setError(null);

    try {
      await login(email, password);
      const redirectTo = state?.from || '/dashboard';
      navigate(redirectTo, { replace: true });
    } catch (err) {
      console.error(err);
      setError('Usuário ou senha inválidos. Verifique seus dados e tente novamente.');
    } finally {
      setSubmitting(false);
    }
  };

  return (
    <div className="flex min-h-screen bg-slate-100">
      {/* Lado esquerdo - faixa azul */}
      <div className="hidden w-1/2 items-center justify-center bg-primary-700 px-8 text-white lg:flex">
        <div className="max-w-md space-y-4">
          <div className="flex items-center gap-3">
            <div className="flex h-14 w-14 items-center justify-center rounded-full bg-white/10">
              <span className="text-3xl font-bold">L</span>
            </div>
            <div>
              <p className="text-sm uppercase tracking-wide text-primary-100">
                Sistema de Gestão
              </p>
              <h1 className="text-3xl font-bold leading-tight">Luminox SGU</h1>
              <p className="text-sm text-primary-100">
                Usinagem, organização e eficiência na palma da mão.
              </p>
            </div>
          </div>

          <hr className="border-primary-400/40" />

          <p className="text-sm leading-relaxed text-primary-100">
            Acompanhe orçamentos, projetos e clientes em um só lugar.
            Acesse com suas credenciais para continuar.
          </p>
        </div>
      </div>

      {/* Lado direito - formulário */}
      <div className="flex w-full items-center justify-center bg-white px-6 py-10 sm:px-10 md:px-16 lg:w-1/2">
        <div className="w-full max-w-md">
          <div className="mb-8 text-center lg:text-left">
            <h2 className="text-2xl font-bold text-primary-700 md:text-3xl">
              Acessar a plataforma
            </h2>
            <p className="mt-2 text-sm text-slate-500">
              Insira suas informações para continuar.
            </p>
          </div>

          {error && (
            <div className="mb-4 rounded-md border border-red-200 bg-red-50 px-3 py-2 text-sm text-red-700">
              {error}
            </div>
          )}

          <form onSubmit={handleSubmit} className="space-y-4">
            <div>
              <label
                htmlFor="email"
                className="mb-1 block text-sm font-medium text-slate-700"
              >
                Nome de usuário / E-mail
              </label>
              <input
                id="email"
                type="email"
                autoComplete="username"
                required
                className="block w-full rounded-lg border border-slate-300 px-3 py-2 text-sm shadow-sm outline-none ring-primary-500 placeholder:text-slate-400 focus:border-primary-500 focus:ring-1"
                placeholder="Digite seu e-mail"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                disabled={submitting}
              />
            </div>

            <div>
              <label
                htmlFor="password"
                className="mb-1 block text-sm font-medium text-slate-700"
              >
                Senha
              </label>
              <input
                id="password"
                type="password"
                autoComplete="current-password"
                required
                className="block w-full rounded-lg border border-slate-300 px-3 py-2 text-sm shadow-sm outline-none ring-primary-500 placeholder:text-slate-400 focus:border-primary-500 focus:ring-1"
                placeholder="Digite sua senha"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                disabled={submitting}
              />
            </div>

            <div className="flex items-center justify-between text-xs sm:text-sm">
              <label className="inline-flex items-center gap-2 text-slate-600">
                <button
                  type="button"
                  onClick={() => setRemember((prev) => !prev)}
                  className={`relative inline-flex h-5 w-9 items-center rounded-full border transition ${
                    remember
                      ? 'border-primary-500 bg-primary-500'
                      : 'border-slate-300 bg-slate-200'
                  }`}
                >
                  <span
                    className={`inline-block h-4 w-4 transform rounded-full bg-white shadow transition ${
                      remember ? 'translate-x-4' : 'translate-x-1'
                    }`}
                  />
                </button>
                <span>Lembrar meu login</span>
              </label>

              <button
                type="button"
                className="text-primary-600 hover:text-primary-700"
              >
                Esqueceu a senha?
              </button>
            </div>

            <button
              type="submit"
              disabled={submitting}
              className="mt-2 w-full rounded-lg bg-primary-600 px-4 py-2 text-sm font-semibold text-white shadow-md transition hover:bg-primary-700 disabled:cursor-not-allowed disabled:opacity-70"
            >
              {submitting ? 'Entrando...' : 'Fazer login'}
            </button>
          </form>

          <div className="mt-8 text-center text-xs text-slate-400">
            <p>Sistema de Gestão de Usinagem</p>
            <p className="mt-1">
              Desenvolvido por{' '}
              <span className="font-semibold text-primary-600">Luminox</span>
            </p>
          </div>
        </div>
      </div>
    </div>
  );
};
