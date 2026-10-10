// Cliente da API do provador. Nenhuma chave fica no navegador.
// Gerações nunca são repetidas automaticamente; cada clique gera um request_id novo.
import { API_BASE_URL } from '../../services/apiConfig';
import { createDemoBackend } from './demoBackend';
import { ApiError } from './errors';

export { ApiError };

export const DEMO_MODE = import.meta.env.VITE_DEMO_MODE === 'true';

export const newRequestId = () =>
  (globalThis.crypto?.randomUUID?.() || `${Date.now()}-${Math.random().toString(36).slice(2)}`).replace(/[^A-Za-z0-9_-]/g, '');

function httpBackend() {
  let token = null;

  async function send(path, { method = 'GET', form, auth = true, signal } = {}) {
    const headers = { Accept: 'application/json' };
    if (auth && token) headers.Authorization = `Bearer ${token}`;
    let response;
    try {
      response = await fetch(`${API_BASE_URL}${path}`, { method, headers, body: form, signal });
    } catch (error) {
      if (error.name === 'AbortError') throw error;
      throw new ApiError('Não foi possível conectar ao serviço do VesteIA. Confira se o backend está ligado.', { status: 0 });
    }
    if (response.status === 204) return null;
    const data = await response.json().catch(() => null);
    if (!response.ok) {
      throw new ApiError(typeof data?.detail === 'string' ? data.detail : 'Não foi possível concluir. Tente novamente.', {
        status: response.status, inconclusive: Boolean(data?.inconclusive), chargedCalls: data?.charged_calls ?? null,
      });
    }
    return data;
  }

  const formOf = fields => {
    const form = new FormData();
    for (const [key, value] of Object.entries(fields)) {
      if (value === undefined || value === null) continue;
      const isFileList = Array.isArray(value) && value.every(item => Array.isArray(item) && item[0] instanceof Blob);
      if (isFileList) value.forEach(([blob, name]) => form.append(key, blob, name));
      else if (value instanceof Blob) form.append(key, value, `${key}.jpg`);
      else form.append(key, typeof value === 'object' ? JSON.stringify(value) : String(value));
    }
    return form;
  };

  return {
    demo: false,
    status: () => send('/api/studio/status'),
    async startSession(accessCode = '') {
      const data = await send('/api/studio/session', { method: 'POST', form: formOf({ access_code: accessCode }), auth: false });
      token = data.token;
      return data;
    },
    hasSession: () => Boolean(token),
    async endSession() {
      if (!token) return;
      try { await send('/api/studio/session', { method: 'DELETE' }); } finally { token = null; }
    },
    checkPhoto: (photo, framing) => send('/api/studio/photo/check', { method: 'POST', form: formOf({ photo, framing }) }),
    avatar: fields => send('/api/studio/avatar', { method: 'POST', form: formOf(fields) }),
    tryon: fields => send('/api/studio/tryon', { method: 'POST', form: formOf(fields) }),
    sizePreviews: fields => send('/api/studio/size-previews', { method: 'POST', form: formOf(fields) }),
  };
}

export const backend = DEMO_MODE ? createDemoBackend() : httpBackend();
