import { useId, useState } from 'react';
import Icon from '../../components/ui/Icon';
import { FileProblem, inspectImage } from './files';
import { BODY_FIELDS, CATEGORIES, SLOT_FIELDS, SLOT_LABEL, slotOf } from './sizeModel';
import { ImageFrame, Notice, Spinner } from './ui';

const FRAMINGS = [
  ['rosto', 'Selfie / rosto', 'Só o rosto aparece. O corpo será estimado.'],
  ['meio_corpo', 'Meio corpo', 'Da cabeça até a cintura. As pernas serão estimadas.'],
  ['corpo_inteiro', 'Corpo inteiro', 'Da cabeça aos pés. Melhor resultado.'],
];
const UPPER = [['vestido', 'Com roupa'], ['sem_camiseta', 'Sem camiseta'], ['nao_informado', 'Prefiro não informar']];

function UploadButton({ label, icon = 'upload', capture, onFile, disabled, multiple = false, variant = 'secondary' }) {
  const id = useId();
  return (
    <label htmlFor={id} className={`btn btn-${variant} upload-btn ${disabled ? 'is-disabled' : ''}`}>
      <Icon name={icon} size={18} /> {label}
      <input id={id} className="sr-only" type="file" accept="image/jpeg,image/png,image/webp" capture={capture} multiple={multiple}
        disabled={disabled} onChange={e => { const files = [...(e.target.files || [])]; e.target.value = ''; if (files.length) onFile(multiple ? files : files[0]); }} />
    </label>
  );
}

export function PhotoStep({ state, dispatch, status, backend }) {
  const { photo, framing, upperState } = state;
  const [checking, setChecking] = useState(false);
  const maxMb = status?.max_upload_mb || 8;
  const partialAllowed = status?.avatar?.accepts_partial_photo !== false;

  async function choose(file, nextFraming = framing) {
    dispatch({ type: 'photoStart' });
    setChecking(true);
    try {
      const info = await inspectImage(file, { maxMb, minSide: 256, label: 'foto' });
      dispatch({ type: 'photo', photo: { file, ...info, warnings: [] } });
      try {
        const check = await backend.checkPhoto(file, nextFraming);
        dispatch({ type: 'photoWarnings', warnings: check.warnings || [] });
      } catch (error) {
        dispatch({ type: 'photoWarnings', warnings: [], serverError: error.message });
      }
    } catch (error) {
      dispatch({ type: 'photoError', message: error instanceof FileProblem ? error.message : 'Não foi possível ler a foto.' });
    } finally {
      setChecking(false);
    }
  }

  return (
    <div className="step-grid">
      <div className="step-main">
        <fieldset className="choice-group">
          <legend>O que a foto mostra?</legend>
          <div className="choice-cards">
            {FRAMINGS.map(([value, title, hint]) => (
              <label key={value} className={`choice-card ${framing === value ? 'is-on' : ''}`}>
                <input type="radio" name="framing" value={value} checked={framing === value} onChange={() => dispatch({ type: 'patch', patch: { framing: value }, resetAvatar: true })} />
                <strong>{title}</strong><span>{hint}</span>
              </label>
            ))}
          </div>
        </fieldset>
        {framing !== 'corpo_inteiro' && (
          partialAllowed
            ? <Notice kind="warn">As regiões do corpo fora da foto serão <strong>estimadas</strong> pela IA. Uma selfie não permite descobrir medidas corporais reais; o corpo gerado é uma aproximação.</Notice>
            : <Notice kind="warn">O modo configurado não gera corpo com IA. Para seguir, envie uma foto de <strong>corpo inteiro</strong> (cabeça aos pés).</Notice>
        )}
        <fieldset className="choice-group">
          <legend>Na foto, a parte de cima está…</legend>
          <div className="segmented">
            {UPPER.map(([value, label]) => (
              <label key={value} className={upperState === value ? 'is-on' : ''}>
                <input type="radio" name="upper" value={value} checked={upperState === value} onChange={() => dispatch({ type: 'patch', patch: { upperState: value }, resetAvatar: true })} />{label}
              </label>
            ))}
          </div>
          <p className="hint">Usado para manter a roupa visível no avatar base (inclusive sem camiseta). Áreas não visíveis recebem roupa neutra.</p>
        </fieldset>
        <div className="upload-row">
          <UploadButton label={photo ? 'Trocar foto' : 'Escolher foto'} variant="primary" onFile={file => choose(file)} disabled={checking} />
          <UploadButton label="Tirar selfie" icon="camera" capture="user" onFile={file => choose(file)} disabled={checking} />
        </div>
        <p className="hint">JPEG, PNG ou WEBP · até {maxMb} MB · mínimo 256 px. A orientação da câmera é respeitada e a foto nunca é esticada.</p>
        {checking && <Spinner label="Verificando a foto…" />}
        {state.photoError && <Notice kind="error" live>{state.photoError}</Notice>}
        {photo?.warnings?.length > 0 && (
          <Notice kind="warn" live><strong>Dicas para um resultado melhor:</strong><ul>{photo.warnings.map(w => <li key={w}>{w}</li>)}</ul></Notice>
        )}
        {state.photoServerError && <Notice kind="warn">Não foi possível conferir a foto no servidor agora ({state.photoServerError}). Você pode continuar; ela será validada novamente ao gerar.</Notice>}
        <details className="tips">
          <summary>Como tirar uma boa foto</summary>
          <ul>
            <li>De frente para a câmera, em pé, braços levemente afastados do corpo.</li>
            <li>Luz uniforme e fundo simples; evite contraluz e sombras fortes.</li>
            <li>Sem objetos cobrindo o corpo. Ângulos muito inclinados podem falhar.</li>
            <li>Roupas justas ou sem camiseta ajudam a IA a respeitar suas proporções.</li>
          </ul>
        </details>
      </div>
      <aside className="step-side">
        <ImageFrame src={photo?.url} alt="Prévia da foto enviada" label={photo ? `${photo.width} × ${photo.height} px` : 'Sua foto aparecerá aqui'}>
          <Icon name="user" size={48} /><span>Nenhuma foto ainda</span>
        </ImageFrame>
      </aside>
    </div>
  );
}

