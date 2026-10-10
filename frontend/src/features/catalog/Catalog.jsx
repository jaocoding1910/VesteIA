import { useState } from 'react';

import Icon from '../../components/ui/Icon';
import ProductImage from './ProductImage';
import { categories, money } from './catalogModel';
import { useStore } from '../commerce/Store';
export default function Catalog({
  products,
  search,
  publico,
  onOpen,
  favoritesOnly = false
}) {
  const [category, setCategory] = useState('todos'),
    [collection, setCollection] = useState('principal');
  const {
    state,
    dispatch
  } = useStore();
  const filtered = products.filter(p => (favoritesOnly || collection === 'completa' || !products.some(i => i.metadata?.principal_mvp) || p.metadata?.principal_mvp) && (category === 'todos' || p.categoria === category) && (!favoritesOnly || state.favorites.includes(p.id)) && (!publico || p.metadata?.publico === publico || p.metadata?.publico === 'unissex') && p.nome.toLocaleLowerCase().includes(search.toLocaleLowerCase()));
  return <>{favoritesOnly ? <section className="collection-intro" data-reveal><div><div className="eyebrow">GUARDADO PARA VOCÊ</div><h1>Suas peças favoritas.</h1><p>Volte às escolhas que merecem outra prova.</p></div></section> : <section className="collection-intro" data-reveal><div><div className="eyebrow">EXPLORE SEU ESTILO</div><h1>{publico==='feminino'?'Coleção feminina.':publico==='masculino'?'Coleção masculina.':'Sua próxima escolha.'}</h1><p>Peças para experimentar no seu avatar.</p></div></section>}
 <div id="colecao" className="catalog-bar" data-reveal><h2>{favoritesOnly ? 'Favoritos' : 'Coleção Essential'} <small>{filtered.length} peças</small></h2><span>Catálogo demonstrativo</span></div><div className="category-tabs"><button className={collection === 'principal' ? 'active' : ''} onClick={() => {
        setCollection('principal');
        setCategory('todos');
      }}>MVP VesteIA</button><button className={collection === 'completa' ? 'active' : ''} onClick={() => setCollection('completa')}>Coleção completa</button>{(collection === 'completa' ? categories : categories.filter(([key]) => ['todos', 'camiseta', 'calca'].includes(key))).map(([key, label]) => <button key={key} className={category === key ? 'active' : ''} onClick={() => setCategory(key)}>{label}</button>)}</div>
 {filtered.length === 0 ? <div className="empty"><Icon name="bag" size={38} /><h3>Nenhuma peça por aqui</h3><p>Experimente outra busca ou marque uma peça como favorita.</p></div> : <div className="product-grid">{filtered.map(p => {
        const v = p.variantes[0];
        return <article className="product-tile" data-reveal key={p.id}><div className="tile-art"><button className="tile-image-button" onClick={() => onOpen(p.id)} aria-label={`Ver ${p.nome}`}><ProductImage product={p} variant={v} /></button><span className="product-tag">ESSENTIAL</span><button className={`favorite icon-button ${state.favorites.includes(p.id) ? 'favorited' : ''}`} aria-label={`${state.favorites.includes(p.id) ? 'Remover dos' : 'Adicionar aos'} favoritos: ${p.nome}`} aria-pressed={state.favorites.includes(p.id)} onClick={() => dispatch({
              type: 'FAVORITE',
              id: p.id
            })}><Icon name="heart" /></button></div><div className="tile-info"><span>{p.marca || 'VesteIA'} / {p.categoria}</span><button className="text-link product-name" onClick={() => onOpen(p.id)}>{p.nome}</button><div className="tile-price"><strong>{money(v?.preco)}</strong><small>{v?.tamanhos.length} tamanhos</small></div><button className="try-button" onClick={() => onOpen(p.id)}><Icon name="sparkle" size={16} /> Experimentar <Icon name="arrow" size={16} /></button></div></article>;
      })}</div>}</>;
}
