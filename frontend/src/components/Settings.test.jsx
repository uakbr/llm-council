import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { vi } from 'vitest';
import Settings from './Settings';
import { api } from '../api';

vi.mock('../api', () => ({
  api: {
    getSettings: vi.fn(),
    updateSettings: vi.fn(),
    testSettings: vi.fn(),
  },
}));

describe('Settings', () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  it('shows preset values and keeps key input empty', async () => {
    api.getSettings.mockResolvedValue({
      openrouter_api_key: '****1234',
      openrouter_api_url: 'https://example.com',
      council_models: ['m1', 'm2'],
      chairman_model: 'boss',
    });
    api.updateSettings.mockResolvedValue({});

    render(<Settings onClose={() => {}} />);

    await screen.findByTestId('settings-panel');
    expect(screen.getByLabelText('OpenRouter API Key').value).toBe('');
    expect(screen.getByTestId('base-url-value')).toHaveTextContent('https://example.com');
    expect(screen.getByText('m1')).toBeInTheDocument();
    expect(screen.getByText('boss')).toBeInTheDocument();
  });

  it('requires an API key before saving', async () => {
    api.getSettings.mockResolvedValue({
      openrouter_api_key: null,
      openrouter_api_url: 'https://example.com',
      council_models: ['m1'],
      chairman_model: 'boss',
    });

    render(<Settings onClose={() => {}} />);

    await screen.findByTestId('base-url-value');
    fireEvent.click(screen.getByRole('button', { name: /save api key/i }));

    expect(await screen.findByRole('alert')).toHaveTextContent('Enter your OpenRouter API key');
    expect(api.updateSettings).not.toHaveBeenCalled();
  });

  it('tests connection with overrides', async () => {
    api.getSettings.mockResolvedValue({
      openrouter_api_key: '****5678',
      openrouter_api_url: 'https://example.com',
      council_models: ['model-a'],
      chairman_model: 'chair',
    });
    api.testSettings.mockResolvedValue({ ok: true, model_count: 3 });

    render(<Settings onClose={() => {}} />);

    await screen.findByText('Settings');
    await userEvent.type(screen.getByLabelText('OpenRouter API Key'), 'sk-test');
    fireEvent.click(screen.getByRole('button', { name: /test connection/i }));

    await waitFor(() => {
      expect(api.testSettings).toHaveBeenCalledWith({
        openrouter_api_url: 'https://example.com',
        openrouter_api_key: 'sk-test',
      });
    });
    expect(await screen.findByTestId('test-success')).toBeInTheDocument();
  });

  it('saves settings with new key and clears the field', async () => {
    api.getSettings.mockResolvedValue({
      openrouter_api_key: '****1234',
      openrouter_api_url: 'https://example.com',
      council_models: ['model-a'],
      chairman_model: 'chair',
    });
    api.updateSettings.mockResolvedValue({ openrouter_api_key: '****9999' });

    render(<Settings onClose={() => {}} />);

    await screen.findByTestId('base-url-value');
    await userEvent.type(screen.getByLabelText('OpenRouter API Key'), 'sk-newkey');

    fireEvent.click(screen.getByRole('button', { name: /save api key/i }));

    await waitFor(() => {
      expect(api.updateSettings).toHaveBeenCalledWith({ openrouter_api_key: 'sk-newkey' });
    });
    expect(screen.getByLabelText('OpenRouter API Key').value).toBe('');
    expect(await screen.findByText('API key saved.')).toBeInTheDocument();
  });

  it('shows load error message and falls back to defaults', async () => {
    api.getSettings.mockRejectedValue(new Error('load failed'));
    render(<Settings onClose={() => {}} />);
    expect(await screen.findByRole('alert')).toHaveTextContent('load failed');
    expect(await screen.findByTestId('base-url-value')).toHaveTextContent('https://openrouter.ai/api/v1/chat/completions');
    expect(screen.getByText('openai/gpt-5.1')).toBeInTheDocument();
  });

  it('clears alerts when user edits key', async () => {
    api.getSettings.mockResolvedValue({
      openrouter_api_key: null,
      openrouter_api_url: 'https://example.com',
      council_models: ['m1'],
      chairman_model: 'boss',
    });
    render(<Settings onClose={() => {}} />);
    await screen.findByTestId('base-url-value');
    fireEvent.click(screen.getByRole('button', { name: /save api key/i }));
    expect(await screen.findByRole('alert')).toBeInTheDocument();
    await userEvent.type(screen.getByLabelText('OpenRouter API Key'), 'abc');
    expect(screen.queryByRole('alert')).not.toBeInTheDocument();
  });

  it('shows test connection failure', async () => {
    api.getSettings.mockResolvedValue({
      openrouter_api_key: null,
      openrouter_api_url: 'https://example.com',
      council_models: ['m1'],
      chairman_model: 'c1',
    });
    api.testSettings.mockRejectedValue(new Error('bad key'));
    render(<Settings onClose={() => {}} />);
    await screen.findByTestId('base-url-value');
    fireEvent.click(screen.getByRole('button', { name: /test connection/i }));
    expect(await screen.findByTestId('test-failure')).toHaveTextContent('bad key');
  });

  it('renders skeleton while loading', () => {
    api.getSettings.mockReturnValue(new Promise(() => {})); // keep pending to stay in loading state
    const { container } = render(<Settings onClose={() => {}} />);
    expect(container.querySelector('.skeleton-block')).toBeInTheDocument();
  });
});
