import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query';
import { getSettingsRequest, updateSettingsRequest } from '@/features/auth/api';
import type { UserSettingsUpdatePayload } from '@/features/auth/types';

export const SETTINGS_QUERY_KEY = ['auth', 'settings'] as const;

export function useSettings() {
  return useQuery({
    queryKey: SETTINGS_QUERY_KEY,
    queryFn: getSettingsRequest,
  });
}

export function useUpdateSettings() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (payload: UserSettingsUpdatePayload) => updateSettingsRequest(payload),
    onSuccess: (settings) => {
      queryClient.setQueryData(SETTINGS_QUERY_KEY, settings);
    },
  });
}
