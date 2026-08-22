import { useForm } from 'react-hook-form';
import { Link } from 'react-router-dom';
import { useRequestPasswordReset } from '@/features/auth/hooks';
import { extractAuthErrorMessage } from '@/features/auth/utils';
import type { PasswordResetRequestPayload } from '@/features/auth/types';
import { ROUTES } from '@/constants';

const EMAIL_PATTERN = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;

export function ForgotPasswordForm() {
  const {
    register,
    handleSubmit,
    formState: { errors },
  } = useForm<PasswordResetRequestPayload>({ mode: 'onBlur' });

  const requestReset = useRequestPasswordReset();

  const onSubmit = (values: PasswordResetRequestPayload) => {
    requestReset.mutate(values);
  };

  if (requestReset.isSuccess) {
    return (
      <div className="space-y-4 text-center">
        <p className="text-sm text-slate-600 dark:text-slate-300">
          If an account exists for that email, we&apos;ve sent a link to reset your password.
        </p>
        <Link
          to={ROUTES.LOGIN}
          className="inline-block text-sm font-medium text-brand-600 hover:underline dark:text-brand-400"
        >
          Back to sign in
        </Link>
      </div>
    );
  }

  return (
    <form onSubmit={handleSubmit(onSubmit)} noValidate className="space-y-4">
      <p className="text-sm text-slate-500 dark:text-slate-400">
        Enter the email associated with your account and we&apos;ll send you a link to reset your
        password.
      </p>

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

      {requestReset.isError && (
        <p className="text-sm text-red-600 dark:text-red-400" role="alert">
          {extractAuthErrorMessage(requestReset.error)}
        </p>
      )}

      <button
        type="submit"
        disabled={requestReset.isPending}
        className="w-full rounded-md bg-brand-600 px-4 py-2 text-sm font-medium text-white transition hover:bg-brand-700 disabled:cursor-not-allowed disabled:opacity-60"
      >
        {requestReset.isPending ? 'Sending…' : 'Send reset link'}
      </button>

      <p className="text-center text-sm text-slate-500 dark:text-slate-400">
        Remembered it?{' '}
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
