import { LoginForm } from '@/features/auth/components/LoginForm';

export function LoginPage() {
  return (
    <div>
      <h2 className="mb-6 text-lg font-semibold text-slate-900 dark:text-slate-100">
        Sign in to your account
      </h2>
      <LoginForm />
    </div>
  );
}
