import { useEffect, useState } from 'react';
import { api } from '../api';
import './Settings.css';

function parseModels(text) {
  return text
    .split('\n')
    .map((line) => line.trim())
    .filter(Boolean);
}

export default function Settings({ onClose }) {
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [testing, setTesting] = useState(false);
  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');
  const [testResult, setTestResult] = useState(null);
  const [maskedKey, setMaskedKey] = useState('');
  const [form, setForm] = useState({
    openrouter_api_key: '',
    openrouter_api_url: '',
    council_models_text: '',
    chairman_model: '',
  });

  useEffect(() => {
    const load = async () => {
      try {
        const data = await api.getSettings();
        setMaskedKey(data.openrouter_api_key || '');
        setForm({
          openrouter_api_key: '',
          openrouter_api_url: data.openrouter_api_url || '',
          council_models_text: (data.council_models || []).join('\n'),
          chairman_model: data.chairman_model || '',
        });
      } catch (e) {
        setError(e.message || 'Failed to load settings');
      } finally {
        setLoading(false);
      }
    };
    load();
  }, []);

  const handleChange = (field) => (e) => {
    setForm((prev) => ({ ...prev, [field]: e.target.value }));
  };

  const handleSave = async (e) => {
    e.preventDefault();
    setSaving(true);
    setSuccess('');
    setError('');

    const councilModels = parseModels(form.council_models_text);
    if (councilModels.length === 0) {
      setSaving(false);
      setError('Add at least one council model.');
      return;
    }

    const payload = {
      openrouter_api_url: form.openrouter_api_url.trim(),
      council_models: councilModels,
      chairman_model: form.chairman_model.trim(),
    };

    if (form.openrouter_api_key.trim() !== '') {
      payload.openrouter_api_key = form.openrouter_api_key.trim();
    }

    try {
      const saved = await api.updateSettings(payload);
      setSuccess('Settings saved.');
      setMaskedKey(saved.openrouter_api_key || maskedKey);
      // Clear the key field after save so we don't resend redacted text
      setForm((prev) => ({ ...prev, openrouter_api_key: '' }));
    } catch (e) {
      setError(e.message || 'Failed to save settings');
    } finally {
      setSaving(false);
    }
  };

  const handleTest = async () => {
    setTesting(true);
    setError('');
    setSuccess('');
    setTestResult(null);

    const payload = {};
    if (form.openrouter_api_key.trim()) {
      payload.openrouter_api_key = form.openrouter_api_key.trim();
    }
    if (form.openrouter_api_url.trim()) {
      payload.openrouter_api_url = form.openrouter_api_url.trim();
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
      <div className="settings">
        <div className="settings-header">
          <h2>Settings</h2>
        </div>
        <div className="settings-card">Loading settings…</div>
      </div>
    );
  }

  return (
    <div className="settings" data-testid="settings-panel">
      <div className="settings-header">
        <div>
          <h2>Settings</h2>
          <p className="settings-subtitle">
            Configure your OpenRouter credentials and model preferences. Keys are stored locally.
          </p>
        </div>
        <div className="settings-actions">
          <button className="secondary-btn" onClick={handleTest} disabled={testing}>
            {testing ? 'Testing…' : 'Test Connection'}
          </button>
          <button className="secondary-btn" onClick={onClose}>
            Back to Chat
          </button>
        </div>
      </div>

      <form className="settings-card" onSubmit={handleSave}>
        {error && <div className="settings-alert error" role="alert">{error}</div>}
        {success && <div className="settings-alert success">{success}</div>}

        <div className="field">
          <label htmlFor="openrouter_api_key">OpenRouter API Key</label>
          <input
            id="openrouter_api_key"
            type="password"
            value={form.openrouter_api_key}
            onChange={handleChange('openrouter_api_key')}
            placeholder={maskedKey ? `Saved (${maskedKey})` : 'sk-or-v1-...'}
            autoComplete="off"
          />
          <div className="field-hint">Leave blank to keep the existing key.</div>
        </div>

        <div className="field">
          <label htmlFor="openrouter_api_url">OpenRouter Base URL</label>
          <input
            id="openrouter_api_url"
            type="text"
            value={form.openrouter_api_url}
            onChange={handleChange('openrouter_api_url')}
            placeholder="https://openrouter.ai/api/v1/chat/completions"
            required
          />
        </div>

        <div className="field">
          <label htmlFor="council_models">Council Models (one per line)</label>
          <textarea
            id="council_models"
            value={form.council_models_text}
            onChange={handleChange('council_models_text')}
            rows={5}
          />
        </div>

        <div className="field">
          <label htmlFor="chairman_model">Chairman Model</label>
          <input
            id="chairman_model"
            type="text"
            value={form.chairman_model}
            onChange={handleChange('chairman_model')}
            required
          />
        </div>

        <div className="settings-actions">
          <button type="submit" className="primary-btn" disabled={saving}>
            {saving ? 'Saving…' : 'Save Settings'}
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
    </div>
  );
}
