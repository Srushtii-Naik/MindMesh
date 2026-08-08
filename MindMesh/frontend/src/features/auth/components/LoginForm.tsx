import { useForm } from 'react-hook-form';
import { Link } from 'react-router-dom';
import { useLogin } from '@/features/auth/hooks';
import { extractAuthErrorMessage } from '@/features/auth/utils';
import { GoogleSignInButton } from '@/features/auth/components/GoogleSignInButton';
import type { LoginPayload } from '@/features/auth/types';
import { ROUTES } from '@/constants';

const EMAIL_PATTERN = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;

export function LoginForm() {
  const {
    register,
    handleSubmit,
    formState: { errors },
  } = useForm<LoginPayload>({ mode: 'onBlur' });

  const login = useLogin();

  const onSubmit = (values: LoginPayload) => {
    login.mutate(values);
  };

  return (
    <form onSubmit={handleSubmit(onSubmit)} noValidate className="space-y-4">
      <div>
        <label
          htmlFor="email"
          className="mb-1 block text-sm font-medium text-slate-700 dark:text-slate-300"
        >
          Email
        </label>
        <input
          id="email"
          type="email"
          autoComplete="email"
          className="w-full rounded-md border border-slate-300 bg-white px-3 py-2 text-sm text-slate-900 outline-none transition focus:border-brand-500 focus:ring-2 focus:ring-brand-500/30 dark:border-slate-700 dark:bg-slate-800 dark:text-slate-100"
          {...register('email', {
            required: 'Email is required.',
            pattern: { value: EMAIL_PATTERN, message: 'Enter a valid email address.' },
          })}
        />
        {errors.email && (
          <p className="mt-1 text-xs text-red-600 dark:text-red-400">{errors.email.message}</p>
        )}
      </div>

      <div>
        <div className="mb-1 flex items-center justify-between">
          <label
            htmlFor="password"
            className="block text-sm font-medium text-slate-700 dark:text-slate-300"
          >
            Password
          </label>
          <Link
            to={ROUTES.FORGOT_PASSWORD}
            className="text-xs font-medium text-brand-600 hover:underline dark:text-brand-400"
          >
            Forgot password?
          </Link>
        </div>
        <input
          id="password"
          type="password"
          autoComplete="current-password"
          className="w-full rounded-md border border-slate-300 bg-white px-3 py-2 text-sm text-slate-900 outline-none transition focus:border-brand-500 focus:ring-2 focus:ring-brand-500/30 dark:border-slate-700 dark:bg-slate-800 dark:text-slate-100"
          {...register('password', { required: 'Password is required.' })}
        />
        {errors.password && (
          <p className="mt-1 text-xs text-red-600 dark:text-red-400">{errors.password.message}</p>
        )}
      </div>

      {login.isError && (
        <p className="text-sm text-red-600 dark:text-red-400" role="alert">
          {extractAuthErrorMessage(login.error)}
        </p>
      )}

      <button
        type="submit"
        disabled={login.isPending}
        className="w-full rounded-md bg-brand-600 px-4 py-2 text-sm font-medium text-white transition hover:bg-brand-700 disabled:cursor-not-allowed disabled:opacity-60"
      >
        {login.isPending ? 'Signing in…' : 'Sign in'}
      </button>

      <div className="relative py-1 text-center">
        <span className="relative z-10 bg-white px-2 text-xs text-slate-400 dark:bg-slate-900">
          or
        </span>
        <div className="absolute inset-x-0 top-1/2 border-t border-slate-200 dark:border-slate-800" />
      </div>

      <div className="flex justify-center">
        <GoogleSignInButton />
      </div>

      <p className="text-center text-sm text-slate-500 dark:text-slate-400">
        Don&apos;t have an account?{' '}
        <Link
          to={ROUTES.REGISTER}
          className="font-medium text-brand-600 hover:underline dark:text-brand-400"
        >
          Create one
        </Link>
      </p>
    </form>
  );
}
