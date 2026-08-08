import { useForm } from 'react-hook-form';
import { Link, useSearchParams } from 'react-router-dom';
import { useConfirmPasswordReset } from '@/features/auth/hooks';
import { extractAuthErrorMessage } from '@/features/auth/utils';
import { ROUTES } from '@/constants';

interface ResetPasswordFormValues {
  new_password: string;
  new_password_confirm: string;
}

export function ResetPasswordForm() {
  const [searchParams] = useSearchParams();
  const uid = searchParams.get('uid');
  const token = searchParams.get('token');

  const {
    register,
    handleSubmit,
    watch,
    formState: { errors },
  } = useForm<ResetPasswordFormValues>({ mode: 'onBlur' });

  const confirmReset = useConfirmPasswordReset();
  const newPassword = watch('new_password');

  if (!uid || !token) {
    return (
      <div className="space-y-4 text-center">
        <p className="text-sm text-red-600 dark:text-red-400">
          This password reset link is missing required information. Please request a new one.
        </p>
        <Link
          to={ROUTES.FORGOT_PASSWORD}
          className="inline-block text-sm font-medium text-brand-600 hover:underline dark:text-brand-400"
        >
          Request a new link
        </Link>
      </div>
    );
  }

  const onSubmit = (values: ResetPasswordFormValues) => {
    confirmReset.mutate({ uid, token, ...values });
  };

  return (
    <form onSubmit={handleSubmit(onSubmit)} noValidate className="space-y-4">
      <div>
        <label
          htmlFor="new_password"
          className="mb-1 block text-sm font-medium text-slate-700 dark:text-slate-300"
        >
          New password
        </label>
        <input
          id="new_password"
          type="password"
          autoComplete="new-password"
          className="w-full rounded-md border border-slate-300 bg-white px-3 py-2 text-sm text-slate-900 outline-none transition focus:border-brand-500 focus:ring-2 focus:ring-brand-500/30 dark:border-slate-700 dark:bg-slate-800 dark:text-slate-100"
          {...register('new_password', {
            required: 'Password is required.',
            minLength: { value: 8, message: 'Password must be at least 8 characters.' },
          })}
        />
        {errors.new_password && (
          <p className="mt-1 text-xs text-red-600 dark:text-red-400">
            {errors.new_password.message}
          </p>
        )}
      </div>

      <div>
        <label
          htmlFor="new_password_confirm"
          className="mb-1 block text-sm font-medium text-slate-700 dark:text-slate-300"
        >
          Confirm new password
        </label>
        <input
          id="new_password_confirm"
          type="password"
          autoComplete="new-password"
          className="w-full rounded-md border border-slate-300 bg-white px-3 py-2 text-sm text-slate-900 outline-none transition focus:border-brand-500 focus:ring-2 focus:ring-brand-500/30 dark:border-slate-700 dark:bg-slate-800 dark:text-slate-100"
          {...register('new_password_confirm', {
            required: 'Please confirm your new password.',
            validate: (value) => value === newPassword || 'Passwords do not match.',
          })}
        />
        {errors.new_password_confirm && (
          <p className="mt-1 text-xs text-red-600 dark:text-red-400">
            {errors.new_password_confirm.message}
          </p>
        )}
      </div>

      {confirmReset.isError && (
        <p className="text-sm text-red-600 dark:text-red-400" role="alert">
          {extractAuthErrorMessage(confirmReset.error)}
        </p>
      )}

      <button
        type="submit"
        disabled={confirmReset.isPending}
        className="w-full rounded-md bg-brand-600 px-4 py-2 text-sm font-medium text-white transition hover:bg-brand-700 disabled:cursor-not-allowed disabled:opacity-60"
      >
        {confirmReset.isPending ? 'Resetting…' : 'Reset password'}
      </button>
    </form>
  );
}
