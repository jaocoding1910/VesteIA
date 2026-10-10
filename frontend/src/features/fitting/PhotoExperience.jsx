import { useEffect, useState, useRef } from 'react';
import AvatarRenderer2D from '../../components/AvatarRenderer2D';
import { request, jsonBody, registerCapture, captureHeaders } from '../../services/mvpApi';
import Icon from '../../components/ui/Icon';
export default function PhotoExperience({
  legacyId,
  onClose
}) {
  const [file, setFile] = useState(null),
    [preview, setPreview] = useState(''),
    [consent, setConsent] = useState(false),
    [busy, setBusy] = useState(false),
    [error, setError] = useState(''),
    [result, setResult] = useState(null),
    [session, setSession] = useState(null);
  const sessionRef = useRef(null);
  useEffect(() => () => {
    if (preview) URL.revokeObjectURL(preview);
  }, [preview]);
  useEffect(() => () => {
    if (sessionRef.current) request(`/provador/sessoes/${sessionRef.current}`, {
      method: 'DELETE',
      headers: captureHeaders(sessionRef.current)
    }).catch(() => {});
  }, []);
  function receive(event) {
    const image = event.target.files[0];
    if (!image) return;
    if (!['image/jpeg', 'image/png', 'image/webp'].includes(image.type) || image.size > 10 * 1024 * 1024) {
      setError('Envie JPEG, PNG ou WebP de até 10 MB.');
      return;
    }
    setError('');
    setResult(null);
    setFile(image);
    setPreview(URL.createObjectURL(image));
  }
  async function analyze() {
    setBusy(true);
    setError('');
    try {
      if (sessionRef.current) await remove();
      const form = new FormData();
      form.append('foto', file);
      form.append('produto_id', legacyId);
      form.append('modo', 'foto');
      const capture = await request('/provador/preparar', {
        method: 'POST',
        body: form
      });
      registerCapture(capture.sessao_id, capture.access_token);
      setSession(capture.sessao_id);
      sessionRef.current = capture.sessao_id;
      const data = await request(`/provador/sessoes/${capture.sessao_id}/executar`, {
        ...jsonBody({}),
        headers: {
          ...captureHeaders(capture.sessao_id)
        }
      });
      setResult(data);
    } catch (e) {
      setError(e.message);
    } finally {
      setBusy(false);
    }
  }
  async function remove() {
    if (!sessionRef.current) return;
    await request(`/provador/sessoes/${sessionRef.current}`, {
      method: 'DELETE',
      headers: captureHeaders(sessionRef.current)
    });
    sessionRef.current = null;
    setSession(null);
    setResult(null);
  }
  const renderer = result?.renderer_avatar_2d,
    vestimenta = result?.vestimenta_avatar_2d,
    caimento = result?.simulacao_caimento_visual;
  return <section className="photo-experience"><div className="section-heading"><div><span className="eyebrow">EXPERIÊNCIA COM FOTO</span><h2>Seu corpo, suas proporções.</h2></div><button className="secondary" onClick={onClose}>Voltar ao avatar</button></div><p className="muted">Foto frontal, corpo inteiro e boa iluminação. A análise usa landmarks e proporções; não mede altura, peso ou circunferências. A renderização é 2D.</p><div className="photo-columns"><div><label className="upload"><Icon name="camera" size={30} /><strong>Escolher foto ou usar câmera</strong><span>JPEG, PNG ou WebP • até 10 MB</span><input type="file" accept="image/jpeg,image/png,image/webp" onChange={receive} /></label><label className="camera-option"><Icon name="camera" size={16} /> Abrir câmera no celular<input type="file" accept="image/jpeg,image/png,image/webp" capture="user" onChange={receive} /></label>{preview && <img className="photo-preview" src={preview} alt="Prévia da sua foto" />}<label className="consent"><input type="checkbox" checked={consent} onChange={e => setConsent(e.target.checked)} /> Autorizo processar esta foto para esta experiência. Não será usada para treinar modelos. A captura expira em 24h e pode ser excluída aqui.</label><button className="primary full" disabled={!file || !consent || busy || !legacyId} onClick={analyze}>{busy ? 'Analisando pose e qualidade…' : 'Analisar minha foto'}</button>{session && <button className="text-link" onClick={() => remove().catch(e => setError(e.message))}>Excluir foto do servidor agora</button>}</div><div className="photo-result">{error && <p className="error" role="alert">{error}</p>}{renderer?.pronto ? <><AvatarRenderer2D renderer={renderer} vestimenta={vestimenta} caimento={caimento} /><p className="muted">Representação de proporções observadas. Não é uma imagem gerada por IA nem prova de ajuste.</p></> : <div className="empty"><Icon name={busy ? 'sparkle' : 'user'} size={46} /><h3>{busy ? 'Preparando sua representação…' : result ? 'Precisamos de outra captura' : 'Sua representação aparece aqui'}</h3><p>{result?.mensagem || result?.resumo_provador?.mensagem || 'Envie uma foto para executar o pipeline original de análise.'}</p>{result?.resumo_provador?.orientacoes?.map(o => <p key={o}>{o}</p>)}</div>}</div></div></section>;
}
