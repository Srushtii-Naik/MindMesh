import { describe, it, expect, vi, beforeEach } from 'vitest';
import { screen, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { renderWithProviders } from '@/test/renderWithProviders';
import { RegisterForm } from '@/features/auth/components/RegisterForm';
import { registerRequest } from '@/features/auth/api';
import { useAuthStore } from '@/features/auth/store';

vi.mock('@/features/auth/api', async (importOriginal) => {
  const actual = await importOriginal<typeof import('@/features/auth/api')>();
  return {
    ...actual,
    registerRequest: vi.fn(),
  };
});

describe('RegisterForm', () => {
  beforeEach(() => {
    vi.clearAllMocks();
    useAuthStore.getState().clearAuth();
  });

  it('rejects mismatched passwords without calling the API', async () => {
    const user = userEvent.setup();
    renderWithProviders(<RegisterForm />);

    await user.type(screen.getByLabelText('Full name'), 'Jane Doe');
    await user.type(screen.getByLabelText('Email'), 'jane@example.com');
    await user.type(screen.getByLabelText('Password'), 'Str0ng!Passw0rd');
    await user.type(screen.getByLabelText('Confirm password'), 'Different!Passw0rd');
    await user.click(screen.getByRole('button', { name: /create account/i }));

    expect(await screen.findByText('Passwords do not match.')).toBeInTheDocument();
    expect(registerRequest).not.toHaveBeenCalled();
  });

  it('rejects a password under 8 characters', async () => {
    const user = userEvent.setup();
    renderWithProviders(<RegisterForm />);

    await user.type(screen.getByLabelText('Password'), 'short');
    await user.tab();

    expect(await screen.findByText('Password must be at least 8 characters.')).toBeInTheDocument();
  });

  it('submits valid registration data and stores the session', async () => {
    vi.mocked(registerRequest).mockResolvedValue({
      access: 'access-token',
      refresh: 'refresh-token',
      user: {
        id: 'user-1',
        email: 'jane@example.com',
        full_name: 'Jane Doe',
        created_at: '2026-01-01T00:00:00Z',
      },
    });

    const user = userEvent.setup();
    renderWithProviders(<RegisterForm />);

    await user.type(screen.getByLabelText('Full name'), 'Jane Doe');
    await user.type(screen.getByLabelText('Email'), 'jane@example.com');
    await user.type(screen.getByLabelText('Password'), 'Str0ng!Passw0rd');
    await user.type(screen.getByLabelText('Confirm password'), 'Str0ng!Passw0rd');
    await user.click(screen.getByRole('button', { name: /create account/i }));

    await waitFor(() => {
      expect(registerRequest).toHaveBeenCalledWith(
        {
          full_name: 'Jane Doe',
          email: 'jane@example.com',
          password: 'Str0ng!Passw0rd',
          password_confirm: 'Str0ng!Passw0rd',
        },
        expect.anything()
      );
    });

    await waitFor(() => {
      expect(useAuthStore.getState().isAuthenticated).toBe(true);
    });
  });
});
