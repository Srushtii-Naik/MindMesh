import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query';
import { useNavigate } from 'react-router-dom';
import {
  listSessionsRequest,
  revokeAllSessionsRequest,
  revokeSessionRequest,
} from '@/features/auth/api';
import { useAuthStore } from '@/features/auth/store';
import { ROUTES } from '@/constants';

export const SESSIONS_QUERY_KEY = ['auth', 'sessions'] as const;

export function useSessions() {
  return useQuery({
    queryKey: SESSIONS_QUERY_KEY,
    queryFn: listSessionsRequest,
  });
}

export function useRevokeSession() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (sessionId: number) => revokeSessionRequest(sessionId),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: SESSIONS_QUERY_KEY });
    },
  });
}

export function useRevokeAllSessions() {
  const clearAuth = useAuthStore((state) => state.clearAuth);
  const navigate = useNavigate();

  return useMutation({
    mutationFn: revokeAllSessionsRequest,
    onSuccess: () => {
      // Revoking every session includes the current device's refresh token,
      // so the local session is cleared and the user is sent to log back in
      // — the same end state as the existing logout flow.
      clearAuth();
      navigate(ROUTES.LOGIN, { replace: true });
    },
  });
}
