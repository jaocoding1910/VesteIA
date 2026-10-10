import { useState } from 'react';
import Icon from '../../components/ui/Icon';
import { useStore } from './Store';
import { money } from '../catalog/catalogModel';
import { request, jsonBody } from '../../services/mvpApi';
export default function Cart({
  onShop,
  onOpen
}) {
  const {
    state,
    dispatch
  } = useStore();
  const [error, setError] = useState(''),
    [validated, setValidated] = useState(null),
    [busy, setBusy] = useState(false);
  async function validate() {
    setBusy(true);
    setError('');
    setValidated(null);
    try {
      setValidated(await request('/mvp/carrinho/validar', jsonBody(state.cart.map(i => ({
        size_id: i.size_id,
        quantidade: i.quantidade
      })))));
    } catch (e) {
      setError(e.message);
    } finally {
      setBusy(false);
    }
  }
  function quantity(item, value) {
    setValidated(null);
    dispatch({
      type: 'QUANTITY',
      id: item.size_id,
      quantidade: value
    });
  }
  return <section className="cart-page"><div className="eyebrow">SUAS ESCOLHAS</div><h1>Minha sacola.</h1><p className="muted">Confira cores e tamanhos antes de continuar.</p>{!state.cart.length ? <div className="empty"><Icon name="bag" size={46} /><h2>Sua sacola está esperando seu estilo.</h2><button className="primary" onClick={onShop}>Explorar coleção <Icon name="arrow" /></button></div> : <div className="cart-layout"><div className="cart-items">{state.cart.map(item => <article key={item.size_id}><div className="cart-item-icon"><Icon name="bag" size={30} /></div><div className="cart-item-name"><button className="text-link" onClick={() => onOpen(item.product_id)}>{item.nome}</button><p>{item.cor} · Tamanho {item.tamanho}</p><strong>{money(validated?.itens.find(i => i.size_id === item.size_id)?.preco ?? item.preco)}</strong></div><label className="field">Qtd.<input aria-label={`Quantidade de ${item.nome}`} type="number" min="1" max="99" value={item.quantidade} onChange={e => quantity(item, Math.max(1, Math.min(99, Number(e.target.value) || 1)))} /></label><button className="icon-button" aria-label={`Remover ${item.nome}`} onClick={() => quantity(item, 0)}><Icon name="close" /></button></article>)}</div><aside className="cart-summary"><h2>Resumo</h2><div><span>{state.cart.reduce((n, i) => n + i.quantidade, 0)} peças</span><strong>{money(validated?.total ?? state.cart.reduce((n, i) => n + i.preco * i.quantidade, 0))}</strong></div><p className="muted small">Os preços e a disponibilidade são conferidos na API. Esta sacola não reserva estoque.</p><button className="primary full" onClick={validate} disabled={busy}>{busy ? 'Conferindo…' : 'Conferir disponibilidade'}</button>{error && <p role="alert" className="error">{error}</p>}{validated && <p role="status" className="success">Itens disponíveis. Total atualizado: {money(validated.total)}.</p>}<p className="privacy-caption"><Icon name="info" size={15} /> O MVP termina na seleção das peças. Pagamento e frete ainda não estão integrados.</p></aside></div>}</section>;
}
