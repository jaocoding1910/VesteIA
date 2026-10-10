import Icon from '../../components/ui/Icon';
import { download } from './files';
import { SLOT_LABEL, categoryLabel, composeLook, slotOf } from './sizeModel';
import { CallsInfo, ImageFrame, Notice, ProviderBadge, Spinner } from './ui';

export function ConsentBox({ state, dispatch, status }) {
  const kinds = new Set([status?.avatar?.kind, status?.tryon?.kind]);
  const external = [status?.avatar, status?.tryon].filter(c => c?.kind === 'external');
  return (
    <label className={`consent ${state.consent ? 'is-on' : ''}`}>
      <input type="checkbox" checked={state.consent} disabled={Boolean(state.busy)} onChange={e => dispatch({ type: 'patch', patch: { consent: e.target.checked } })} />
      <span>
        <strong>Autorizo o processamento das minhas imagens nesta sessão.</strong>{' '}
        {external.length > 0
          ? <>As fotos serão enviadas a <strong>{[...new Set(external.map(c => c.label))].join(' e ')}</strong>, serviço externo que pode cobrar por geração e segue os próprios termos. </>
          : kinds.has('local') ? <>O processamento acontece no computador onde o VesteIA está instalado. </>
          : <>Neste modo as imagens são simuladas, sem IA. </>}
        O VesteIA não salva as fotos; você pode limpar a sessão a qualquer momento.
      </span>
    </label>
  );
}

function ErrorBox({ error }) {
  if (!error) return null;
  return (
    <Notice kind="error" live>
      <strong>{error.inconclusive ? 'Resposta inconclusiva. ' : 'Não foi possível gerar. '}</strong>{error.message}
      {error.chargedCalls > 0 && <> Esta tentativa foi contabilizada no limite ({error.chargedCalls} {error.chargedCalls > 1 ? 'gerações' : 'geração'}).</>}
      {' '}Nada foi repetido automaticamente; tente de novo somente se quiser.
    </Notice>
  );
}

export function AvatarStep({ state, dispatch, status, remaining, onGenerate }) {
  const caps = status?.avatar;
  const calls = caps?.generates ? 1 : 0;
  const busy = state.busy === 'avatar';
  const avatar = state.avatar;
  const blockedFraming = caps && !caps.accepts_partial_photo && state.framing !== 'corpo_inteiro';
  return (
    <div className="step-grid step-grid--wide">
      <div className="step-main">
        <div className="provider-line"><span>Avatar: <strong>{caps?.label || '—'}</strong></span><ProviderBadge caps={caps} /></div>
        {caps && !caps.ready && <Notice kind="warn">{caps.message}</Notice>}
        {caps?.kind === 'simulated' && <Notice kind="sim">Modo simulado: o “avatar” é a sua foto centralizada e carimbada. Serve para testar o fluxo, não a qualidade da IA.</Notice>}
        {!caps?.generates && caps && <Notice kind="info">Sem gerador de IA configurado: sua foto de corpo inteiro será usada como avatar base, apenas centralizada, sem distorção.</Notice>}
        {blockedFraming && <Notice kind="warn">Este modo exige foto de corpo inteiro. Volte à etapa 1 e envie outra foto.</Notice>}
        <ConsentBox state={state} dispatch={dispatch} status={status} />
        <CallsInfo calls={calls} remaining={remaining(caps)} paid={caps?.paid} simulated={caps?.kind === 'simulated'} />
        <div className="actions">
          <button className="btn btn-primary" disabled={!state.consent || busy || Boolean(state.busy) || !caps?.ready || blockedFraming} onClick={onGenerate}>
            {busy ? <Spinner label="Gerando avatar base…" /> : <><Icon name="wand" size={18} /> {avatar ? 'Gerar novamente' : 'Gerar avatar base'}</>}
          </button>
          {avatar && !avatar.approved && (
            <button className="btn btn-secondary" disabled={Boolean(state.busy)} onClick={() => dispatch({ type: 'approveAvatar' })}><Icon name="check" size={18} /> Aprovar este avatar</button>
          )}
        </div>
        {busy && <p className="hint" role="status">Isso pode levar até alguns minutos. Não é preciso clicar de novo.</p>}
        <ErrorBox error={state.busy ? null : state.errors.avatar} />
        {avatar && (
          <div className="result-notes">
            {avatar.estimated && <Notice kind="warn">Partes do corpo que não estavam na foto foram <strong>estimadas</strong>. Elas não representam suas medidas reais.</Notice>}
            {avatar.notes?.map(n => <p key={n} className="hint">{n}</p>)}
            <p className="hint">Confira rosto, cabelo, barba, tom de pele e proporções. Se algo mudou, gere novamente ou troque a foto; não aprove um avatar que não pareça você.</p>
            {avatar.approved && <Notice kind="ok">Avatar base aprovado. Ele será a referência de identidade de todas as próximas gerações.</Notice>}
          </div>
        )}
      </div>
      <div className="pair">
        <ImageFrame src={state.photo?.url} alt="Foto original enviada" label="Sua foto" />
        <ImageFrame src={avatar?.image} alt="Avatar base gerado" label="Avatar base" badge={avatar?.simulated ? 'SIMULADO' : avatar && !caps?.generates ? 'Sem IA' : null}>
          {busy ? <Spinner label="Gerando…" /> : <><Icon name="user" size={44} /><span>O avatar base aparece aqui</span></>}
        </ImageFrame>
      </div>
      {avatar && <button className="btn btn-ghost btn-sm download" onClick={() => download(avatar.image, 'vesteia-avatar-base.jpg')}><Icon name="download" size={16} /> Baixar avatar base</button>}
    </div>
  );
}

