import { describe, it, expect, vi } from 'vitest';
import { screen, waitFor } from '@testing-library/react';
import { renderWithProviders } from '@/test/renderWithProviders';
import { MessageList } from '@/features/ai-chat/components/MessageList';
import type { Message } from '@/features/ai-chat/types';

const { listMessagesRequest } = vi.hoisted(() => ({
  listMessagesRequest: vi.fn(),
}));

vi.mock('@/features/ai-chat/api', async () => {
  const actual =
    await vi.importActual<typeof import('@/features/ai-chat/api')>('@/features/ai-chat/api');
  return { ...actual, listMessagesRequest };
});

function makeMessage(overrides: Partial<Message> = {}): Message {
  return {
    id: 'message-1',
    role: 'user',
    content: 'Hello there',
    created_at: '2026-01-01T00:00:00Z',
    ...overrides,
  };
}

describe('MessageList', () => {
  it('prompts to start or pick a conversation when none is active', () => {
    renderWithProviders(<MessageList conversationId={undefined} />);

    expect(
      screen.getByText('Start a new conversation or pick one from the list to begin.')
    ).toBeInTheDocument();
  });

  it('shows an empty state when the conversation has no messages yet', async () => {
    listMessagesRequest.mockResolvedValue({ count: 0, next: null, previous: null, results: [] });

    renderWithProviders(<MessageList conversationId="conv-1" />);

    await waitFor(() =>
      expect(screen.getByText('Say hello to start the conversation.')).toBeInTheDocument()
    );
  });

  it('renders each message returned by the query', async () => {
    listMessagesRequest.mockResolvedValue({
      count: 2,
      next: null,
      previous: null,
      results: [
        makeMessage({ id: '1', role: 'user', content: 'What is on my plate today?' }),
        makeMessage({ id: '2', role: 'assistant', content: 'You have 2 tasks due today.' }),
      ],
    });

    renderWithProviders(<MessageList conversationId="conv-1" />);

    expect(await screen.findByText('What is on my plate today?')).toBeInTheDocument();
    expect(screen.getByText('You have 2 tasks due today.')).toBeInTheDocument();
  });

  it('shows an error state when the request fails', async () => {
    listMessagesRequest.mockRejectedValue(new Error('network error'));

    renderWithProviders(<MessageList conversationId="conv-1" />);

    await waitFor(() =>
      expect(screen.getByText("Couldn't load this conversation.")).toBeInTheDocument()
    );
  });
});
