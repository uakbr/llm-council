import { useState, useEffect } from 'react';
import Sidebar from './components/Sidebar';
import ChatInterface from './components/ChatInterface';
import Settings from './components/Settings';
import { api } from './api';
import './App.css';

export function appendConversationMessages(conversation, newMessages) {
  if (!conversation) return conversation;
  const existing = Array.isArray(conversation.messages) ? conversation.messages : [];
  return {
    ...conversation,
    messages: [...existing, ...newMessages],
  };
}

export function updateLatestAssistant(conversation, conversationId, updateFn) {
  if (!conversation || conversation.id !== conversationId) return conversation;
  const messages = Array.isArray(conversation.messages) ? conversation.messages : [];
  if (messages.length === 0) return conversation;

  const lastIndex = messages.length - 1;
  const lastMsg = messages[lastIndex];
  const nextMsg = updateFn({
    ...lastMsg,
    loading: { ...(lastMsg.loading || {}) },
  }) || lastMsg;

  const nextMessages = [...messages];
  nextMessages[lastIndex] = nextMsg;
  return { ...conversation, messages: nextMessages };
}

function App() {
  const [conversations, setConversations] = useState([]);
  const [currentConversationId, setCurrentConversationId] = useState(null);
  const [currentConversation, setCurrentConversation] = useState(null);
  const [isLoading, setIsLoading] = useState(false);
  const [activeView, setActiveView] = useState('chat'); // 'chat' | 'settings'

  // Load conversations on mount
  useEffect(() => {
    loadConversations();
  }, []);

  // Load conversation details when selected
  useEffect(() => {
    if (currentConversationId) {
      loadConversation(currentConversationId);
    }
  }, [currentConversationId]);

  const loadConversations = async () => {
    try {
      const convs = await api.listConversations();
      setConversations(convs);
    } catch (error) {
      console.error('Failed to load conversations:', error);
    }
  };

  const loadConversation = async (id) => {
    try {
      const conv = await api.getConversation(id);
      setCurrentConversation(conv);
    } catch (error) {
      console.error('Failed to load conversation:', error);
    }
  };

  const handleNewConversation = async () => {
    try {
      const newConv = await api.createConversation();
      setConversations([
        { id: newConv.id, created_at: newConv.created_at, message_count: 0 },
        ...conversations,
      ]);
      setCurrentConversationId(newConv.id);
      setActiveView('chat');
    } catch (error) {
      console.error('Failed to create conversation:', error);
    }
  };

  const handleSelectConversation = (id) => {
    setCurrentConversationId(id);
    setActiveView('chat');
  };

  const handleSendMessage = async (content) => {
    if (!currentConversationId || !currentConversation) return;

    const streamConversationId = currentConversationId;
    setIsLoading(true);
    try {
      const userMessage = { role: 'user', content };
      const assistantMessage = {
        role: 'assistant',
        stage1: null,
        stage2: null,
        stage3: null,
        metadata: null,
        loading: {
          stage1: false,
          stage2: false,
          stage3: false,
        },
      };

      // Add user + assistant placeholder together
      setCurrentConversation((prev) =>
        appendConversationMessages(prev, [userMessage, assistantMessage])
      );

      await api.sendMessageStream(streamConversationId, content, (eventType, event) => {
        switch (eventType) {
          case 'stage1_start':
            setCurrentConversation((prev) =>
              updateLatestAssistant(prev, streamConversationId, (msg) => ({
                ...msg,
                loading: { ...msg.loading, stage1: true },
              }))
            );
            break;

          case 'stage1_complete':
            setCurrentConversation((prev) =>
              updateLatestAssistant(prev, streamConversationId, (msg) => ({
                ...msg,
                stage1: event.data,
                loading: { ...msg.loading, stage1: false },
              }))
            );
            break;

          case 'stage2_start':
            setCurrentConversation((prev) =>
              updateLatestAssistant(prev, streamConversationId, (msg) => ({
                ...msg,
                loading: { ...msg.loading, stage2: true },
              }))
            );
            break;

          case 'stage2_complete':
            setCurrentConversation((prev) =>
              updateLatestAssistant(prev, streamConversationId, (msg) => ({
                ...msg,
                stage2: event.data,
                metadata: event.metadata,
                loading: { ...msg.loading, stage2: false },
              }))
            );
            break;

          case 'stage3_start':
            setCurrentConversation((prev) =>
              updateLatestAssistant(prev, streamConversationId, (msg) => ({
                ...msg,
                loading: { ...msg.loading, stage3: true },
              }))
            );
            break;

          case 'stage3_complete':
            setCurrentConversation((prev) =>
              updateLatestAssistant(prev, streamConversationId, (msg) => ({
                ...msg,
                stage3: event.data,
                loading: { ...msg.loading, stage3: false },
              }))
            );
            break;

          case 'title_complete':
            loadConversations();
            break;

          case 'complete':
            loadConversations();
            setIsLoading(false);
            break;

          case 'error':
            console.error('Stream error:', event.message);
            setIsLoading(false);
            break;

          default:
            console.log('Unknown event type:', eventType);
        }
      });
    } catch (error) {
      console.error('Failed to send message:', error);
      setCurrentConversation((prev) => {
        if (!prev || !Array.isArray(prev.messages) || prev.messages.length < 2) return prev;
        return { ...prev, messages: prev.messages.slice(0, -2) };
      });
      setIsLoading(false);
    }
  };

  return (
    <div className="app">
      <Sidebar
        conversations={conversations}
        currentConversationId={currentConversationId}
        onSelectConversation={handleSelectConversation}
        onNewConversation={handleNewConversation}
        onOpenSettings={() => setActiveView('settings')}
        isSettingsOpen={activeView === 'settings'}
      />
      {activeView === 'settings' ? (
        <Settings onClose={() => setActiveView('chat')} />
      ) : (
        <ChatInterface
          conversation={currentConversation}
          onSendMessage={handleSendMessage}
          isLoading={isLoading}
        />
      )}
    </div>
  );
}

export default App;
