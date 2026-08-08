import { useMutation, type UseMutationResult } from '@tanstack/react-query';
import { useNavigate } from 'react-router-dom';
import { loginRequest } from '@/features/auth/api';
import { useAuthStore } from '@/features/auth/store';
import type { AuthResponse, LoginPayload } from '@/features/auth/types';
import { ROUTES } from '@/constants';

export function useLogin(): UseMutationResult<AuthResponse, unknown, LoginPayload> {
  const setAuth = useAuthStore((state) => state.setAuth);
  const navigate = useNavigate();

  return useMutation({
    mutationFn: loginRequest,
    onSuccess: (data) => {
      setAuth(data.user, { access: data.access, refresh: data.refresh });
      navigate(ROUTES.HOME, { replace: true });
    },
  });
}
