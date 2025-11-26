import { render, screen, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { vi } from 'vitest';
import ChatInterface from './ChatInterface';

const baseConversation = {
  id: '1',
  messages: [
    { role: 'user', content: 'Hi there' },
    {
      role: 'assistant',
      stage1: null,
      stage2: null,
      stage3: null,
      metadata: null,
      loading: {},
    },
  ],
};

describe('ChatInterface', () => {
  it('shows welcome empty state when no conversation', () => {
    render(<ChatInterface conversation={null} onSendMessage={vi.fn()} isLoading={false} />);
    expect(screen.getByText(/welcome to llm council/i)).toBeInTheDocument();
  });

  it('submits message and clears input on success', async () => {
    const onSend = vi.fn().mockResolvedValue();
    render(<ChatInterface conversation={baseConversation} onSendMessage={onSend} isLoading={false} />);

    await userEvent.type(screen.getByPlaceholderText(/ask your question/i), 'hello{enter}');
    await waitFor(() => expect(onSend).toHaveBeenCalledWith('hello'));
    expect(screen.getByPlaceholderText(/ask your question/i).value).toBe('');
  });

  it('shows error when submission fails', async () => {
    const onSend = vi.fn().mockRejectedValue(new Error('boom'));
    render(<ChatInterface conversation={baseConversation} onSendMessage={onSend} isLoading={false} />);

    await userEvent.type(screen.getByPlaceholderText(/ask your question/i), 'oops{enter}');
    expect(await screen.findByRole('alert')).toHaveTextContent('boom');
  });
});
