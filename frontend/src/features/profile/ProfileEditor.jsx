import AvatarControls from './AvatarControls';
import { useState } from 'react';
import Modal from '../../components/ui/Modal';
import { useStore } from '../commerce/Store';
import { request, jsonBody } from '../../services/mvpApi';
import AvatarVisualTabs from '../fitting/AvatarVisualTabs';
import AvatarView from '../fitting/AvatarView';
import { neutralProfile } from '../fitting/avatarModel';
import PhotoAvatarSource from './PhotoAvatarSource';
const fields = [['altura_aproximada_cm', 'Altura', 'cm', 100, 230], ['peso_aproximado_kg', 'Peso', 'kg', 25, 300], ['ombros_cm', 'Ombros', 'cm', 15, 90], ['torax_cm', 'Tórax', 'cm', 40, 250], ['cintura_cm', 'Cintura', 'cm', 30, 250], ['quadril_cm', 'Quadril', 'cm', 40, 250], ['pe_cm', 'Comprimento do pé', 'cm', 10, 40]];
export default function ProfileEditor({
  onClose,
  onComplete,
  legacyId
}) {
  const {
      state,
      dispatch
    } = useStore(),
    [profile, setProfile] = useState({
      ...neutralProfile,
      ...state.profile,
      medidas: {
        ...state.profile?.medidas
      }
    }),
    [source, setSource] = useState('manual'),
    [visualMode,setVisualMode] = useState('natural'),
    [busy, setBusy] = useState(false),
    [error, setError] = useState('');
  const set = (key, value) => setProfile(p => ({
    ...p,
    [key]: value
  }));
  async function finish(e) {
    e.preventDefault();
    setBusy(true);
    setError('');
    const id = state.profileId || crypto.randomUUID();
    try {
      const value = {
        ...profile,
        proporcao_tronco: ['curto','media','longo'].includes(profile.proporcao_tronco)?profile.proporcao_tronco:'media',
        apelido: profile.apelido.trim() || 'Você'
      };
      await request(`/mvp/perfis/${id}`, {
        ...jsonBody(value),
        method: 'PUT'
      });
      dispatch({
        type: 'PROFILE',
        profile: value,
        id
      });
      onComplete();
    } catch (e) {
      setError(e.message);
    } finally {
      setBusy(false);
    }
  }
  return <Modal title="Seu avatar VesteIA" onClose={onClose}><form onSubmit={finish}><div className="avatar-editor-layout"><aside className="avatar-editor-preview"><AvatarVisualTabs value={visualMode} onChange={setVisualMode}/><AvatarView profile={profile} cleanPreview visualMode={visualMode}/>{visualMode==='points'&&<small>Guias ilustrativos do molde; não são medidas detectadas.</small>}<span>Prévia do seu avatar · 2D</span></aside><div className="avatar-editor-controls"><label className="field">Apelido<input autoFocus value={profile.apelido} maxLength={60} onChange={e => set('apelido', e.target.value)} /></label><div className="segmented" role="group" aria-label="Origem do avatar"><button type="button" className={source === 'manual' ? 'active' : ''} aria-pressed={source === 'manual'} onClick={() => setSource('manual')}>Personalizar</button><button type="button" className={source === 'foto' ? 'active' : ''} aria-pressed={source === 'foto'} onClick={() => setSource('foto')}>Usar foto como referência</button></div>{source === 'foto' && <PhotoAvatarSource legacyId={legacyId} onApply={config => setProfile(p => ({
            ...p,
            ...config
          }))} />}
 <label className="field">Acabamento do avatar<select aria-label="Acabamento do avatar" value={profile.estilo_avatar} onChange={e => set('estilo_avatar',e.target.value)}><option value="humano">Humano · rosto e corpo liso</option><option value="manequim">Manequim neutro</option></select></label><div className="field">Modelo<div className="segmented">{['masculino', 'feminino'].map(v => <button type="button" key={v} aria-pressed={profile.genero === v} className={profile.genero === v ? 'active' : ''} onClick={() => set('genero', v)}>{v === 'masculino' ? 'Masculino' : 'Feminino'}</button>)}</div></div><AvatarControls profile={profile} set={set}/> {profile.estilo_avatar==='humano'&&<p className="muted small">O modelo humano permite ajustar pele, cabelo e cor. Quatro estilos de cabelo, cores naturais e pele ajustável. O rosto permanece o da base; o corpo usa uma superfície lisa.</p>}<details className="body-measures"><summary>Medidas para recomendar tamanhos</summary><p className="muted">Informe somente o que conhece. Tórax, cintura e quadril são circunferências; ombros são a distância entre as pontas.</p><div className="measure-fields">{fields.map(([key, label, unit, min, max]) => <label className="field" key={key}>{label} ({unit})<input type="number" min={min} max={max} step=".1" placeholder="Opcional" value={['peso_aproximado_kg','altura_aproximada_cm'].includes(key) ? profile[key] ?? '' : profile.medidas[key] ?? ''} onChange={e => {
                  const value = e.target.value === '' ? null : Number(e.target.value);
                  if (['peso_aproximado_kg','altura_aproximada_cm'].includes(key)) set(key, value);else setProfile(p => {
                    const medidas = {
                      ...p.medidas
                    };
                    if (value === null) delete medidas[key];else medidas[key] = value;
                    return {
                      ...p,
                      medidas
                    };
                  });
                }} /></label>)}</div></details><p className="muted small">Aparência e proporções são visuais. A recomendação usa suas medidas informadas.</p></div></div>{error && <p className="error" role="alert">{error}</p>}<button className="primary full" disabled={busy}>{busy ? 'Salvando…' : 'Salvar meu avatar'}</button></form></Modal>;
}
