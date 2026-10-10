import { useEffect, useId, useRef } from 'react';
import Icon from '../../components/ui/Icon';

/** Moldura retrato 2:3; a imagem é contida (nunca esticada). */
export function ImageFrame({ src, alt, label, badge, children, tone = 'default' }) {
  return (
    <figure className={`frame frame--${tone}`}>
      <div className="frame__box">
        {src ? <img src={src} alt={alt} /> : <div className="frame__empty">{children}</div>}
        {badge && <span className="frame__badge">{badge}</span>}
      </div>
      {label && <figcaption>{label}</figcaption>}
    </figure>
  );
}

export function Notice({ kind = 'info', icon, children, live = false }) {
  const icons = { info: 'info', warn: 'alert', error: 'alert', ok: 'check', sim: 'sparkle' };
  return (
    <div className={`notice notice-${kind}`} role={live ? (kind === 'error' ? 'alert' : 'status') : undefined}>
      <Icon name={icon || icons[kind]} size={18} />
      <div>{children}</div>
    </div>
  );
}

export function CallsInfo({ calls, remaining, paid, simulated }) {
  if (calls === 0) return <p className="calls"><Icon name="check" size={16} /> Esta etapa não usa IA: nenhuma geração será solicitada.</p>;
  const over = remaining !== null && calls > remaining;
  return (
    <p className={`calls ${over ? 'calls--over' : ''}`}>
      <Icon name="layers" size={16} />
      <span>
        {calls > 1 ? 'Serão solicitadas' : 'Será solicitada'} <strong>{calls} {calls > 1 ? 'gerações' : 'geração'}</strong>
        {paid ? ' com custo no provedor' : simulated ? (calls > 1 ? ' simuladas' : ' simulada') + ', sem custo' : ' locais, sem custo de API'}.
        {remaining !== null && <> Restam {remaining} nesta sessão.</>}
      </span>
    </p>
  );
}

export function ConfirmDialog({ open, title, children, confirmLabel, onConfirm, onCancel }) {
  const ref = useRef(null);
  const titleId = useId();
  useEffect(() => {
    const dialog = ref.current;
    if (!dialog) return;
    if (open && !dialog.open) dialog.showModal?.();
    if (!open && dialog.open) dialog.close();
  }, [open]);
  return (
    <dialog ref={ref} className="confirm" aria-labelledby={titleId} onCancel={e => { e.preventDefault(); onCancel(); }}>
      <h2 id={titleId}>{title}</h2>
      <div className="confirm__body">{children}</div>
      <div className="confirm__actions">
        <button className="btn btn-secondary" onClick={onCancel}>Cancelar</button>
        <button className="btn btn-primary" onClick={onConfirm} autoFocus>{confirmLabel}</button>
      </div>
    </dialog>
  );
}

export function Spinner({ label }) {
  return <span className="spinner" role="status"><i aria-hidden="true" />{label}</span>;
}

export function ProviderBadge({ caps }) {
  if (!caps) return null;
  if (caps.kind === 'simulated') return <span className="badge badge-sim">Simulado · sem IA</span>;
  if (caps.kind === 'none') return <span className="badge">Sem IA</span>;
  if (caps.paid) return <span className="badge badge-paid">Externo · com custo</span>;
  return <span className="badge badge-ok">Local · sem custo de API</span>;
}
