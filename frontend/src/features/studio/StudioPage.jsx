import { useCallback, useEffect, useMemo, useReducer, useRef, useState } from 'react';
import Icon from '../../components/ui/Icon';
import { ApiError, backend, newRequestId } from './api';
import CompareStep from './CompareStep';
import { dataUrlToBlob } from './files';
import { AvatarStep, TryOnStep } from './GenerateSteps';
import { DetailsStep, GarmentsStep, PhotoStep } from './InputSteps';
import { composeLook, num, slotOf } from './sizeModel';
import { ConfirmDialog, Notice, ProviderBadge, Spinner } from './ui';
import './Studio.css';

const STEPS = [
  ['Sua foto', 'Envie uma selfie ou foto. Diga o que ela mostra para sabermos o que precisa ser estimado.'],
  ['Peças', 'Envie a imagem de uma ou mais peças de roupa.'],
  ['Categoria e tamanho', 'Informe o tipo de cada peça. Tamanho e medidas são opcionais.'],
  ['Avatar base', 'Gere seu avatar base e aprove-o antes de vestir as peças.'],
  ['Vestir', 'Escolha as peças e gere a imagem com elas.'],
  ['Comparar', 'Veja antes e depois, compare tamanhos e monte o look.'],
];
const DEFAULT_SIZES = ['P', 'M', 'G', 'GG'];

const initial = {
  step: 1, framing: 'corpo_inteiro', upperState: 'nao_informado', photo: null, photoError: '', photoServerError: '',
  garments: [], body: {}, consent: false, avatar: null, look: [], result: null, previews: null, busy: null,
  errors: {}, usage: null,
};

const revoke = url => { if (url?.startsWith('blob:')) URL.revokeObjectURL(url); };

function reducer(state, action) {
  switch (action.type) {
    case 'patch': {
      const next = { ...state, ...action.patch };
      if (action.resetAvatar && state.avatar) Object.assign(next, { avatar: null, result: null, previews: null });
      return next;
    }
    case 'goto': return { ...state, step: action.step };
    case 'photoStart': return { ...state, photoError: '', photoServerError: '' };
    case 'photo':
      revoke(state.photo?.url);
      return { ...state, photo: action.photo, photoError: '', avatar: null, result: null, previews: null };
    case 'photoWarnings': return { ...state, photo: state.photo && { ...state.photo, warnings: action.warnings }, photoServerError: action.serverError || '' };
    case 'photoError': return { ...state, photoError: action.message };
    case 'addGarment': {
      const garment = { id: `g${Date.now().toString(36)}${Math.random().toString(36).slice(2, 6)}`, description: '', category: '', sizes: [...DEFAULT_SIZES], selected: '', measures: {}, ...action.garment };
      return { ...state, garments: [...state.garments, garment], look: [...state.look, garment.id] };
    }
    case 'removeGarment': {
      revoke(state.garments.find(g => g.id === action.id)?.url);
      return { ...state, garments: state.garments.filter(g => g.id !== action.id), look: state.look.filter(id => id !== action.id), previews: state.previews?.garmentId === action.id ? null : state.previews };
    }
    case 'garment': return { ...state, garments: state.garments.map(g => g.id === action.id ? { ...g, ...action.patch } : g) };
    case 'measure': return {
      ...state, garments: state.garments.map(g => g.id !== action.id ? g : { ...g, measures: { ...g.measures, [action.size]: { ...(g.measures[action.size] || {}), [action.key]: action.value } } }),
    };
    case 'body': return { ...state, body: { ...state.body, [action.key]: action.value } };
    case 'approveAvatar': return { ...state, avatar: { ...state.avatar, approved: true }, step: 5 };
    case 'lookAdd': {
      const items = composeLook([...state.look, action.id].map(id => state.garments.find(g => g.id === id)).filter(Boolean));
      return { ...state, look: items.map(g => g.id) };
    }
    case 'lookRemove': return { ...state, look: state.look.filter(id => id !== action.id) };
    case 'busy': return { ...state, busy: action.busy, errors: { ...state.errors, [action.busy]: null } };
    case 'fail': return { ...state, busy: null, errors: { ...state.errors, [action.kind]: action.error } };
    case 'avatarDone': return { ...state, busy: null, avatar: { ...action.avatar, approved: false }, result: null, previews: null, usage: action.usage || state.usage };
    case 'resultDone': return { ...state, busy: null, result: action.result, step: 6, usage: action.usage || state.usage };
    case 'previewsDone': return { ...state, busy: null, previews: action.previews, usage: action.usage || state.usage };
    case 'usage': return { ...state, usage: action.usage };
    case 'reset':
      revoke(state.photo?.url);
      state.garments.forEach(g => revoke(g.url));
      return { ...initial };
    default: return state;
  }
}

