import { useEffect, useRef, useState } from 'react';
import { useGoogleLogin } from '@/features/auth/hooks';
import { extractAuthErrorMessage } from '@/features/auth/utils';

const GOOGLE_SCRIPT_SRC = 'https://accounts.google.com/gsi/client';

interface GoogleCredentialResponse {
  credential: string;
}

interface GoogleIdConfiguration {
  client_id: string;
  callback: (response: GoogleCredentialResponse) => void;
}

interface GoogleButtonConfiguration {
  type?: 'standard' | 'icon';
  theme?: 'outline' | 'filled_blue' | 'filled_black';
  size?: 'large' | 'medium' | 'small';
  width?: number;
  text?: 'signin_with' | 'signup_with' | 'continue_with';
}

interface GoogleAccountsId {
  initialize: (config: GoogleIdConfiguration) => void;
  renderButton: (parent: HTMLElement, options: GoogleButtonConfiguration) => void;
}

declare global {
  interface Window {
    google?: {
      accounts: {
        id: GoogleAccountsId;
      };
    };
  }
}

let scriptLoadPromise: Promise<void> | null = null;

function loadGoogleScript(): Promise<void> {
  if (window.google?.accounts?.id) {
    return Promise.resolve();
  }

  scriptLoadPromise ??= new Promise((resolve, reject) => {
    const existing = document.querySelector<HTMLScriptElement>(
      `script[src="${GOOGLE_SCRIPT_SRC}"]`
    );
    if (existing) {
      existing.addEventListener('load', () => resolve());
      existing.addEventListener('error', () => reject(new Error('Failed to load Google script.')));
      return;
    }

    const script = document.createElement('script');
    script.src = GOOGLE_SCRIPT_SRC;
    script.async = true;
    script.defer = true;
    script.onload = () => resolve();
    script.onerror = () => reject(new Error('Failed to load Google script.'));
    document.head.appendChild(script);
  });

  return scriptLoadPromise;
}

/**
 * Renders Google's own "Sign in with Google" button via Google Identity
 * Services (GIS). On credential receipt, hands the ID token to
 * `useGoogleLogin`, which POSTs it to /api/v1/auth/google/ and completes the
 * session the same way email/password login does.
 *
 * Silently renders nothing if no client ID is configured (e.g. local
 * development without Google credentials set up) rather than showing a
 * broken button.
 */
export function GoogleSignInButton() {
  const buttonContainerRef = useRef<HTMLDivElement>(null);
  const [loadError, setLoadError] = useState<string | null>(null);
  const googleLogin = useGoogleLogin();
  const clientId = import.meta.env.VITE_GOOGLE_OAUTH_CLIENT_ID;

  useEffect(() => {
    if (!clientId || !buttonContainerRef.current) {
      return;
    }

    let cancelled = false;

    loadGoogleScript()
      .then(() => {
        if (cancelled || !window.google || !buttonContainerRef.current) {
          return;
        }

        window.google.accounts.id.initialize({
          client_id: clientId,
          callback: (response) => {
            googleLogin.mutate({ id_token: response.credential });
          },
        });

        window.google.accounts.id.renderButton(buttonContainerRef.current, {
          type: 'standard',
          theme: 'outline',
          size: 'large',
          text: 'signin_with',
          width: 320,
        });
      })
      .catch(() => {
        if (!cancelled) {
          setLoadError('Google sign-in is unavailable right now.');
        }
      });

    return () => {
      cancelled = true;
    };
    // eslint-disable-next-line react-hooks/exhaustive-deps -- googleLogin.mutate is stable per mutation instance
  }, [clientId]);

  if (!clientId) {
    return null;
  }

  return (
    <div>
      <div ref={buttonContainerRef} data-testid="google-signin-button" />
      {loadError && <p className="mt-1 text-xs text-red-600 dark:text-red-400">{loadError}</p>}
      {googleLogin.isError && (
        <p className="mt-1 text-xs text-red-600 dark:text-red-400" role="alert">
          {extractAuthErrorMessage(googleLogin.error)}
        </p>
      )}
    </div>
  );
}
