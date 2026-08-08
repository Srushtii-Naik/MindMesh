import { useMutation, type UseMutationResult } from '@tanstack/react-query';
import { useNavigate } from 'react-router-dom';
import { registerRequest } from '@/features/auth/api';
import { useAuthStore } from '@/features/auth/store';
import type { AuthResponse, RegisterPayload } from '@/features/auth/types';
import { ROUTES } from '@/constants';

export function useRegister(): UseMutationResult<AuthResponse, unknown, RegisterPayload> {
  const setAuth = useAuthStore((state) => state.setAuth);
  const navigate = useNavigate();

  return useMutation({
    mutationFn: registerRequest,
    onSuccess: (data) => {
      // Registration issues a token pair immediately (ARCHITECTURE.md Section 5),
      // so a new user lands straight in the app rather than being sent to log in again.
      setAuth(data.user, { access: data.access, refresh: data.refresh });
      navigate(ROUTES.HOME, { replace: true });
    },
  });
}
