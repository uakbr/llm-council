import { render, screen } from '@testing-library/react';
import Sidebar from './Sidebar';

describe('Sidebar', () => {
  it('highlights active conversation', () => {
    const conversations = [
      { id: 'c1', title: 'One', message_count: 1 },
      { id: 'c2', title: 'Two', message_count: 0 },
    ];

    render(
      <Sidebar
        conversations={conversations}
        currentConversationId="c2"
        onSelectConversation={() => {}}
        onNewConversation={() => {}}
      />
    );

    const active = screen.getByText('Two').closest('.conversation-item');
    expect(active).toHaveClass('active');
  });

  it('shows empty state when no conversations', () => {
    render(
      <Sidebar
        conversations={[]}
        currentConversationId={null}
        onSelectConversation={() => {}}
        onNewConversation={() => {}}
      />
    );

    expect(screen.getByText('No conversations yet')).toBeInTheDocument();
  });
});
