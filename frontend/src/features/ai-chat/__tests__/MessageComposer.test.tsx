import { describe, it, expect, vi } from 'vitest';
import { screen, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { renderWithProviders } from '@/test/renderWithProviders';
import { MessageComposer } from '@/features/ai-chat/components/MessageComposer';
import type { Message } from '@/features/ai-chat/types';

const { sendMessageRequest } = vi.hoisted(() => ({
  sendMessageRequest: vi.fn(),
}));

vi.mock('@/features/ai-chat/api', async () => {
  const actual =
    await vi.importActual<typeof import('@/features/ai-chat/api')>('@/features/ai-chat/api');
  return { ...actual, sendMessageRequest };
});

function makeAssistantMessage(overrides: Partial<Message> = {}): Message {
  return {
    id: 'assistant-1',
    role: 'assistant',
    content: 'Here is my reply.',
    created_at: '2026-01-01T00:00:00Z',
    ...overrides,
  };
}

describe('MessageComposer', () => {
  it('shows a validation message when submitted empty', async () => {
    const user = userEvent.setup();
    renderWithProviders(<MessageComposer conversationId="conv-1" />);

    await user.click(screen.getByRole('button', { name: /send/i }));

    expect(await screen.findByText('Type a message first.')).toBeInTheDocument();
    expect(sendMessageRequest).not.toHaveBeenCalled();
  });

  it('sends the typed message and clears the input on success', async () => {
    sendMessageRequest.mockResolvedValue(makeAssistantMessage());
    const user = userEvent.setup();

    renderWithProviders(<MessageComposer conversationId="conv-1" />);

    const textarea = screen.getByLabelText('Message');
    await user.type(textarea, 'What should I do today?');
    await user.click(screen.getByRole('button', { name: /send/i }));

    await waitFor(() =>
      expect(sendMessageRequest).toHaveBeenCalledWith('conv-1', {
        content: 'What should I do today?',
      })
    );
    await waitFor(() => expect(textarea).toHaveValue(''));
  });

  it('shows an error message when sending fails', async () => {
    sendMessageRequest.mockRejectedValue({
      isAxiosError: true,
      response: { data: { detail: 'The AI provider returned an empty response.' } },
    });
    const user = userEvent.setup();

    renderWithProviders(<MessageComposer conversationId="conv-1" />);

    await user.type(screen.getByLabelText('Message'), 'Hello?');
    await user.click(screen.getByRole('button', { name: /send/i }));

    expect(
      await screen.findByText('The AI provider returned an empty response.')
    ).toBeInTheDocument();
  });
});