export function GarmentsStep({ state, dispatch, status }) {
  const [error, setError] = useState('');
  const max = status?.max_garments || 4;
  const maxMb = status?.max_upload_mb || 8;

  async function add(files) {
    setError('');
    const room = max - state.garments.length;
    if (room <= 0) { setError(`Você pode enviar até ${max} peças.`); return; }
    for (const file of files.slice(0, room)) {
      try {
        const info = await inspectImage(file, { maxMb, minSide: 128, label: 'imagem da peça' });
        dispatch({ type: 'addGarment', garment: { file, ...info } });
      } catch (e) {
        setError(e instanceof FileProblem ? `${file.name}: ${e.message}` : 'Não foi possível ler a imagem.');
      }
    }
    if (files.length > room) setError(`Somente ${room} imagem(ns) adicionada(s). O limite é ${max} peças.`);
  }

  return (
    <div className="step-stack">
      <div className="upload-row">
        <UploadButton label="Adicionar peças" variant="primary" multiple onFile={add} disabled={state.garments.length >= max} />
        <span className="hint">Até {max} peças · JPEG, PNG ou WEBP · até {maxMb} MB cada</span>
      </div>
      {error && <Notice kind="error" live>{error}</Notice>}
      {state.garments.length === 0 ? (
        <div className="empty-drop"><Icon name="shirt" size={40} /><strong>Envie a foto da roupa</strong><span>Peça inteira, de frente, sem pessoa ou cabide atrapalhando e com fundo simples. Fotos de produto funcionam melhor que desenhos.</span></div>
      ) : (
        <ul className="garment-grid">
          {state.garments.map((g, index) => (
            <li key={g.id} className="garment-card">
              <div className="garment-card__img"><img src={g.url} alt={`Peça ${index + 1}${g.description ? `: ${g.description}` : ''}`} /></div>
              <label className="field">
                <span>Descrição (opcional)</span>
                <input value={g.description} maxLength={80} placeholder="Ex.: camiseta preta básica" onChange={e => dispatch({ type: 'garment', id: g.id, patch: { description: e.target.value } })} />
              </label>
              <button className="btn btn-ghost btn-sm" onClick={() => dispatch({ type: 'removeGarment', id: g.id })}><Icon name="trash" size={16} /> Remover</button>
            </li>
          ))}
        </ul>
      )}
    </div>
  );
}

