import { RegisterForm } from '@/features/auth/components/RegisterForm';

export function RegisterPage() {
  return (
    <div>
      <h2 className="mb-6 text-lg font-semibold text-slate-900 dark:text-slate-100">
        Create your account
      </h2>
      <RegisterForm />
    </div>
  );
}
