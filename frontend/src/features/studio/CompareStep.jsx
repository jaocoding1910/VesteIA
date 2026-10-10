import { useMemo, useRef, useState } from 'react';
import Icon from '../../components/ui/Icon';
import { download } from './files';
import { ConsentBox, ErrorBox, LookPicker } from './GenerateSteps';
import { BodyMeasures, MeasuresTable } from './InputSteps';
import { SLOT_FIELDS, categoryLabel, compareSizes, missingSummary, num, slotOf } from './sizeModel';
import { CallsInfo, ConfirmDialog, ImageFrame, Notice, ProviderBadge, Spinner } from './ui';

const TABS = [['before', 'Antes e depois', 'compare'], ['sizes', 'Comparar tamanhos', 'ruler']];

function Tabs({ value, onChange }) {
  const refs = useRef({});
  const move = (e, index) => {
    if (!['ArrowRight', 'ArrowLeft', 'Home', 'End'].includes(e.key)) return;
    e.preventDefault();
    const next = e.key === 'Home' ? 0 : e.key === 'End' ? TABS.length - 1 : (index + (e.key === 'ArrowRight' ? 1 : -1) + TABS.length) % TABS.length;
    onChange(TABS[next][0]);
    refs.current[TABS[next][0]]?.focus();
  };
  return (
    <div className="tabs" role="tablist" aria-label="Visualização do resultado">
      {TABS.map(([key, label, icon], index) => (
        <button key={key} ref={el => { refs.current[key] = el; }} role="tab" id={`tab-${key}`} aria-controls={`panel-${key}`}
          aria-selected={value === key} tabIndex={value === key ? 0 : -1} onClick={() => onChange(key)} onKeyDown={e => move(e, index)}>
          <Icon name={icon} size={16} /> {label}
        </button>
      ))}
    </div>
  );
}

function BeforeAfter({ state, dispatch, status, remaining, lookItems, stale, onGenerate }) {
  const caps = status?.tryon;
  const calls = !lookItems.length ? 0 : caps?.multi_garment ? 1 : lookItems.length;
  return (
    <div className="before-panel">
      <div className="pair pair--large">
        <ImageFrame src={state.avatar?.image} alt="Avatar base aprovado" label="Avatar base" badge={state.avatar?.simulated ? 'SIMULADO' : null} />
        <ImageFrame src={state.result?.image} alt={`Resultado com ${lookItems.map(i => i.description || categoryLabel(i.category)).join(', ')}`} label="Com a peça escolhida" badge={state.result?.simulated ? 'SIMULADO' : stale ? 'Desatualizado' : null}>
          {state.busy === 'tryon' ? <Spinner label="Gerando…" /> : <><Icon name="shirt" size={44} /><span>Gere a imagem para ver o look</span></>}
        </ImageFrame>
      </div>
      {state.result?.notes?.map(n => <p key={n} className="hint">{n}</p>)}
      <div className="look-panel">
        <div className="look-panel__head">
          <h3 className="sub"><Icon name="layers" size={18} /> Montar o look</h3>
          <button className="btn btn-ghost btn-sm" onClick={() => dispatch({ type: 'goto', step: 2 })}><Icon name="plus" size={16} /> Enviar outra peça</button>
        </div>
        <p className="hint">Vestir uma peça substitui a da mesma região; as outras peças aprovadas continuam. Nada é gerado automaticamente ao mudar o look.</p>
        <LookPicker state={state} dispatch={dispatch} compact />
        {stale && lookItems.length > 0 && <Notice kind="info">O look mudou desde a última imagem. Gere novamente para ver a combinação atual.</Notice>}
        {!lookItems.length && <Notice kind="info">Escolha ao menos uma peça para vestir.</Notice>}
        {(stale || !state.result) && lookItems.length > 0 && (
          <>
            <ConsentBox state={state} dispatch={dispatch} status={status} />
            <CallsInfo calls={calls} remaining={remaining(caps)} paid={caps?.paid} simulated={caps?.kind === 'simulated'} />
            <button className="btn btn-primary" disabled={!state.consent || Boolean(state.busy) || !caps?.ready} onClick={onGenerate}>
              {state.busy === 'tryon' ? <Spinner label="Vestindo…" /> : <><Icon name="wand" size={18} /> Gerar com o look atual</>}
            </button>
          </>
        )}
        <ErrorBox error={state.busy ? null : state.errors.tryon} />
      </div>
      {state.result && (
        <div className="actions">
          <button className="btn btn-secondary btn-sm" onClick={() => download(state.result.image, 'vesteia-look.jpg')}><Icon name="download" size={16} /> Baixar imagem</button>
          <button className="btn btn-ghost btn-sm" onClick={() => dispatch({ type: 'patch', patch: { result: null } })}><Icon name="trash" size={16} /> Descartar resultado</button>
        </div>
      )}
    </div>
  );
}