function SizeEditor({ garment, dispatch }) {
  const [draft, setDraft] = useState('');
  const addSize = () => {
    const label = draft.trim().toUpperCase().slice(0, 6);
    if (!label || garment.sizes.includes(label)) return;
    dispatch({ type: 'garment', id: garment.id, patch: { sizes: [...garment.sizes, label] } });
    setDraft('');
  };
  return (
    <div className="size-editor">
      <span className="field-label">Tamanhos disponíveis da peça</span>
      <div className="chips">
        {garment.sizes.map(size => (
          <span key={size} className="chip">{size}
            <button aria-label={`Remover tamanho ${size}`} onClick={() => dispatch({ type: 'garment', id: garment.id, patch: { sizes: garment.sizes.filter(s => s !== size), selected: garment.selected === size ? '' : garment.selected } })}><Icon name="close" size={12} /></button>
          </span>
        ))}
        <span className="chip-add">
          <input aria-label="Novo tamanho" value={draft} placeholder="+ tamanho" maxLength={6} onChange={e => setDraft(e.target.value)} onKeyDown={e => { if (e.key === 'Enter') { e.preventDefault(); addSize(); } }} />
          <button className="btn btn-ghost btn-sm" onClick={addSize}>Adicionar</button>
        </span>
      </div>
      <fieldset className="choice-group">
        <legend>Tamanho escolhido (opcional)</legend>
        <div className="segmented">
          <label className={!garment.selected ? 'is-on' : ''}><input type="radio" name={`sel-${garment.id}`} checked={!garment.selected} onChange={() => dispatch({ type: 'garment', id: garment.id, patch: { selected: '' } })} />Não informar</label>
          {garment.sizes.map(size => (
            <label key={size} className={garment.selected === size ? 'is-on' : ''}><input type="radio" name={`sel-${garment.id}`} checked={garment.selected === size} onChange={() => dispatch({ type: 'garment', id: garment.id, patch: { selected: size } })} />{size}</label>
          ))}
        </div>
      </fieldset>
    </div>
  );
}

export function MeasuresTable({ garment, dispatch, compact = false }) {
  const slot = slotOf(garment.category);
  if (!slot) return <p className="hint">Escolha a categoria para ver os campos de medida.</p>;
  const fields = SLOT_FIELDS[slot];
  if (!garment.sizes.length) return <p className="hint">Adicione tamanhos para informar medidas.</p>;
  const set = (size, key, value) => dispatch({ type: 'measure', id: garment.id, size, key, value });
  return (
    <div className={`table-wrap ${compact ? 'is-compact' : ''}`}>
      <table className="measures">
        <caption className="sr-only">Medidas da peça em centímetros por tamanho</caption>
        <thead><tr><th scope="col">Medida (cm)</th>{garment.sizes.map(size => <th scope="col" key={size}>{size}</th>)}</tr></thead>
        <tbody>
          {fields.map(([key, label]) => (
            <tr key={key}>
              <th scope="row">{label}</th>
              {garment.sizes.map(size => (
                <td key={size}><input inputMode="decimal" aria-label={`${label}, tamanho ${size}`} value={garment.measures?.[size]?.[key] ?? ''} placeholder="—" onChange={e => set(size, key, e.target.value.replace(/[^0-9.,]/g, '').slice(0, 6))} /></td>
              ))}
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}

export function BodyMeasures({ body, dispatch }) {
  return (
    <div className="body-grid">
      {BODY_FIELDS.map(([key, label]) => (
        <label key={key} className="field">
          <span>{label}</span>
          <span className="unit-input"><input inputMode="decimal" value={body[key] ?? ''} placeholder="—" onChange={e => dispatch({ type: 'body', key, value: e.target.value.replace(/[^0-9.,]/g, '').slice(0, 6) })} /><em>cm</em></span>
        </label>
      ))}
    </div>
  );
}

export function DetailsStep({ state, dispatch }) {
  return (
    <div className="step-stack">
      {state.garments.map((g, index) => {
        const slot = slotOf(g.category);
        return (
          <section key={g.id} className="detail-card" aria-labelledby={`gd-${g.id}`}>
            <div className="detail-card__img"><img src={g.url} alt="" /></div>
            <div className="detail-card__body">
              <h3 id={`gd-${g.id}`}>Peça {index + 1}{g.description ? ` · ${g.description}` : ''}</h3>
              <label className="field">
                <span>Categoria <em className="req">obrigatória</em></span>
                <select value={g.category} onChange={e => dispatch({ type: 'garment', id: g.id, patch: { category: e.target.value } })} aria-invalid={!g.category}>
                  <option value="">Escolha…</option>
                  {CATEGORIES.map(([id, label, s]) => <option key={id} value={id}>{label} — {SLOT_LABEL[s].toLowerCase()}</option>)}
                </select>
              </label>
              {slot && <p className="hint">Ao vestir, substitui a peça da região “{SLOT_LABEL[slot].toLowerCase()}”{slot === 'full' ? ' (parte de cima e de baixo)' : ''}.</p>}
              <SizeEditor garment={g} dispatch={dispatch} />
              <details className="tips">
                <summary>Medidas da peça por tamanho (opcional)</summary>
                <p className="hint">Use a tabela de medidas da loja, com a peça esticada sobre a mesa. Não estimamos centímetros pela foto.</p>
                <MeasuresTable garment={g} dispatch={dispatch} />
              </details>
            </div>
          </section>
        );
      })}
      <details className="tips detail-body">
        <summary>Suas medidas (opcional)</summary>
        <p className="hint">Com elas, a comparação mostra a folga em cada tamanho. Ficam somente nesta aba.</p>
        <BodyMeasures body={state.body} dispatch={dispatch} />
      </details>
    </div>
  );
}
