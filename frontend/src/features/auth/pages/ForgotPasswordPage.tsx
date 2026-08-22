import { ForgotPasswordForm } from '@/features/auth/components/ForgotPasswordForm';

export function ForgotPasswordPage() {
  return (
    <div>
      <h2 className="mb-6 text-lg font-semibold text-slate-900 dark:text-slate-100">
        Reset your password
      </h2>
      <ForgotPasswordForm />
    </div>
  );
}