function SizesPanel({ state, dispatch, status, remaining, onPreviews }) {
  const sized = state.garments.filter(g => slotOf(g.category));
  const [garmentId, setGarmentId] = useState(() => (state.look.find(id => sized.some(g => g.id === id)) || sized[0]?.id));
  const garment = sized.find(g => g.id === garmentId) || sized[0];
  const [picked, setPicked] = useState(null);
  const [confirm, setConfirm] = useState(false);
  const caps = status?.tryon;
  const slot = garment ? slotOf(garment.category) : null;
  const selected = garment?.selected || garment?.sizes[0] || '';
  const rows = useMemo(() => garment ? compareSizes(slot, garment.sizes, garment.measures || {}, selected, state.body) : [], [garment, slot, selected, state.body]);
  if (!garment) return <Notice kind="info">Informe a categoria de uma peça para comparar tamanhos.</Notice>;
  const missing = missingSummary(slot, garment.sizes, garment.measures || {}, state.body);
  const firstField = SLOT_FIELDS[slot][0];
  const eligible = garment.sizes.filter(size => num(garment.measures?.[size]?.[firstField[0]]) !== null);
  const maxSizes = status?.max_sizes || 4;
  const chosen = (picked || eligible.slice(0, maxSizes)).filter(size => eligible.includes(size)).slice(0, maxSizes);
  // O tamanho de referência entra sempre que tiver medidas, para comparar com ele.
  const toGenerate = withSelected(chosen, selected, eligible).slice(0, maxSizes);
  const previewKey = JSON.stringify([garment.id, toGenerate, toGenerate.map(s => garment.measures?.[s]), state.body, selected]);
  const previews = state.previews?.garmentId === garment.id ? state.previews : null;
  const previewsStale = previews && previews.key !== previewKey;
  const canVisual = caps?.size_previews;

  return (
    <div className="sizes-panel">
      {sized.length > 1 && (
        <label className="field field--inline">
          <span>Peça</span>
          <select value={garment.id} onChange={e => { setGarmentId(e.target.value); setPicked(null); }}>
            {sized.map(g => <option key={g.id} value={g.id}>{g.description || categoryLabel(g.category)}</option>)}
          </select>
        </label>
      )}
      <div className="size-head">
        <img src={garment.url} alt="" />
        <div>
          <h3>{garment.description || categoryLabel(garment.category)}</h3>
          <p className="hint">Tamanho escolhido: <strong>{garment.selected || `não informado (comparando a partir de ${selected})`}</strong>. P não é sempre justo e GG não é sempre oversized: a leitura vem das medidas.</p>
        </div>
      </div>

      <div className="size-cards" role="list">
        {rows.map(row => (
          <article key={row.label} role="listitem" className={`size-card ${row.selected ? 'is-selected' : ''}`}>
            <header><strong>{row.label}</strong>{row.selected && <span className="badge">Escolhido</span>}</header>
            {row.filled === 0 ? <p className="hint">Sem medidas informadas.</p> : (
              <dl>
                {row.diffs.filter(d => d.value !== null).map(d => (
                  <div key={d.key}><dt>{d.name}</dt><dd>{d.value} cm{d.delta !== null && d.delta !== 0 && <em className={d.delta > 0 ? 'up' : 'down'}> {d.delta > 0 ? '+' : ''}{d.delta}</em>}</dd></div>
                ))}
              </dl>
            )}
            {row.readings.length > 0 && (
              <ul className="readings">
                {row.readings.map(r => <li key={r.label} className={`tone-${r.tone}`}><span>{r.label}</span> {r.text} <small>({r.unit} {r.value > 0 ? '+' : ''}{r.value} cm)</small></li>)}
              </ul>
            )}
          </article>
        ))}
      </div>

      {(missing.sizesWithout.length > 0 || !missing.hasBody) && (
        <Notice kind="warn">
          {missing.sizesWithout.length > 0 && <>Faltam medidas da peça em: <strong>{missing.sizesWithout.join(', ')}</strong>. </>}
          {!missing.hasBody && <>Sem as suas medidas, mostramos apenas as diferenças entre os tamanhos (não a folga no seu corpo). </>}
          Adicione abaixo; não inventamos centímetros a partir da imagem.
        </Notice>
      )}
      <details className="tips" open={missing.sizesWithout.length === garment.sizes.length}>
        <summary>Editar medidas da peça</summary>
        <MeasuresTable garment={garment} dispatch={dispatch} />
      </details>
      <details className="tips">
        <summary>Editar suas medidas</summary>
        <BodyMeasures body={state.body} dispatch={dispatch} />
      </details>
      <p className="hint">Faixas de folga são aproximações gerais; tecido com elastano, malha e modelagem mudam o caimento.</p>

      <section className="visual-sizes" aria-labelledby="visual-title">
        <div className="provider-line"><h3 id="visual-title" className="sub">Prévias visuais por tamanho</h3><ProviderBadge caps={caps} /></div>
        {!canVisual ? (
          <Notice kind="info">O provedor atual ({caps?.label || '—'}) não recebe medidas e não consegue produzir diferenças visuais confiáveis entre tamanhos. Use a comparação de medidas acima — não mostramos a mesma imagem repetida como se fossem tamanhos diferentes.</Notice>
        ) : eligible.length < 2 ? (
          <Notice kind="info">Para gerar prévias, informe ao menos “{firstField[1]}” em dois tamanhos ou mais.</Notice>
        ) : (
          <>
            <fieldset className="choice-group">
              <legend>Tamanhos para gerar (máx. {maxSizes})</legend>
              <div className="segmented">
                {eligible.map(size => {
                  const on = chosen.includes(size);
                  return (
                    <label key={size} className={on ? 'is-on' : ''}>
                      <input type="checkbox" checked={on} disabled={!on && chosen.length >= maxSizes} onChange={() => setPicked(on ? chosen.filter(s => s !== size) : [...chosen, size])} />{size}
                    </label>
                  );
                })}
              </div>
            </fieldset>
            <Notice kind="warn">Prévias <strong>ilustrativas</strong>, orientadas pelas medidas informadas. Não são uma simulação física validada do tecido.</Notice>
            <ConsentBox state={state} dispatch={dispatch} status={status} />
            <CallsInfo calls={toGenerate.length} remaining={remaining(caps)} paid={caps?.paid} simulated={caps?.kind === 'simulated'} />
            <button className="btn btn-primary" disabled={toGenerate.length < 2 || !state.consent || Boolean(state.busy) || !caps?.ready} onClick={() => setConfirm(true)}>
              {state.busy === 'sizes' ? <Spinner label="Gerando prévias…" /> : <><Icon name="ruler" size={18} /> Gerar prévias de {toGenerate.length} tamanhos</>}
            </button>
            {eligible.includes(selected) && !chosen.includes(selected) && <p className="hint">O tamanho de referência ({selected}) é sempre incluído.</p>}
          </>
        )}
        <ErrorBox error={state.busy ? null : state.errors.sizes} />
        {previews && (
          <>
            {previewsStale && <Notice kind="info">As medidas ou a seleção mudaram depois destas prévias. Gere novamente se quiser atualizá-las.</Notice>}
            {previews.error && <Notice kind="warn">A geração parou no tamanho {previews.error.size}: {previews.error.message}</Notice>}
            <div className="preview-grid">
              {previews.items.map(item => (
                <div key={item.label} className={`preview-item ${item.repeated_of ? 'is-repeated' : ''}`}>
                  <ImageFrame src={item.image} alt={`Prévia ilustrativa no tamanho ${item.label}`} label={`${item.label}${item.label === previews.selected ? ' · escolhido' : ''}`} badge={item.simulated ? 'SIMULADO' : 'Ilustrativa'} />
                  {item.repeated_of && <p className="hint warn-text">Praticamente igual ao tamanho {item.repeated_of}: não use como diferença de caimento.</p>}
                </div>
              ))}
            </div>
          </>
        )}
      </section>
      <ConfirmDialog open={confirm} title="Confirmar prévias por tamanho" confirmLabel={`Gerar ${toGenerate.length} prévias`}
        onCancel={() => setConfirm(false)}
        onConfirm={() => { setConfirm(false); onPreviews({ garment, sizes: toGenerate, selected: eligible.includes(selected) ? selected : toGenerate[0], key: previewKey }); }}>
        <p>Serão solicitadas <strong>{toGenerate.length} gerações</strong> — uma para cada tamanho ({toGenerate.join(', ')}){caps?.paid ? ', cobradas pelo provedor' : ''}.</p>
        <p>As imagens são prévias ilustrativas orientadas pelas medidas; não são simulação física. Se uma geração falhar, as seguintes não serão feitas e nada é repetido automaticamente.</p>
      </ConfirmDialog>
    </div>
  );
}

function withSelected(chosen, selected, eligible) {
  const list = [...chosen];
  if (selected && eligible.includes(selected) && !list.includes(selected)) list.unshift(selected);
  return list;
}

export default function CompareStep(props) {
  const [tab, setTab] = useState('before');
  return (
    <div className="compare">
      <Tabs value={tab} onChange={setTab} />
      <div id={`panel-${tab}`} role="tabpanel" aria-labelledby={`tab-${tab}`} className="tab-panel" tabIndex={0}>
        {tab === 'before' ? <BeforeAfter {...props} /> : <SizesPanel {...props} />}
      </div>
    </div>
  );
}
