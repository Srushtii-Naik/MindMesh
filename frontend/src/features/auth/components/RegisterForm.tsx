import { useForm } from 'react-hook-form';
import { Link } from 'react-router-dom';
import { useRegister } from '@/features/auth/hooks';
import { extractAuthErrorMessage } from '@/features/auth/utils';
import { GoogleSignInButton } from '@/features/auth/components/GoogleSignInButton';
import type { RegisterPayload } from '@/features/auth/types';
import { ROUTES } from '@/constants';

const EMAIL_PATTERN = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;

export function RegisterForm() {
  const {
    register,
    handleSubmit,
    watch,
    formState: { errors },
  } = useForm<RegisterPayload>({ mode: 'onBlur' });

  const registerMutation = useRegister();
  const password = watch('password');

  const onSubmit = (values: RegisterPayload) => {
    registerMutation.mutate(values);
  };

  return (
    <form onSubmit={handleSubmit(onSubmit)} noValidate className="space-y-4">
      <div>
        <label
          htmlFor="full_name"
          className="mb-1 block text-sm font-medium text-slate-700 dark:text-slate-300"
        >
          Full name
        </label>
        <input
          id="full_name"
          type="text"
          autoComplete="name"
          className="w-full rounded-md border border-slate-300 bg-white px-3 py-2 text-sm text-slate-900 outline-none transition focus:border-brand-500 focus:ring-2 focus:ring-brand-500/30 dark:border-slate-700 dark:bg-slate-800 dark:text-slate-100"
          {...register('full_name', {
            required: 'Full name is required.',
            minLength: { value: 2, message: 'Full name is too short.' },
          })}
        />
        {errors.full_name && (
          <p className="mt-1 text-xs text-red-600 dark:text-red-400">{errors.full_name.message}</p>
        )}
      </div>

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
        <label
          htmlFor="password"
          className="mb-1 block text-sm font-medium text-slate-700 dark:text-slate-300"
        >
          Password
        </label>
        <input
          id="password"
          type="password"
          autoComplete="new-password"
          className="w-full rounded-md border border-slate-300 bg-white px-3 py-2 text-sm text-slate-900 outline-none transition focus:border-brand-500 focus:ring-2 focus:ring-brand-500/30 dark:border-slate-700 dark:bg-slate-800 dark:text-slate-100"
          {...register('password', {
            required: 'Password is required.',
            minLength: { value: 8, message: 'Password must be at least 8 characters.' },
          })}
        />
        {errors.password && (
          <p className="mt-1 text-xs text-red-600 dark:text-red-400">{errors.password.message}</p>
        )}
        <p className="mt-1 text-xs text-slate-400">
          The server also enforces its own password strength rules.
        </p>
      </div>

      <div>
        <label
          htmlFor="password_confirm"
          className="mb-1 block text-sm font-medium text-slate-700 dark:text-slate-300"
        >
          Confirm password
        </label>
        <input
          id="password_confirm"
          type="password"
          autoComplete="new-password"
          className="w-full rounded-md border border-slate-300 bg-white px-3 py-2 text-sm text-slate-900 outline-none transition focus:border-brand-500 focus:ring-2 focus:ring-brand-500/30 dark:border-slate-700 dark:bg-slate-800 dark:text-slate-100"
          {...register('password_confirm', {
            required: 'Please confirm your password.',
            validate: (value) => value === password || 'Passwords do not match.',
          })}
        />
        {errors.password_confirm && (
          <p className="mt-1 text-xs text-red-600 dark:text-red-400">
            {errors.password_confirm.message}
          </p>
        )}
      </div>

      {registerMutation.isError && (
        <p className="text-sm text-red-600 dark:text-red-400" role="alert">
          {extractAuthErrorMessage(registerMutation.error)}
        </p>
      )}

      <button
        type="submit"
        disabled={registerMutation.isPending}
        className="w-full rounded-md bg-brand-600 px-4 py-2 text-sm font-medium text-white transition hover:bg-brand-700 disabled:cursor-not-allowed disabled:opacity-60"
      >
        {registerMutation.isPending ? 'Creating account…' : 'Create account'}
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
        Already have an account?{' '}
        <Link
          to={ROUTES.LOGIN}
          className="font-medium text-brand-600 hover:underline dark:text-brand-400"
        >
          Sign in
        </Link>
      </p>
    </form>
  );
}
