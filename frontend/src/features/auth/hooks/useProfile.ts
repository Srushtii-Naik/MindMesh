import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query';
import { getProfileRequest, updateProfileRequest } from '@/features/auth/api';
import { useAuthStore } from '@/features/auth/store';
import type { UserProfileUpdatePayload } from '@/features/auth/types';

export const PROFILE_QUERY_KEY = ['auth', 'profile'] as const;

export function useProfile() {
  return useQuery({
    queryKey: PROFILE_QUERY_KEY,
    queryFn: getProfileRequest,
  });
}

export function useUpdateProfile() {
  const queryClient = useQueryClient();
  const updateStoredUser = useAuthStore((state) => state.updateUser);

  return useMutation({
    mutationFn: (payload: UserProfileUpdatePayload) => updateProfileRequest(payload),
    onSuccess: (profile) => {
      queryClient.setQueryData(PROFILE_QUERY_KEY, profile);
      // Keep the lightweight user object in the auth store (used for
      // greetings/etc. elsewhere in the app) in sync with the full profile.
      updateStoredUser({ full_name: profile.full_name });
    },
  });
}
