import { useState, useEffect, useRef } from 'react';
import AvatarVisualTabs from './AvatarVisualTabs';
import Icon from '../../components/ui/Icon';
import ProductImage from '../catalog/ProductImage';
import { money, orderedSizes, garmentColor } from '../catalog/catalogModel';
import { useStore } from '../commerce/Store';
import { focusFrame, fitOptions, garmentAppearance } from './garmentModel';
import { neutralProfile } from './avatarModel';
import SizeCard from './SizeCard';
import LookPanel from './LookPanel';
import RealisticTryOn from './RealisticTryOn';
import MeasuredPreview from './MeasuredPreview.jsx';
import useComparison from './useComparison';
export default function FittingRoom({
  product,
  onBack,
  onProfile,
  previewGender,
  onCart,
  initialVariantId,
  initialSizeId,
  onSelection
}) {
  const {
      state,
      dispatch
    } = useStore(),
    savedLook = state.look.find(item => item.product.id === product.id),
    [variantId, setVariantId] = useState(initialVariantId || savedLook?.variant.id || product.variantes[0]?.id),
    [selectedId, setSelectedId] = useState(initialSizeId || savedLook?.size.id || null),
    [preference, setPreference] = useState(savedLook?.fit || 'padrao'),
    [notice, setNotice] = useState(''),
    [gender, setGender] = useState(null),
    [outfitMode, setOutfitMode] = useState('single'),
    [hiddenCurrent,setHiddenCurrent] = useState(false),
    [framing, setFraming] = useState('full'),
    [visualMode,setVisualMode] = useState(()=>sessionStorage.getItem('vesteia:visual')==='points'?'points':'natural'),
    touch = useRef(null);
  const changeVisualMode=value=>{setVisualMode(value);sessionStorage.setItem('vesteia:visual',value);};
  const variant = product.variantes.find(v => v.id === variantId) || product.variantes[0],
    sizes = orderedSizes(variant),
    comparison = useComparison(product, variant, state.profile, preference),
    recommendation = comparison.value?.recomendacao;
  const selected = sizes.find(s => s.id === selectedId) || sizes.find(s => s.id === recommendation?.size_id) || sizes[0];
  const avatarProfile = {
    ...neutralProfile,
    ...state.profile,
    genero: (gender?.profile === state.profile ? gender.value : null) || state.profile?.genero || previewGender || (product.metadata?.publico === 'feminino' ? 'feminino' : 'masculino')
  };
  useEffect(() => {
    if (!notice) return;
    const timer = setTimeout(() => setNotice(''), 4000);
    return () => clearTimeout(timer);
  }, [notice]);
  function changeVariant(nextVariant) {
    const nextSize = orderedSizes(nextVariant)[0];
    setVariantId(nextVariant.id);
    setSelectedId(nextSize?.id || null);
    if (savedLook && nextSize) dispatch({type:'LOOK',item:{...savedLook,product,variant:nextVariant,size:nextSize,fit:preference}});
  }
  function changeFit(value) {
    setPreference(value);
    if (state.look.some(i => i.product.id === product.id)) dispatch({
      type: 'LOOK_FIT',
      id: product.id,
      fit: value
    });
  }
  function changeSize(id) {
    setSelectedId(id);
    const size = sizes.find(s => s.id === id);
    if (size && state.look.some(i => i.product.id === product.id)) dispatch({
      type: 'LOOK_SIZE',
      id: product.id,
      size
    });
  }
  function add() {
    if (!selected || selected.estoque === 0) return;
    dispatch({
      type: 'ADD',
      item: {
        size_id: selected.id,
        product_id: product.id,
        nome: product.nome,
        cor: variant.cor,
        tamanho: selected.label,
        preco: variant.preco
      }
    });
    setNotice('Peça adicionada à sacola.');
    onCart?.();
  }
  function addLook() {
    if (!selected) return;
    setOutfitMode('look');
    setHiddenCurrent(false);
    dispatch({
      type: 'LOOK',
      item: {
        product,
        variant,
        size: selected,
        fit: preference,
        ativo: true
      }
    });
    setNotice('Peça adicionada ao look. Escolha outra peça para combinar.');
  }
  function swipeEnd(e) {
    if (!touch.current) return;
    const dx = e.changedTouches[0].clientX - touch.current.x,
      dy = e.changedTouches[0].clientY - touch.current.y;
    touch.current = null;
    if (Math.abs(dx) < 45 || Math.abs(dx) < Math.abs(dy)) return;
    const index = sizes.findIndex(s => s.id === selected?.id),
      next = Math.max(0, Math.min(sizes.length - 1, index + (dx < 0 ? 1 : -1)));
    changeSize(sizes[next].id);
  }
  const favorite = state.favorites.includes(product.id);
  return <><div className="breadcrumb"><button onClick={onBack}>Catálogo</button><span>/</span><strong>{product.nome}</strong></div><div className="fitting-layout"><aside className="product-sidebar"><div className="sidebar-product-art"><ProductImage key={variant?.id} product={product} variant={variant} large /><span className="product-tag">VESTEIA</span><button className={`favorite icon-button ${favorite ? 'favorited' : ''}`} aria-label="Favoritar peça" aria-pressed={favorite} onClick={() => dispatch({
            type: 'FAVORITE',
            id: product.id
          })}><Icon name="heart" /></button></div><h2>{product.nome}</h2><strong className="sidebar-price">{money(variant?.preco)}</strong><p className="installments">Coleção demonstrativa</p><div className="divider" /><div className="sidebar-label">Cor: <strong>{variant?.cor}</strong></div><div className="swatches">{product.variantes.map(v => <button key={v.id} aria-label={`Cor ${v.cor}`} aria-pressed={variant.id === v.id} className={variant.id === v.id ? 'active' : ''} style={{
            background: garmentColor(v)
          }} onClick={() => changeVariant(v)} />)}</div><p className="fabric">{variant?.metadata?.tecido || 'Material não informado'} · {variant?.modelagem || 'regular'}</p><button className="secondary full" onClick={onProfile}><Icon name="edit" size={15} />{state.profile ? 'Editar meu avatar' : 'Criar meu avatar'}</button><p className="privacy-caption">{state.profile?.apelido || 'Manequim de exemplo'} · medidas informadas por você</p></aside>
 <section className="fitting-main"><header className="fitting-heading"><div><div className="eyebrow">SEU PROVADOR VESTEIA</div><h1>Prepare seu avatar. Experimente a peça.</h1><p>Selfie, avatar aprovado e prévia vestida — com comparação dimensional separada.</p></div></header><div className="mobile-size-tabs" style={{display:'flex',flexWrap:'wrap'}} role="group" aria-label="Tamanho da peça">{sizes.map(s=><button key={s.id} aria-pressed={selected?.id===s.id} className={selected?.id===s.id?'active':''} onClick={()=>changeSize(s.id)}>{s.label}</button>)}</div><p className="small muted">Seleção do catálogo. O CatVTON atual gera aparência, não caimento físico por tamanho.</p><RealisticTryOn key={`${product.id}-${variant.id}-${JSON.stringify(avatarProfile)}`} product={product} variant={variant} profile={avatarProfile} size={selected} onSize={changeSize}/><details className="legacy-preview"><summary>Provador 2D anterior · opcional</summary><div className="comparison-toolbar"><label>Modelo<select aria-label="Modelo do avatar" value={avatarProfile.genero} onChange={e => setGender({
              value: e.target.value,
              profile: state.profile
            })}><option value="masculino">Masculino</option><option value="feminino">Feminino</option></select></label><label>Caimento desejado<select aria-label="Caimento desejado" value={preference} onChange={e => changeFit(e.target.value)}>{fitOptions.map(([key, label]) => <option key={key} value={key}>{label}</option>)}</select></label><button className="text-link" onClick={onProfile}>Personalizar corpo →</button></div><MeasuredPreview key={`measured-${product.id}-${variant.id}-${JSON.stringify(avatarProfile)}`} product={product} variant={variant} size={selected} onSize={changeSize}/><AvatarVisualTabs value={visualMode} onChange={changeVisualMode}/>{visualMode==='points'&&<p className="guide-description">Guias visuais do avatar. A roupa, o corpo e os tamanhos permanecem iguais. Estes pontos não são uma medição detectada.</p>}<div className="fitting-view-options"><div className="outfit-controls" role="group" aria-label="Visualização das peças">{[['single', 'Peça isolada'], ['look', 'Look completo'], ['base', 'Base neutra']].map(([key, label]) => <button key={key} className={outfitMode === key ? 'active' : ''} aria-pressed={outfitMode === key} onClick={() => {setOutfitMode(key);if(key==='single')setHiddenCurrent(false);}}>{label}</button>)}</div><label className="frame-select">Enquadramento<select aria-label="Enquadramento" value={framing} onChange={e => setFraming(e.target.value)}><option value="full">Corpo inteiro</option><option value="detail">Detalhe da peça</option></select></label></div><div className="mobile-size-tabs" role="group" aria-label="Tamanho em destaque">{sizes.map(s => <button key={s.id} className={selected?.id === s.id ? 'active' : ''} aria-pressed={selected?.id === s.id} onClick={() => changeSize(s.id)}>{s.label}</button>)}</div>{outfitMode==='single'&&<p className="muted small">Somente a peça escolhida. A roupa da base é substituída por uma superfície neutra de manequim.</p>}<p className="swipe-hint">Deslize sobre o avatar para comparar os tamanhos.</p>{outfitMode!=='base'&&!garmentAppearance({product,variant,avatarGender:avatarProfile.genero}).garmentUrl&&<p className="muted small" role="status">Esta peça ainda não tem imagem preparada para uma prévia fiel. A visualização abaixo é aproximada.</p>}<div className="comparison-grid" style={{
          '--cards': Math.min(sizes.length, 4)
        }} onTouchStart={e => {
          touch.current = {
            x: e.touches[0].clientX,
            y: e.touches[0].clientY
          };
        }} onTouchEnd={swipeEnd}>{sizes.map(s => <SizeCard visualMode={visualMode} key={s.id} product={product} variant={variant} size={s} firstSize={sizes[0]} profile={avatarProfile} fit={preference} details={comparison.value?.tamanhos?.find(item => item.size_id === s.id)} active={selected?.id === s.id} recommended={recommendation?.size_id === s.id} onSelect={() => changeSize(s.id)} look={outfitMode === 'look' ? state.look : []} showProduct={outfitMode === 'single' || (outfitMode === 'look' && !hiddenCurrent)} frame={framing === 'detail' && outfitMode !== 'base' ? focusFrame(product, variant) : null} loading={comparison.loading} />)}</div>{!sizes.length && <p className="empty">Esta variante não possui tamanhos cadastrados.</p>}{comparison.error && <p className="error" role="alert">{comparison.error}</p>}
 </details><div className="recommendation-panel"><div className="recommendation-icon"><Icon name="star" size={25} /></div><div><h2>{recommendation ? <>Tamanho sugerido: <span>{recommendation.tamanho}</span></> : 'Qual tamanho combina com você?'}</h2><p>{recommendation ? 'Sugestão pelas medidas informadas e pela tabela desta variante.' : comparison.value?.mensagem || 'Informe suas medidas no avatar para receber uma sugestão.'}</p>{recommendation && <details className="recommendation-detail"><summary>Por que este tamanho? · confiança {recommendation.confianca.toLowerCase()}</summary>{recommendation.motivos.map(reason => <p key={reason}>{reason}</p>)}{recommendation.alternativa && <p>Também vale comparar o tamanho {recommendation.alternativa}.</p>}</details>}</div>{!recommendation && <button className="secondary" onClick={onProfile}>Informar medidas</button>}</div><div className="purchase-strip"><div><span>Tamanho escolhido</span><strong>{selected?.label || '—'} <small>· {variant?.cor}</small></strong></div><div className="purchase-actions">{onSelection&&<button className="primary return-size" disabled={!selected||selected.estoque===0} onClick={()=>onSelection({productId:product.id,variantId:variant.id,sizeId:selected.id})}>Usar este tamanho na loja</button>}<button className="secondary" disabled={!selected} onClick={addLook}><Icon name="user" size={17} />Adicionar ao look</button><button className="primary" disabled={!selected || selected.estoque === 0} onClick={add}><Icon name="bag" size={18} />{selected?.estoque === 0 ? 'Indisponível' : 'Adicionar à sacola'}</button></div></div><LookPanel onVisibility={(id,visible)=>{if(id===product.id)setHiddenCurrent(!visible);}} currentId={product.id} onCurrentSize={setSelectedId} onCurrentFit={setPreference} onAddMore={onBack} /><p className="visual-caption">Prévia frontal 2D ajustada por regiões. A peça varia com as medidas cadastradas, mantendo o mesmo corpo. O encaixe é aproximado; não simula a física do tecido.</p>{notice && <p className="toast" role="status"><Icon name="check" />{notice}</p>}</section></div></>;
}
