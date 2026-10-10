import {useState} from 'react';
import useCatalog from '../catalog/useCatalog';
import FittingRoom from '../fitting/FittingRoom';
import ProfileEditor from '../profile/ProfileEditor';
import {PROTOCOL} from './embedProtocol';
export default function EmbeddedFitting({config}){
 const catalog=useCatalog(),[profileOpen,setProfileOpen]=useState(false),product=catalog.data.find(p=>p.id===config.productId);
 const send=(type,selection={})=>{if(window.parent!==window)window.parent.postMessage({protocol:PROTOCOL,type,channel:config.channel,productId:config.productId,...selection},location.origin);};
 return <div className="experience embedded-fitting"><header className="embedded-header"><a href="#inicio" target="_blank" rel="noopener">Veste<span>IA</span></a><span>Experimente antes de escolher.</span><button onClick={()=>send('close')}>Fechar provador ×</button></header><main className="site-main">{catalog.loading?<p role="status">Preparando a peça…</p>:catalog.error?<div className="empty"><p role="alert">{catalog.error}</p><button onClick={catalog.retry}>Tentar novamente</button></div>:product?<FittingRoom key={product.id} product={product} onBack={()=>send('close')} onProfile={()=>setProfileOpen(true)} initialVariantId={config.variantId} initialSizeId={config.sizeId} onSelection={selection=>send('selection',selection)}/>:<p role="alert">Produto não encontrado no catálogo conectado.</p>}</main>{profileOpen&&product&&<ProfileEditor legacyId={product.variantes[0]?.tamanhos[0]?.legacy_product_id} onClose={()=>setProfileOpen(false)} onComplete={()=>setProfileOpen(false)}/>}</div>;
}
