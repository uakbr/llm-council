import { render, screen, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { vi } from 'vitest';

const {
  mockListConversations,
  mockCreateConversation,
  mockGetConversation,
  mockSendMessageStream,
} = vi.hoisted(() => ({
  mockListConversations: vi.fn().mockResolvedValue([]),
  mockCreateConversation: vi.fn().mockResolvedValue({
    id: 'c1',
    created_at: 'now',
    message_count: 0,
  }),
  mockGetConversation: vi.fn().mockResolvedValue({
    id: 'c1',
    created_at: 'now',
    title: 'New Conversation',
    messages: [],
  }),
  mockSendMessageStream: vi.fn(),
}));

vi.mock('./api', () => ({
  api: {
    listConversations: mockListConversations,
    createConversation: mockCreateConversation,
    getConversation: mockGetConversation,
    sendMessageStream: (...args) => mockSendMessageStream(...args),
    sendMessage: vi.fn(),
  },
}));

import App, { appendConversationMessages, updateLatestAssistant } from './App';

describe('state helper functions', () => {
  beforeEach(() => {
    mockListConversations.mockClear();
    mockCreateConversation.mockClear();
    mockGetConversation.mockClear();
    mockSendMessageStream.mockReset();
  });

  const baseConversation = {
    id: 'c1',
    messages: [
      { role: 'user', content: 'hi' },
      {
        role: 'assistant',
        stage1: null,
        stage2: null,
        stage3: null,
        metadata: null,
        loading: { stage1: false, stage2: false, stage3: false },
      },
    ],
  };

  it('appends messages defensively', () => {
    const result = appendConversationMessages(baseConversation, [
      { role: 'user', content: 'next' },
    ]);
    expect(result.messages).toHaveLength(3);
    expect(result.messages[2].content).toBe('next');
  });

  it('returns original conversation when ids mismatch', () => {
    const updated = updateLatestAssistant(baseConversation, 'other', (msg) => ({
      ...msg,
      stage1: ['x'],
    }));
    expect(updated).toBe(baseConversation);
  });

  it('updates last assistant immutably', () => {
    const updated = updateLatestAssistant(baseConversation, 'c1', (msg) => ({
      ...msg,
      stage2: ['rank'],
      loading: { ...msg.loading, stage2: true },
    }));
    // original untouched
    expect(baseConversation.messages[1].stage2).toBeNull();
    // updated applied
    expect(updated.messages[1].stage2).toEqual(['rank']);
    expect(updated.messages[1].loading.stage2).toBe(true);
  });

  it('runs sendMessageStream flow and applies stage data', async () => {
    const user = userEvent.setup();

    mockSendMessageStream.mockImplementation(async (_id, _content, onEvent) => {
      const stage1 = [{ model: 'openai/gpt', response: 'r1' }];
      const stage2 = [{ model: 'openai/gpt', ranking: 'FINAL RANKING:\n1. Response A', parsed_ranking: ['Response A'] }];
      const metadata = {
        label_to_model: { 'Response A': 'openai/gpt' },
        aggregate_rankings: [{ model: 'openai/gpt', average_rank: 1, rankings_count: 1 }],
      };
      const stage3 = { model: 'chair', response: 'final' };
      onEvent('stage1_start', {});
      onEvent('stage1_complete', { data: stage1 });
      onEvent('stage2_start', {});
      onEvent('stage2_complete', { data: stage2, metadata });
      onEvent('stage3_start', {});
      onEvent('stage3_complete', { data: stage3 });
      onEvent('title_complete', { data: {} });
      onEvent('error', { message: 'oops' });
      onEvent('complete', {});
    });

    render(<App />);

    const newBtn = await screen.findByText('+ New Conversation');
    await user.click(newBtn);

    // Wait for conversation to load
    await waitFor(() => expect(mockGetConversation).toHaveBeenCalled());

    const textarea = await screen.findByPlaceholderText(/Ask your question/i);
    await user.type(textarea, 'test question');
    await user.keyboard('{Enter}');

    expect(mockSendMessageStream).toHaveBeenCalledWith(
      'c1',
      'test question',
      expect.any(Function)
    );

    await screen.findByText('Stage 1: Individual Responses');
    await screen.findByText('Stage 2: Peer Rankings');
    await screen.findByText('Stage 3: Final Council Answer');
    await screen.findByText(/Aggregate Rankings/i);
  });

  it('rolls back optimistic messages when stream fails', async () => {
    const user = userEvent.setup();
    mockSendMessageStream.mockImplementation(async () => {
      throw new Error('boom');
    });

    render(<App />);

    const newBtn = await screen.findByText('+ New Conversation');
    await user.click(newBtn);
    await waitFor(() => expect(mockGetConversation).toHaveBeenCalled());

    const textarea = await screen.findByPlaceholderText(/Ask your question/i);
    await user.type(textarea, 'fail case');
    await user.keyboard('{Enter}');

    await waitFor(() => expect(mockSendMessageStream).toHaveBeenCalled());
    expect(await screen.findByText('Start a conversation')).toBeInTheDocument();
  });
});