export function LookPicker({ state, dispatch, compact }) {
  const lookItems = composeLook(state.look.map(id => state.garments.find(g => g.id === id)).filter(Boolean));
  return (
    <ul className={`look-list ${compact ? 'is-compact' : ''}`}>
      {state.garments.map(g => {
        const on = lookItems.some(item => item.id === g.id);
        const slot = slotOf(g.category);
        const replaces = !on && slot ? lookItems.find(item => { const s = slotOf(item.category); return s === slot || (slot === 'full' && (s === 'upper' || s === 'lower')) || ((slot === 'upper' || slot === 'lower') && s === 'full'); }) : null;
        return (
          <li key={g.id} className={on ? 'is-on' : ''}>
            <img src={g.url} alt="" />
            <div>
              <strong>{g.description || categoryLabel(g.category)}</strong>
              <small>{categoryLabel(g.category)} · {slot ? SLOT_LABEL[slot] : 'sem categoria'}{g.selected ? ` · tamanho ${g.selected}` : ''}</small>
              {replaces && <small className="replace-hint">Substitui: {replaces.description || categoryLabel(replaces.category)}</small>}
            </div>
            <button className={`btn btn-sm ${on ? 'btn-secondary' : 'btn-primary'}`} disabled={!slot || Boolean(state.busy)} onClick={() => dispatch({ type: on ? 'lookRemove' : 'lookAdd', id: g.id })}>
              {on ? <><Icon name="close" size={14} /> Remover</> : replaces ? <><Icon name="refresh" size={14} /> Substituir</> : <><Icon name="plus" size={14} /> Vestir</>}
            </button>
          </li>
        );
      })}
    </ul>
  );
}

export function TryOnStep({ state, dispatch, status, remaining, lookItems, onGenerate }) {
  const caps = status?.tryon;
  const calls = !lookItems.length ? 0 : caps?.multi_garment ? 1 : lookItems.length;
  const busy = state.busy === 'tryon';
  return (
    <div className="step-grid step-grid--wide">
      <div className="step-main">
        <div className="provider-line"><span>Prova: <strong>{caps?.label || '—'}</strong></span><ProviderBadge caps={caps} /></div>
        {caps && !caps.ready && <Notice kind="warn">{caps.message}</Notice>}
        {caps?.kind === 'simulated' && <Notice kind="sim">Modo simulado: a peça é colada sobre o avatar e carimbada. Não representa a qualidade da IA.</Notice>}
        <h3 className="sub">Peças para vestir</h3>
        <LookPicker state={state} dispatch={dispatch} />
        {!caps?.multi_garment && lookItems.length > 1 && <p className="hint">Este provedor veste uma peça por vez, sempre partindo do avatar base aprovado.</p>}
        <ConsentBox state={state} dispatch={dispatch} status={status} />
        {lookItems.length > 0 && <CallsInfo calls={calls} remaining={remaining(caps)} paid={caps?.paid} simulated={caps?.kind === 'simulated'} />}
        <div className="actions">
          <button className="btn btn-primary" disabled={!lookItems.length || !state.consent || Boolean(state.busy) || !caps?.ready} onClick={onGenerate}>
            {busy ? <Spinner label="Vestindo as peças…" /> : <><Icon name="wand" size={18} /> Gerar imagem com as peças</>}
          </button>
        </div>
        {busy && <p className="hint" role="status">A geração pode levar alguns minutos. Não é preciso clicar de novo.</p>}
        <ErrorBox error={state.busy ? null : state.errors.tryon} />
      </div>
      <div className="pair">
        <ImageFrame src={state.avatar?.image} alt="Avatar base aprovado" label="Avatar base" badge={state.avatar?.simulated ? 'SIMULADO' : null} />
        <ImageFrame src={state.result?.image} alt="Resultado com as peças" label="Com a peça escolhida" badge={state.result?.simulated ? 'SIMULADO' : null}>
          {busy ? <Spinner label="Gerando…" /> : <><Icon name="shirt" size={44} /><span>O resultado aparece aqui</span></>}
        </ImageFrame>
      </div>
    </div>
  );
}

export { ErrorBox };
