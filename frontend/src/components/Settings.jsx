import { useEffect, useState } from 'react';
import { api } from '../api';
import './Settings.css';

const DEFAULTS = {
  openrouter_api_url: 'https://openrouter.ai/api/v1/chat/completions',
  council_models: [
    'openai/gpt-5.1',
    'google/gemini-3-pro-preview',
    'anthropic/claude-sonnet-4.5',
    'x-ai/grok-4',
  ],
  chairman_model: 'google/gemini-3-pro-preview',
};

export default function Settings({ onClose }) {
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [testing, setTesting] = useState(false);
  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');
  const [testResult, setTestResult] = useState(null);
  const [maskedKey, setMaskedKey] = useState('');
  const [form, setForm] = useState({ openrouter_api_key: '' });
  const [presets, setPresets] = useState(DEFAULTS);

  useEffect(() => {
    const load = async () => {
      try {
        const data = await api.getSettings();
        setMaskedKey(data.openrouter_api_key || '');
        setPresets({
          openrouter_api_url: data.openrouter_api_url || DEFAULTS.openrouter_api_url,
          council_models: data.council_models?.length ? data.council_models : DEFAULTS.council_models,
          chairman_model: data.chairman_model || DEFAULTS.chairman_model,
        });
      } catch (e) {
        setError(e.message || 'Failed to load settings');
        setPresets(DEFAULTS);
      } finally {
        setLoading(false);
      }
    };
    load();
  }, []);

  const clearMessages = () => {
    setError('');
    setSuccess('');
    setTestResult(null);
  };

  const handleChange = (field) => (e) => {
    clearMessages();
    setForm((prev) => ({ ...prev, [field]: e.target.value }));
  };

  const handleSave = async (e) => {
    e.preventDefault();
    setSaving(true);
    clearMessages();

    const key = form.openrouter_api_key.trim();
    if (!key) {
      setSaving(false);
      setError('Enter your OpenRouter API key');
      return;
    }

    try {
      const saved = await api.updateSettings({ openrouter_api_key: key });
      setSuccess('API key saved.');
      setMaskedKey(saved.openrouter_api_key || maskedKey);
      setForm({ openrouter_api_key: '' });
    } catch (e) {
      setError(e.message || 'Failed to save settings');
    } finally {
      setSaving(false);
    }
  };

  const handleTest = async () => {
    setTesting(true);
    clearMessages();

    const payload = {
      openrouter_api_url: presets.openrouter_api_url,
    };

    if (form.openrouter_api_key.trim()) {
      payload.openrouter_api_key = form.openrouter_api_key.trim();
    }

    try {
      const result = await api.testSettings(payload);
      setTestResult({ ok: true, model_count: result.model_count });
      setSuccess(`Connection OK — found ${result.model_count} models.`);
    } catch (e) {
      setError(e.message || 'Connection test failed');
      setTestResult({ ok: false, message: e.message });
    } finally {
      setTesting(false);
    }
  };

  if (loading) {
    return (
      <div className="settings" data-testid="settings-panel">
        <div className="settings-header">
          <div>
            <h2>Settings</h2>
            <p className="settings-subtitle">Loading your OpenRouter preferences…</p>
          </div>
          <div className="settings-actions">
            <button className="secondary-btn" disabled>
              Back to Chat
            </button>
          </div>
        </div>
        <div className="settings-card skeleton">
          <div className="skeleton-block w-60" />
          <div className="skeleton-block w-90" />
          <div className="skeleton-block w-50" />
        </div>
      </div>
    );
  }

  return (
    <div className="settings" data-testid="settings-panel">
      <div className="settings-header">
        <div>
          <h2>Settings</h2>
          <p className="settings-subtitle">
            Just drop in your OpenRouter API key. We&apos;ll use our recommended endpoint and default model roster.
          </p>
        </div>
        <div className="settings-actions header-actions">
          <button className="secondary-btn" onClick={onClose}>
            Back to Chat
          </button>
        </div>
      </div>

      <form className="settings-card" onSubmit={handleSave} aria-label="OpenRouter settings form">
        <div className="alert-region" aria-live="polite">
          {error && <div className="settings-alert error" role="alert">{error}</div>}
          {success && <div className="settings-alert success" role="status">{success}</div>}
        </div>

        <div className="field">
          <label htmlFor="openrouter_api_key">OpenRouter API Key</label>
          <input
            id="openrouter_api_key"
            type="password"
            value={form.openrouter_api_key}
            onChange={handleChange('openrouter_api_key')}
            placeholder={maskedKey ? 'Saved key on file' : 'sk-or-v1-...'}
            autoComplete="off"
          />
          <div className="field-hint">
            Stored only on this device. You can create or view keys on your OpenRouter dashboard.
          </div>
        </div>

        <div className="preset-panel" aria-label="Preset OpenRouter settings">
          <div className="preset-header">Everything else is preconfigured</div>
          <div className="preset-grid">
            <div className="preset-item">
              <div className="preset-label">Endpoint</div>
              <code className="preset-value" data-testid="base-url-value">
                {presets.openrouter_api_url}
              </code>
              <div className="preset-hint">From OpenRouter docs (chat completions).</div>
            </div>
            <div className="preset-item">
              <div className="preset-label">Council models</div>
              <div className="chip-row">
                {presets.council_models.map((model) => (
                  <span className="chip" key={model}>
                    {model}
                  </span>
                ))}
              </div>
              {!presets.council_models.length && (
                <div className="preset-hint">Using defaults from config.</div>
              )}
            </div>
            <div className="preset-item">
              <div className="preset-label">Chair model</div>
              {presets.chairman_model ? (
                <span className="chip chip-primary">{presets.chairman_model}</span>
              ) : (
                <div className="preset-hint">Using defaults from config.</div>
              )}
            </div>
          </div>
        </div>

        <div className="settings-actions form-actions">
          <button type="submit" className="primary-btn" disabled={saving}>
            {saving ? 'Saving…' : 'Save API Key'}
          </button>
          <button
            type="button"
            className="secondary-btn"
            onClick={handleTest}
            disabled={testing}
          >
            {testing ? 'Testing…' : 'Test Connection'}
          </button>
        </div>
      </form>

      {testResult && (
        <div className="settings-card subtle">
          {testResult.ok ? (
            <div data-testid="test-success">
              Connection successful. Models available: {testResult.model_count}.
            </div>
          ) : (
            <div className="settings-alert error" role="alert" data-testid="test-failure">
              Connection failed: {testResult.message}
            </div>
          )}
        </div>
      )}

      <div className="settings-footer actions-bottom">
        <button className="secondary-btn" onClick={onClose}>
          Back to Chat
        </button>
      </div>
    </div>
  );
}
