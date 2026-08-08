import { useMutation, type UseMutationResult } from '@tanstack/react-query';
import { useNavigate } from 'react-router-dom';
import { confirmPasswordResetRequest, requestPasswordResetRequest } from '@/features/auth/api';
import type {
  PasswordResetConfirmPayload,
  PasswordResetRequestPayload,
} from '@/features/auth/types';
import { ROUTES } from '@/constants';

export function useRequestPasswordReset(): UseMutationResult<
  { detail: string },
  unknown,
  PasswordResetRequestPayload
> {
  return useMutation({ mutationFn: requestPasswordResetRequest });
}

export function useConfirmPasswordReset(): UseMutationResult<
  { detail: string },
  unknown,
  PasswordResetConfirmPayload
> {
  const navigate = useNavigate();

  return useMutation({
    mutationFn: confirmPasswordResetRequest,
    onSuccess: () => {
      // The backend blacklists all existing sessions on a successful reset,
      // so the user is sent to log in fresh with the new password.
      navigate(ROUTES.LOGIN, { replace: true });
    },
  });
}
