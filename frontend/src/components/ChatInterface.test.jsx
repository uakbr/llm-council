import { render, screen } from '@testing-library/react';
import ChatInterface from './ChatInterface';

const baseConversation = {
  id: 'conv-1',
  messages: [{ role: 'user', content: 'hello' }],
};

describe('ChatInterface', () => {
  it('renders input form even when messages exist', () => {
    render(
      <ChatInterface
        conversation={baseConversation}
        onSendMessage={() => {}}
        isLoading={false}
      />
    );

    expect(
      screen.getByPlaceholderText(/Ask your question/i)
    ).toBeInTheDocument();
  });
});
