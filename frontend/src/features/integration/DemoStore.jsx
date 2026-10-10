import {useCallback,useEffect,useRef,useState} from 'react';
import ProductImage from '../catalog/ProductImage';
import {money,orderedSizes,garmentColor} from '../catalog/catalogModel';
import Modal from '../../components/ui/Modal';
import Icon from '../../components/ui/Icon';
import {embedUrl,PROTOCOL,validSelection} from './embedProtocol';
function StoreProduct({product,onBack}){
 const [variantId,setVariantId]=useState(product.variantes[0]?.id),[sizeId,setSizeId]=useState(null),[session,setSession]=useState(null),[notice,setNotice]=useState('');
 const frame=useRef(null),variant=product.variantes.find(v=>v.id===variantId)||product.variantes[0],sizes=orderedSizes(variant),size=sizes.find(s=>s.id===sizeId),close=useCallback(()=>setSession(null),[]);
 useEffect(()=>{
  if(!session)return;
  const receive=event=>{
   if(event.origin!==location.origin||event.source!==frame.current?.contentWindow||event.data?.protocol!==PROTOCOL||event.data.channel!==session.channel||event.data.productId!==product.id)return;
   if(event.data.type==='close'){close();return;}
   const selected=validSelection(event.data,product,session.channel);if(!selected)return;
   setVariantId(selected.variant.id);setSizeId(selected.size.id);setNotice(`Escolha aplicada: ${selected.size.label} · ${selected.variant.cor}.`);close();
  };window.addEventListener('message',receive);return()=>window.removeEventListener('message',receive);
 },[session,product,close]);
 const open=()=>{const channel=crypto.randomUUID();setSession({channel,url:embedUrl(product,variant,size,channel)});setNotice('');};
 return <><button className="text-link demo-back" onClick={onBack}>← Voltar à coleção</button><div className="demo-product"><div className="demo-photo"><ProductImage key={variant.id} product={product} variant={variant} large/></div><section className="demo-product-info"><div className="eyebrow">FORMA / COLEÇÃO DEMONSTRATIVA</div><h1>{product.nome}</h1><p>{product.descricao||'Peça de catálogo para testar a integração com o provador.'}</p><strong className="demo-price">{money(variant.preco)}</strong><small>Preço demonstrativo · sem cobrança</small><label className="field">Cor: {variant.cor}</label><div className="swatches">{product.variantes.map(v=><button key={v.id} aria-label={`Escolher cor ${v.cor}`} aria-pressed={variant.id===v.id} className={variant.id===v.id?'active':''} style={{background:garmentColor(v)}} onClick={()=>{setVariantId(v.id);setSizeId(null);setNotice('');}}/>)}</div><fieldset className="demo-sizes"><legend>Tamanho</legend>{sizes.map(s=><button key={s.id} aria-label={`Escolher tamanho ${s.label}`} aria-pressed={sizeId===s.id} disabled={s.estoque===0} className={sizeId===s.id?'active':''} onClick={()=>{setSizeId(s.id);setNotice('');}}>{s.label}</button>)}</fieldset><button className="secondary demo-try" onClick={open}><Icon name="sparkle"/>Experimentar com VesteIA</button><p className="small muted">Compare os tamanhos no avatar e devolva sua escolha à loja.</p><button className="primary full" disabled={!size||size.estoque===0} onClick={()=>setNotice(`Compra demonstrativa: ${product.nome}, ${size.label}, ${variant.cor}. Nenhum pedido ou pagamento foi criado.`)}>Continuar compra demonstrativa</button><p className="demo-payment">Pix · Cartão · Boleto — apresentação demonstrativa</p>{notice&&<p className="success" role="status">{notice}</p>}<details className="demo-table"><summary>Medidas da peça e disponibilidade</summary>{sizes.map(s=><p key={s.id}><strong>{s.label}</strong> · {Object.entries(s.medidas||{}).map(([k,v])=>`${k.replace('_cm','').replace('_',' ')}: ${v} cm`).join(' · ')} · estoque {s.estoque??'a consultar'}</p>)}</details></section></div>{session&&<Modal title="Provador VesteIA · loja FORMA" onClose={close}><iframe ref={frame} title="Provador virtual da peça selecionada" className="demo-iframe" src={session.url}/><p className="small muted">Ao usar o tamanho, a seleção retorna a esta página. O pagamento permanece na loja.</p></Modal>}</>;
}
export default function DemoStore({products}){
 const [selectedId,setSelectedId]=useState(null);
 const demo=products.filter(p=>p.metadata?.loja_demo==='forma');
 const collection=demo.length?demo:products.filter(p=>['camiseta','calca','short','vestido'].includes(p.categoria)).filter((p,i,a)=>a.findIndex(q=>q.categoria===p.categoria)===i);
 const selected=collection.find(p=>p.id===selectedId);
 return <section className="demo-store"><header className="demo-store-header"><button onClick={()=>setSelectedId(null)} className="demo-brand">FORMA<span>studio</span></button><span>Loja demonstrativa · integração VesteIA</span><a href="#inicio">Voltar ao VesteIA ↗</a></header>{selected?<StoreProduct key={selected.id} product={selected} onBack={()=>setSelectedId(null)}/>:<><div className="demo-store-intro"><div className="eyebrow">ESCOLHA. EXPERIMENTE. COMPARE.</div><h1>Antes da compra,<br/>uma nova perspectiva.</h1><p>Uma coleção pequena para testar o provador dentro da página de produto.</p></div>{!demo.length&&<p className="demo-note">Mostrando peças do catálogo atual. Para testar a coleção FORMA, siga as instruções do banco demonstrativo.</p>}<div className="demo-store-grid">{collection.map(p=><article key={p.id}><button aria-label={`Abrir ${p.nome} na loja`} onClick={()=>setSelectedId(p.id)}><div className="demo-photo"><ProductImage product={p} variant={p.variantes[0]}/></div><h2>{p.nome}</h2><p>{money(p.variantes[0]?.preco)}</p><span>Ver peça e experimentar →</span></button></article>)}</div></>}</section>;
}
