import { Component, lazy, Suspense, useEffect, useState } from 'react';
import Icon from './components/ui/Icon';
import HomePage from './features/home/HomePage';
import { DEMO_MODE } from './features/studio/api';
import './Layout.css';

// O provador só é carregado quando a pessoa entra nele (homepage mais leve).
const StudioPage = lazy(() => import('./features/studio/StudioPage'));

const ROUTES = { '': 'home', '#inicio': 'home', '#provador': 'studio', '#privacidade': 'privacy' };
// Âncoras internas (#como-funciona, #main-content) não trocam de página.
const routeOf = hash => ROUTES[hash] ?? null;
const readRoute = () => routeOf(location.hash) || 'home';

class ErrorBoundary extends Component {
  state = { error: false };
  static getDerivedStateFromError() { return { error: true }; }
  render() {
    if (!this.state.error) return this.props.children;
    return (
      <div className="page-error" role="alert">
        <h1>Algo saiu do esperado.</h1>
        <p>Recarregue a página. Suas imagens ficam somente nesta aba e não foram enviadas para armazenamento.</p>
        <button className="btn btn-primary" onClick={() => location.reload()}>Recarregar</button>
      </div>
    );
  }
}

function Brand() {
  return (
    <a className="brand" href="#inicio" aria-label="VesteIA, página inicial">
      <img src="/assets/brand/vesteia-mark.png" alt="" width="30" height="44" />
      <span>Veste<b>IA</b></span>
    </a>
  );
}

export default function App() {
  const [route, setRoute] = useState(readRoute);
  const [menu, setMenu] = useState(false);

  useEffect(() => {
    const onHash = () => {
      const next = routeOf(location.hash);
      if (!next) return;
      setRoute(previous => {
        if (previous !== next) window.scrollTo({ top: 0 });
        return next;
      });
      setMenu(false);
      if (location.hash === '#provador' || location.hash === '#inicio') document.getElementById('main-content')?.focus({ preventScroll: true });
    };
    window.addEventListener('hashchange', onHash);
    return () => window.removeEventListener('hashchange', onHash);
  }, []);

  useEffect(() => {
    document.title = route === 'studio' ? 'Provador · VesteIA' : 'VesteIA — provador virtual com inteligência artificial';
  }, [route]);

  return (
    <ErrorBoundary>
      <a className="skip-link" href="#main-content">Ir para o conteúdo</a>
      <div className="ambient" aria-hidden="true"><i /><i /><i /></div>
      <header className="site-header">
        <div className="site-header__inner">
          <Brand />
          <button className="nav-toggle" aria-expanded={menu} aria-controls="site-nav" onClick={() => setMenu(v => !v)}>
            <Icon name={menu ? 'close' : 'menu'} /><span className="sr-only">Menu</span>
          </button>
          <nav id="site-nav" className={`site-nav ${menu ? 'is-open' : ''}`} aria-label="Principal">
            <a href="#inicio" aria-current={route === 'home' ? 'page' : undefined}>Início</a>
            <a href={route === 'home' ? '#como-funciona' : '#inicio'} onClick={() => route !== 'home' && setTimeout(() => document.getElementById('como-funciona')?.scrollIntoView(), 60)}>Como funciona</a>
            <a href="#privacidade" aria-current={route === 'privacy' ? 'page' : undefined}>Privacidade</a>
            <a className="btn btn-primary btn-sm" href="#provador" aria-current={route === 'studio' ? 'page' : undefined}>
              <Icon name="sparkle" size={16} /> Experimentar com IA
            </a>
          </nav>
        </div>
      </header>
      {DEMO_MODE && <p className="demo-ribbon" role="note">Prévia de demonstração · respostas simuladas no navegador, sem IA real</p>}
      <main id="main-content" tabIndex={-1}>
        {route === 'studio' ? (
          <Suspense fallback={<div className="page-loading" role="status">Abrindo o provador…</div>}><StudioPage /></Suspense>
        ) : route === 'privacy' ? <Privacy /> : <HomePage />}
      </main>
      <footer className="site-footer">
        <div className="site-footer__inner">
          <div><Brand /><p>Veja. Escolha. Confie.</p></div>
          <p className="site-footer__note">MVP em desenvolvimento. Imagens de exemplo são ilustrativas; resultados reais dependem do provedor de IA configurado, das fotos enviadas e das medidas informadas.</p>
          <nav aria-label="Rodapé"><a href="#provador">Provador</a><a href="#privacidade">Privacidade</a></nav>
        </div>
      </footer>
    </ErrorBoundary>
  );
}

function Privacy() {
  return (
    <article className="privacy-page">
      <span className="eyebrow">Privacidade e transparência</span>
      <h1>Suas fotos, sob seu controle.</h1>
      <ul>
        <li><strong>Consentimento antes de processar.</strong> Nenhuma imagem é enviada para geração sem a sua autorização explícita, que informa se o processamento é local ou em serviço externo.</li>
        <li><strong>Sem armazenamento permanente.</strong> O servidor processa as fotos em memória e não as grava em disco ou banco. As imagens da sessão ficam apenas nesta aba do navegador.</li>
        <li><strong>Limpe quando quiser.</strong> O botão “Limpar sessão” descarta fotos, avatar e resultados e encerra a sessão no servidor.</li>
        <li><strong>Sem medidas inventadas.</strong> Uma selfie não revela medidas corporais. Partes do corpo fora da foto são estimadas e identificadas como tal; a comparação de tamanhos usa somente medidas informadas.</li>
        <li><strong>Controle de uso.</strong> Gerações só acontecem por clique, com limite por sessão e por dia. Nada é repetido automaticamente.</li>
        <li><strong>Serviços externos.</strong> Quando um provedor externo (por exemplo, a API de imagens da OpenAI) estiver ativo, as imagens são enviadas a ele somente após o consentimento, e seguem os termos desse provedor.</li>
      </ul>
      <a className="btn btn-primary" href="#provador"><Icon name="sparkle" size={18} /> Experimentar com IA</a>
    </article>
  );
}
