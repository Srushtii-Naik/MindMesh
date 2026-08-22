import { describe, it, expect } from 'vitest';
import { AxiosError, AxiosHeaders } from 'axios';
import { extractAuthErrorMessage } from '@/features/auth/utils';

function makeAxiosError(data: unknown, status = 400): AxiosError {
  return new AxiosError('Request failed', 'ERR_BAD_REQUEST', undefined, undefined, {
    status,
    statusText: 'Bad Request',
    headers: {},
    config: { headers: new AxiosHeaders() },
    data,
  });
}

describe('extractAuthErrorMessage', () => {
  it('returns the detail message when present', () => {
    const error = makeAxiosError({ detail: 'Invalid credentials.', code: 'invalid' });
    expect(extractAuthErrorMessage(error)).toBe('Invalid credentials.');
  });

  it('returns the first field error when there is no detail field', () => {
    const error = makeAxiosError({ password_confirm: ['Passwords do not match.'] });
    expect(extractAuthErrorMessage(error)).toBe('Passwords do not match.');
  });

  it('falls back to a network error message when there is no response data', () => {
    const error = new AxiosError('Network Error', 'ERR_NETWORK');
    expect(extractAuthErrorMessage(error)).toMatch(/network/i);
  });

  it('falls back to a generic message for non-Axios errors', () => {
    expect(extractAuthErrorMessage(new Error('boom'))).toBe(
      'Something went wrong. Please try again.'
    );
  });

  it('falls back to a generic message when the error is not an Error at all', () => {
    expect(extractAuthErrorMessage('a string error')).toBe(
      'Something went wrong. Please try again.'
    );
  });
});
