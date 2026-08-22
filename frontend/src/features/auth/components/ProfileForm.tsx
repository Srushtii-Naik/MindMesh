import { useEffect } from 'react';
import { useForm } from 'react-hook-form';
import { useProfile, useUpdateProfile } from '@/features/auth/hooks';
import { extractAuthErrorMessage } from '@/features/auth/utils';
import type { UserProfileUpdatePayload } from '@/features/auth/types';

export function ProfileForm() {
  const { data: profile, isLoading, isError } = useProfile();
  const updateProfile = useUpdateProfile();

  const {
    register,
    handleSubmit,
    reset,
    formState: { errors, isDirty },
  } = useForm<UserProfileUpdatePayload>();

  useEffect(() => {
    if (profile) {
      reset({ full_name: profile.full_name });
    }
  }, [profile, reset]);

  if (isLoading) {
    return <p className="text-sm text-slate-500 dark:text-slate-400">Loading profile…</p>;
  }

  if (isError || !profile) {
    return (
      <p className="text-sm text-red-600 dark:text-red-400">Couldn&apos;t load your profile.</p>
    );
  }

  const onSubmit = (values: UserProfileUpdatePayload) => {
    updateProfile.mutate(values);
  };

  return (
    <form onSubmit={handleSubmit(onSubmit)} noValidate className="space-y-4">
      <div>
        <span className="mb-1 block text-sm font-medium text-slate-700 dark:text-slate-300">
          Email
        </span>
        <p className="text-sm text-slate-500 dark:text-slate-400">{profile.email}</p>
        {profile.auth_provider === 'google' && (
          <p className="mt-1 text-xs text-slate-400">Signed in with Google</p>
        )}
      </div>

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

      {updateProfile.isError && (
        <p className="text-sm text-red-600 dark:text-red-400" role="alert">
          {extractAuthErrorMessage(updateProfile.error)}
        </p>
      )}
      {updateProfile.isSuccess && (
        <p className="text-sm text-green-600 dark:text-green-400">Profile updated.</p>
      )}

      <button
        type="submit"
        disabled={!isDirty || updateProfile.isPending}
        className="rounded-md bg-brand-600 px-4 py-2 text-sm font-medium text-white transition hover:bg-brand-700 disabled:cursor-not-allowed disabled:opacity-60"
      >
        {updateProfile.isPending ? 'Saving…' : 'Save changes'}
      </button>
    </form>
  );
}
