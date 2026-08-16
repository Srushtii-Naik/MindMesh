import { describe, it, expect, vi } from 'vitest';
import { screen, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { renderWithProviders } from '@/test/renderWithProviders';
import { ConversationList } from '@/features/ai-chat/components/ConversationList';
import type { Conversation } from '@/features/ai-chat/types';

const { listConversationsRequest, createConversationRequest, deleteConversationRequest } =
  vi.hoisted(() => ({
    listConversationsRequest: vi.fn(),
    createConversationRequest: vi.fn(),
    deleteConversationRequest: vi.fn(),
  }));

vi.mock('@/features/ai-chat/api', async () => {
  const actual =
    await vi.importActual<typeof import('@/features/ai-chat/api')>('@/features/ai-chat/api');
  return {
    ...actual,
    listConversationsRequest,
    createConversationRequest,
    deleteConversationRequest,
  };
});

function makeConversation(overrides: Partial<Conversation> = {}): Conversation {
  return {
    id: 'conv-1',
    title: 'Getting organized',
    created_at: '2026-01-01T00:00:00Z',
    updated_at: '2026-01-01T00:00:00Z',
    ...overrides,
  };
}

describe('ConversationList', () => {
  it('shows an empty state when there are no conversations', async () => {
    listConversationsRequest.mockResolvedValue([]);

    renderWithProviders(<ConversationList activeConversationId={undefined} onSelect={vi.fn()} />);

    await waitFor(() =>
      expect(screen.getByText('No conversations yet — start one above.')).toBeInTheDocument()
    );
  });

  it('renders each conversation returned by the query', async () => {
    listConversationsRequest.mockResolvedValue([
      makeConversation({ id: '1', title: 'Planning my week' }),
      makeConversation({ id: '2', title: 'Grocery run' }),
    ]);

    renderWithProviders(<ConversationList activeConversationId={undefined} onSelect={vi.fn()} />);

    expect(await screen.findByText('Planning my week')).toBeInTheDocument();
    expect(screen.getByText('Grocery run')).toBeInTheDocument();
  });

  it('calls onSelect with the new conversation id after creating one', async () => {
    listConversationsRequest.mockResolvedValue([]);
    createConversationRequest.mockResolvedValue(makeConversation({ id: 'new-conv' }));
    const onSelect = vi.fn();
    const user = userEvent.setup();

    renderWithProviders(<ConversationList activeConversationId={undefined} onSelect={onSelect} />);

    await user.click(await screen.findByText('New conversation'));

    await waitFor(() => expect(onSelect).toHaveBeenCalledWith('new-conv'));
  });

  it('shows an error state when the request fails', async () => {
    listConversationsRequest.mockRejectedValue(new Error('network error'));

    renderWithProviders(<ConversationList activeConversationId={undefined} onSelect={vi.fn()} />);

    await waitFor(() =>
      expect(screen.getByText("Couldn't load your conversations.")).toBeInTheDocument()
    );
  });
});
