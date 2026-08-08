import { useMutation, type UseMutationResult } from '@tanstack/react-query';
import { useNavigate } from 'react-router-dom';
import { googleLoginRequest } from '@/features/auth/api';
import { useAuthStore } from '@/features/auth/store';
import type { AuthResponse, GoogleAuthPayload } from '@/features/auth/types';
import { ROUTES } from '@/constants';

export function useGoogleLogin(): UseMutationResult<AuthResponse, unknown, GoogleAuthPayload> {
  const setAuth = useAuthStore((state) => state.setAuth);
  const navigate = useNavigate();

  return useMutation({
    mutationFn: googleLoginRequest,
    onSuccess: (data) => {
      setAuth(data.user, { access: data.access, refresh: data.refresh });
      navigate(ROUTES.HOME, { replace: true });
    },
  });
}