const lookSignature = items => items.map(g => `${g.id}:${g.category}:${g.selected || ''}`).join('|');

export default function StudioPage() {
  const [state, dispatch] = useReducer(reducer, initial);
  const [status, setStatus] = useState(null);
  const [boot, setBoot] = useState({ phase: 'loading', message: '' });
  const [accessCode, setAccessCode] = useState('');
  const [confirmClear, setConfirmClear] = useState(false);
  const inFlight = useRef(false);
  const headingRef = useRef(null);

  // Consulta o backend e abre uma sessão; devolve o resultado sem alterar estado (aplicado por quem chamou).
  const connect = useCallback(async (code = '') => {
    try {
      const info = await backend.status();
      if (info.access_code_required && !code) return { info, boot: { phase: 'code', message: '' } };
      const session = await backend.startSession(code);
      return { info, usage: session.usage, boot: { phase: 'ready', message: '' } };
    } catch (error) {
      return { boot: { phase: error.status === 403 ? 'code' : 'error', message: error.message } };
    }
  }, []);

  const apply = useCallback(result => {
    if (result.info) setStatus(result.info);
    if (result.usage) dispatch({ type: 'usage', usage: result.usage });
    setBoot(result.boot);
  }, []);

  useEffect(() => {
    let active = true;
    connect('').then(result => { if (active) apply(result); });
    return () => { active = false; backend.endSession().catch(() => {}); };
  }, [connect, apply]);

  const start = async code => {
    setBoot({ phase: 'loading', message: '' });
    apply(await connect(code));
  };


  // Ao trocar de etapa, o foco vai para o título (leitores de tela e teclado).
  useEffect(() => { headingRef.current?.focus({ preventScroll: false }); }, [state.step]);

  const lookItems = useMemo(() => composeLook(state.look.map(id => state.garments.find(g => g.id === id)).filter(g => g && slotOf(g.category))), [state.look, state.garments]);
  const stale = Boolean(state.result) && state.result.signature !== lookSignature(lookItems);

  const remaining = caps => {
    const u = state.usage;
    if (!u || !caps) return null;
    const values = [u.limite_sessao - u.sessao];
    if (caps.paid) values.push(u.limite_pagas_dia - u.pagas_hoje, u.limite_pagas_total - u.pagas_total);
    else values.push(u.limite_locais_dia - u.locais_hoje);
    return Math.max(0, Math.min(...values));
  };

  async function guarded(kind, task) {
    if (inFlight.current) return; // bloqueia duplo clique antes da próxima renderização
    inFlight.current = true;
    dispatch({ type: 'busy', busy: kind });
    try {
      await task();
    } catch (error) {
      const info = error instanceof ApiError ? error : new ApiError('Falha inesperada. Tente novamente.');
      dispatch({ type: 'fail', kind, error: { message: info.message, inconclusive: info.inconclusive, chargedCalls: info.chargedCalls, status: info.status } });
    } finally {
      inFlight.current = false;
    }
  }

  const generateAvatar = () => guarded('avatar', async () => {
    const caps = status.avatar;
    const data = await backend.avatar({
      photo: state.photo.file, framing: state.framing, upper_state: state.upperState, consent: 'true',
      request_id: newRequestId(), expected_calls: caps.generates ? 1 : 0,
    });
    dispatch({ type: 'avatarDone', usage: data.usage, avatar: { image: data.image, simulated: data.simulated, provider: data.provider, notes: data.notes, estimated: data.estimated_regions } });
  });

  const generateTryOn = () => guarded('tryon', async () => {
    const caps = status.tryon;
    const items = lookItems;
    const base = await dataUrlToBlob(state.avatar.image);
    const data = await backend.tryon({
      base, garments: items.map((g, i) => [g.file, `peca-${i + 1}`]),
      garments_meta: items.map(g => ({ category: g.category, description: g.description, size_label: g.selected || null })),
      consent: 'true', request_id: newRequestId(), expected_calls: caps.multi_garment ? 1 : items.length,
    });
    dispatch({ type: 'resultDone', usage: data.usage, result: { image: data.image, simulated: data.simulated, notes: data.notes, signature: lookSignature(items) } });
  });

  const generatePreviews = ({ garment, sizes, selected, key }) => guarded('sizes', async () => {
    const base = await dataUrlToBlob(state.avatar.image);
    const payloadSizes = sizes.map(label => ({ label, measures: Object.fromEntries(Object.entries(garment.measures?.[label] || {}).map(([k, v]) => [k, num(v)]).filter(([, v]) => v !== null)) }));
    const body = Object.fromEntries(Object.entries(state.body).map(([k, v]) => [k, num(v)]).filter(([, v]) => v !== null));
    const data = await backend.sizePreviews({
      base, garment: [[garment.file, 'peca']], category: garment.category, description: garment.description,
      sizes: payloadSizes, selected_label: selected, body, consent: 'true', request_id: newRequestId(), expected_calls: sizes.length,
    });
    dispatch({ type: 'previewsDone', usage: data.usage, previews: { garmentId: garment.id, items: data.previews, selected, key, error: data.error || null } });
  });

  async function clearSession() {
    setConfirmClear(false);
    try { await backend.endSession(); } catch { /* sessão já encerrada */ }
    dispatch({ type: 'reset' });
    await start(accessCode);
  }

  const canNext = {
    1: Boolean(state.photo) && !state.photoError && (status?.avatar?.accepts_partial_photo !== false || state.framing === 'corpo_inteiro'),
    2: state.garments.length > 0,
    3: state.garments.length > 0 && state.garments.every(g => g.category),
    4: Boolean(state.avatar?.approved),
    5: Boolean(state.result),
    6: false,
  };
  const reachable = step => step === 1 || [...Array(step - 1).keys()].every(i => canNext[i + 1]);

  if (boot.phase !== 'ready') {
    return (
      <div className="studio studio--boot">
        {boot.phase === 'loading' && <Spinner label="Preparando o provador…" />}
        {boot.phase === 'error' && (
          <div className="boot-card">
            <Icon name="alert" size={36} />
            <h1>Serviço indisponível</h1>
            <p>{boot.message || 'Não foi possível iniciar o provador.'}</p>
            <p className="hint">Confira se o backend está ligado (INICIAR_BACKEND.bat). O provador não precisa de banco de dados.</p>
            <button className="btn btn-primary" onClick={() => start(accessCode)}><Icon name="refresh" size={18} /> Tentar novamente</button>
          </div>
        )}
        {boot.phase === 'code' && (
          <form className="boot-card" onSubmit={e => { e.preventDefault(); start(accessCode); }}>
            <Icon name="lock" size={36} />
            <h1>Acesso de teste</h1>
            <p>Este provador está em teste restrito. Informe o código de acesso.</p>
            {boot.message && <Notice kind="error" live>{boot.message}</Notice>}
            <label className="field"><span>Código de acesso</span><input value={accessCode} onChange={e => setAccessCode(e.target.value)} autoComplete="off" /></label>
            <button className="btn btn-primary" disabled={!accessCode}>Entrar</button>
          </form>
        )}
      </div>
    );
  }

  const simulated = status?.avatar?.kind === 'simulated' || status?.tryon?.kind === 'simulated';
  const [title, subtitle] = STEPS[state.step - 1];
  const stepProps = { state, dispatch, status, backend, remaining, lookItems, stale };

  return (
    <div className="studio">
      <div className="studio__top">
        <div>
          <span className="eyebrow">Provador VesteIA</span>
          <p className="studio__providers">
            <span>Avatar: {status?.avatar?.label}</span> <ProviderBadge caps={status?.avatar} />
            <span>Prova: {status?.tryon?.label}</span> <ProviderBadge caps={status?.tryon} />
          </p>
        </div>
        <button className="btn btn-danger btn-sm" onClick={() => setConfirmClear(true)} disabled={Boolean(state.busy)}><Icon name="trash" size={16} /> Limpar sessão</button>
      </div>
      {simulated && <Notice kind="sim">Modo de teste com <strong>respostas simuladas</strong>: as imagens são colagens carimbadas “SIMULAÇÃO”, sem IA. A qualidade real depende do provedor configurado.</Notice>}

      <nav className="stepper" aria-label="Etapas do provador">
        <ol>
          {STEPS.map(([label], index) => {
            const step = index + 1;
            const done = step < state.step && canNext[step];
            return (
              <li key={label} className={`${state.step === step ? 'is-current' : ''} ${done ? 'is-done' : ''}`}>
                <button onClick={() => dispatch({ type: 'goto', step })} disabled={!reachable(step) || Boolean(state.busy)} aria-current={state.step === step ? 'step' : undefined}>
                  <span className="stepper__dot">{done ? <Icon name="check" size={14} /> : step}</span>
                  <span className="stepper__label">{label}</span>
                </button>
              </li>
            );
          })}
        </ol>
      </nav>

      <section className="studio__panel" aria-labelledby="step-title" key={state.step}>
        <header className="panel-head">
          <span className="panel-head__num">Etapa {state.step} de 6</span>
          <h1 id="step-title" tabIndex={-1} ref={headingRef}>{title}</h1>
          <p>{subtitle}</p>
        </header>
        {state.step === 1 && <PhotoStep {...stepProps} />}
        {state.step === 2 && <GarmentsStep {...stepProps} />}
        {state.step === 3 && <DetailsStep {...stepProps} />}
        {state.step === 4 && <AvatarStep {...stepProps} onGenerate={generateAvatar} />}
        {state.step === 5 && <TryOnStep {...stepProps} onGenerate={generateTryOn} />}
        {state.step === 6 && <CompareStep {...stepProps} onGenerate={generateTryOn} onPreviews={generatePreviews} />}
        <footer className="panel-nav">
          <button className="btn btn-secondary" disabled={state.step === 1 || Boolean(state.busy)} onClick={() => dispatch({ type: 'goto', step: state.step - 1 })}><Icon name="back" size={18} /> Voltar</button>
          {state.step < 6 && (
            <button className="btn btn-primary" disabled={!canNext[state.step] || Boolean(state.busy)} onClick={() => dispatch({ type: 'goto', step: state.step + 1 })}>
              {state.step === 4 && !state.avatar?.approved ? 'Aprove o avatar para continuar' : state.step === 5 && !state.result ? 'Gere a imagem para continuar' : 'Continuar'} <Icon name="arrow" size={18} />
            </button>
          )}
        </footer>
      </section>
      {state.usage && (
        <p className="usage-line">Uso nesta sessão: {state.usage.sessao} de {state.usage.limite_sessao} gerações{status?.tryon?.paid || status?.avatar?.paid ? ` · pagas hoje: ${state.usage.pagas_hoje}/${state.usage.limite_pagas_dia}` : ''}. Nada é gerado sem o seu clique.</p>
      )}
      <ConfirmDialog open={confirmClear} title="Limpar a sessão?" confirmLabel="Limpar tudo" onCancel={() => setConfirmClear(false)} onConfirm={clearSession}>
        <p>Foto, peças, avatar base, resultados e medidas desta aba serão descartados, e a sessão no servidor será encerrada. Isso não pode ser desfeito.</p>
      </ConfirmDialog>
    </div>
  );
}
