import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest';
import { screen, waitFor } from '@testing-library/react';
import { renderWithProviders } from '@/test/renderWithProviders';
import { GoogleSignInButton } from '@/features/auth/components/GoogleSignInButton';

const originalEnv = { ...import.meta.env };

function mockGoogleGlobal() {
  const initialize = vi.fn();
  const renderButton = vi.fn();
  window.google = { accounts: { id: { initialize, renderButton } } };
  return { initialize, renderButton };
}

describe('GoogleSignInButton', () => {
  beforeEach(() => {
    vi.stubEnv('VITE_GOOGLE_OAUTH_CLIENT_ID', 'test-client-id.apps.googleusercontent.com');
    document
      .querySelectorAll('script[src="https://accounts.google.com/gsi/client"]')
      .forEach((el) => el.remove());
    delete (window as { google?: unknown }).google;
  });

  afterEach(() => {
    vi.unstubAllEnvs();
    Object.assign(import.meta.env, originalEnv);
  });

  it('renders nothing when no client ID is configured', () => {
    vi.stubEnv('VITE_GOOGLE_OAUTH_CLIENT_ID', '');
    renderWithProviders(<GoogleSignInButton />);

    expect(screen.queryByTestId('google-signin-button')).not.toBeInTheDocument();
  });

  it('initializes Google Identity Services and renders the button once the script loads', async () => {
    const { initialize, renderButton } = mockGoogleGlobal();

    renderWithProviders(<GoogleSignInButton />);

    // The component appends a <script> tag; simulate the browser firing its
    // load event once the (mocked, already-available) SDK is "loaded".
    const script = document.querySelector<HTMLScriptElement>(
      'script[src="https://accounts.google.com/gsi/client"]'
    );
    script?.dispatchEvent(new Event('load'));

    await waitFor(() => {
      expect(initialize).toHaveBeenCalledWith(
        expect.objectContaining({ client_id: 'test-client-id.apps.googleusercontent.com' })
      );
    });
    expect(renderButton).toHaveBeenCalled();
  });
});
