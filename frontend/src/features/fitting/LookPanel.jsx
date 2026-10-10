import Icon from '../../components/ui/Icon';
import { useStore } from '../commerce/Store';
import { orderedSizes } from '../catalog/catalogModel';
import { fitOptions } from './garmentModel';
export default function LookPanel({
  currentId,
  onVisibility,
  onCurrentSize,
  onCurrentFit,
  onAddMore
}) {
  const {
    state,
    dispatch
  } = useStore();
  if (!state.look.length) return null;
  return <section className="look-panel"><div className="section-heading"><h3>Seu look</h3><button className="text-link" onClick={onAddMore}>Adicionar outra peça →</button></div><p className="muted small">Uma peça por região. A peça em teste fica em destaque.</p>{state.look.map(item => <div className="look-item" key={item.product.id}><label><input type="checkbox" checked={item.ativo} onChange={() => {dispatch({type:'TOGGLE_LOOK',id:item.product.id});onVisibility?.(item.product.id,!item.ativo);}} />{item.product.nome}</label><label>Tamanho<select aria-label={`Tamanho do look: ${item.product.nome}`} value={item.size.id} onChange={e => {
          const size = orderedSizes(item.variant).find(s => s.id === Number(e.target.value));
          dispatch({
            type: 'LOOK_SIZE',
            id: item.product.id,
            size
          });
          if (item.product.id === currentId) onCurrentSize(size.id);
        }}>{orderedSizes(item.variant).map(size => <option key={size.id} value={size.id}>{size.label}{size.estoque === 0 ? ' · sem estoque' : ''}</option>)}</select></label><label>Caimento<select aria-label={`Caimento do look: ${item.product.nome}`} value={item.fit || 'padrao'} onChange={e => {
          dispatch({
            type: 'LOOK_FIT',
            id: item.product.id,
            fit: e.target.value
          });
          if (item.product.id === currentId) onCurrentFit(e.target.value);
        }}>{fitOptions.map(([value, label]) => <option key={value} value={value}>{label}</option>)}</select></label><button aria-label={`Remover ${item.product.nome} do look`} className="icon-button" onClick={() => {dispatch({type:'REMOVE_LOOK',id:item.product.id});onVisibility?.(item.product.id,false);}}><Icon name="close" size={16} /></button></div>)}</section>;
}
