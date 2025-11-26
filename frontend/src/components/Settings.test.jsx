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

  it('shows loaded values and keeps key input empty', async () => {
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
    expect(screen.getByLabelText('OpenRouter Base URL').value).toBe('https://example.com');
    expect(screen.getByLabelText('Chairman Model').value).toBe('boss');
  });

  it('validates models before saving', async () => {
    api.getSettings.mockResolvedValue({
      openrouter_api_key: null,
      openrouter_api_url: 'https://example.com',
      council_models: [],
      chairman_model: 'boss',
    });

    render(<Settings onClose={() => {}} />);

    await screen.findByDisplayValue('https://example.com');
    fireEvent.click(screen.getByRole('button', { name: /save settings/i }));

    expect(await screen.findByRole('alert')).toHaveTextContent('Add at least one council model');
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
    fireEvent.click(screen.getByText('Test Connection'));

    await waitFor(() => {
      expect(api.testSettings).toHaveBeenCalledWith({
        openrouter_api_key: 'sk-test',
        openrouter_api_url: 'https://example.com',
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

    await screen.findByDisplayValue('https://example.com');
    await userEvent.type(screen.getByLabelText('OpenRouter API Key'), 'sk-newkey');
    await userEvent.type(screen.getByLabelText('Council Models (one per line)'), '\nmodel-b');
    await userEvent.clear(screen.getByLabelText('Chairman Model'));
    await userEvent.type(screen.getByLabelText('Chairman Model'), 'boss');

    fireEvent.click(screen.getByRole('button', { name: /save settings/i }));

    await waitFor(() => {
      expect(api.updateSettings).toHaveBeenCalledWith({
        openrouter_api_key: 'sk-newkey',
        openrouter_api_url: 'https://example.com',
        council_models: ['model-a', 'model-b'],
        chairman_model: 'boss',
      });
    });
    expect(screen.getByLabelText('OpenRouter API Key').value).toBe('');
    expect(await screen.findByText('Settings saved.')).toBeInTheDocument();
  });

  it('shows load error message', async () => {
    api.getSettings.mockRejectedValue(new Error('load failed'));
    render(<Settings onClose={() => {}} />);
    expect(await screen.findByRole('alert')).toHaveTextContent('load failed');
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
    await screen.findByDisplayValue('https://example.com');
    fireEvent.click(screen.getAllByText('Test Connection')[0]);
    expect(await screen.findByTestId('test-failure')).toHaveTextContent('bad key');
  });
});
