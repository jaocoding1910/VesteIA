import { useEffect, useRef, useState } from 'react';
import { request, registerCapture, captureHeaders } from '../../services/mvpApi';
import Icon from '../../components/ui/Icon';
export default function PhotoAvatarSource({
  legacyId,
  onApply
}) {
  const [file, setFile] = useState(null),
    [preview, setPreview] = useState(''),
    [consent, setConsent] = useState(false),
    [busy, setBusy] = useState(false),
    [error, setError] = useState(''),
    [message, setMessage] = useState(''),
    session = useRef(null),
    mounted = useRef(true);
  useEffect(() => () => {
    if (preview) URL.revokeObjectURL(preview);
  }, [preview]);
  useEffect(() => {
    mounted.current = true;
    return () => {
      mounted.current = false;
      if (session.current) request(`/provador/sessoes/${session.current}`, {
        method: 'DELETE',
        headers: captureHeaders(session.current)
      }).catch(() => {});
    };
  }, []);
  function receive(e) {
    const image = e.target.files?.[0];
    if (!image) return;
    if (!['image/jpeg', 'image/png', 'image/webp'].includes(image.type) || image.size > 10 * 1024 * 1024) {
      setError('Envie JPEG, PNG ou WebP de até 10 MB.');
      return;
    }
    setFile(image);
    setPreview(URL.createObjectURL(image));
    setMessage('');
    setError('');
  }
  async function analyze() {
    setBusy(true);
    setError('');
    let id;
    try {
      const form = new FormData();
      form.append('foto', file);
      form.append('produto_id', legacyId);
      form.append('modo', 'foto');
      const capture = await request('/provador/preparar', {
        method: 'POST',
        body: form
      });
      id = capture.sessao_id;
      session.current = id;
      registerCapture(id, capture.access_token);
      if (!mounted.current) return;
      const result = await request(`/mvp/avatar/foto/${id}`, {
        method: 'POST',
        headers: captureHeaders(id)
      });
      if (!mounted.current) return;
      if (result.aplicavel) {
        onApply(result.configuracao);
        setMessage(result.mensagem);
      } else setError(result.mensagem);
    } catch (e) {
      if (mounted.current) setError(e.message);
    } finally {
      if (id) {
        try {
          await request(`/provador/sessoes/${id}`, {
            method: 'DELETE',
            headers: captureHeaders(id)
          });
          session.current = null;
        } catch {
          if (mounted.current) setError('A análise terminou, mas a exclusão da captura falhou. A captura privada expira em até 24h.');
        }
      }
      if (mounted.current) setBusy(false);
    }
  }
  return <section className="avatar-photo-source"><p className="muted">Foto frontal, em pé e de corpo inteiro. Ela ajusta proporções visuais deste mesmo avatar; não calcula medidas em cm.</p><label className="upload"><Icon name="camera" /><strong>Escolher foto de corpo inteiro</strong><input aria-label="Foto para criar avatar" type="file" accept="image/jpeg,image/png,image/webp" onChange={receive} disabled={busy} /></label>{preview && <img className="source-preview" src={preview} alt="Prévia da foto para avatar" />}<label className="consent"><input type="checkbox" checked={consent} onChange={e => setConsent(e.target.checked)} disabled={busy} /> Autorizo a análise temporária. A captura será excluída ao concluir; se a exclusão falhar, expira em 24h.</label><button type="button" className="secondary full" disabled={!file || !consent || !legacyId || busy} onClick={analyze}>{busy ? 'Analisando proporções…' : 'Aplicar proporções da foto'}</button>{error && <p className="error" role="alert">{error}</p>}{message && <p className="success" role="status">{message}</p>}<small className="muted">MVP com representação 2D. Geração fotorrealista externa ainda não configurada.</small></section>;
}
