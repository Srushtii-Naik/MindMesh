import { useMutation, type UseMutationResult } from '@tanstack/react-query';
import { useNavigate } from 'react-router-dom';
import { logoutRequest } from '@/features/auth/api';
import { useAuthStore } from '@/features/auth/store';
import { ROUTES } from '@/constants';

export function useLogout(): UseMutationResult<void, unknown, void> {
  const refreshToken = useAuthStore((state) => state.refreshToken);
  const clearAuth = useAuthStore((state) => state.clearAuth);
  const navigate = useNavigate();

  return useMutation({
    mutationFn: async () => {
      if (refreshToken) {
        await logoutRequest(refreshToken);
      }
    },
    // Clear local session state regardless of whether the server call
    // succeeds — an expired/invalid refresh token shouldn't trap the user
    // in a logged-in-looking state they can't escape.
    onSettled: () => {
      clearAuth();
      navigate(ROUTES.LOGIN, { replace: true });
    },
  });
}
