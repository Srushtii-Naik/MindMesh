import { describe, it, expect, vi, beforeEach } from 'vitest';
import { screen, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { renderWithProviders } from '@/test/renderWithProviders';
import { LoginForm } from '@/features/auth/components/LoginForm';
import { loginRequest } from '@/features/auth/api';
import { useAuthStore } from '@/features/auth/store';

vi.mock('@/features/auth/api', async (importOriginal) => {
  const actual = await importOriginal<typeof import('@/features/auth/api')>();
  return {
    ...actual,
    loginRequest: vi.fn(),
  };
});

describe('LoginForm', () => {
  beforeEach(() => {
    vi.clearAllMocks();
    useAuthStore.getState().clearAuth();
  });

  it('shows validation errors when submitted empty', async () => {
    const user = userEvent.setup();
    renderWithProviders(<LoginForm />);

    await user.click(screen.getByRole('button', { name: /sign in/i }));

    expect(await screen.findByText('Email is required.')).toBeInTheDocument();
    expect(screen.getByText('Password is required.')).toBeInTheDocument();
    expect(loginRequest).not.toHaveBeenCalled();
  });

  it('rejects a malformed email', async () => {
    const user = userEvent.setup();
    renderWithProviders(<LoginForm />);

    await user.type(screen.getByLabelText('Email'), 'not-an-email');
    await user.tab();

    expect(await screen.findByText('Enter a valid email address.')).toBeInTheDocument();
  });

  it('submits valid credentials and stores the session on success', async () => {
    vi.mocked(loginRequest).mockResolvedValue({
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
    renderWithProviders(<LoginForm />);

    await user.type(screen.getByLabelText('Email'), 'jane@example.com');
    await user.type(screen.getByLabelText('Password'), 'CorrectHorse123!');
    await user.click(screen.getByRole('button', { name: /sign in/i }));

    await waitFor(() => {
      expect(loginRequest).toHaveBeenCalledWith(
        { email: 'jane@example.com', password: 'CorrectHorse123!' },
        expect.anything()
      );
    });

    await waitFor(() => {
      expect(useAuthStore.getState().isAuthenticated).toBe(true);
    });
    expect(useAuthStore.getState().user?.email).toBe('jane@example.com');
  });

  it('displays a server-provided error message on failed login', async () => {
    const { AxiosError, AxiosHeaders } = await import('axios');
    vi.mocked(loginRequest).mockRejectedValue(
      new AxiosError('Request failed', 'ERR_BAD_REQUEST', undefined, undefined, {
        status: 401,
        statusText: 'Unauthorized',
        headers: {},
        config: { headers: new AxiosHeaders() },
        data: { detail: 'No active account found with the given credentials' },
      })
    );

    const user = userEvent.setup();
    renderWithProviders(<LoginForm />);

    await user.type(screen.getByLabelText('Email'), 'jane@example.com');
    await user.type(screen.getByLabelText('Password'), 'WrongPassword!');
    await user.click(screen.getByRole('button', { name: /sign in/i }));

    expect(
      await screen.findByText('No active account found with the given credentials')
    ).toBeInTheDocument();
  });
});
