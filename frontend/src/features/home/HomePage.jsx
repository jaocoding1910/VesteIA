import { useRef, useState } from 'react';
import Icon from '../../components/ui/Icon';
import useReveal from '../../components/ui/useReveal';
import './HomePage.css';

const A = '/assets/experience/';
const STEPS = [
  ['camera', 'Envie sua foto', 'Selfie, meio corpo ou corpo inteiro, em JPEG, PNG ou WEBP. Você vê a orientação na hora.'],
  ['shirt', 'Envie a peça', 'Uma ou mais fotos de roupas: de frente, inteiras e com fundo simples.'],
  ['ruler', 'Categoria e tamanho', 'Diga o que é cada peça. Tamanho e medidas são opcionais e nunca inventados.'],
  ['user', 'Aprove o avatar base', 'Confira rosto, cabelo, tom de pele e proporções antes de seguir.'],
  ['wand', 'Vista as peças', 'A peça substitui a da mesma região; as outras do look continuam.'],
  ['compare', 'Compare e monte o look', 'Antes e depois, tamanhos lado a lado e combinações.'],
];

function MeshFigure({ className }) {
  return (
    <svg className={className} viewBox="0 0 300 420" aria-hidden="true" focusable="false">
      <defs>
        <pattern id="mesh" width="14" height="14" patternUnits="userSpaceOnUse" patternTransform="rotate(-8)">
          <path d="M14 0H0V14" fill="none" stroke="#6d7dff" strokeWidth="1" opacity=".55" />
        </pattern>
        <linearGradient id="meshFade" x1="0" y1="0" x2="0" y2="1">
          <stop offset="0" stopColor="#8fb3ff" stopOpacity=".55" />
          <stop offset="1" stopColor="#a78bfa" stopOpacity=".15" />
        </linearGradient>
      </defs>
      <path d="M150 20c30 0 52 24 52 58 0 22-9 40-22 50l4 16c46 10 82 34 92 70l14 206H10l14-206c10-36 46-60 92-70l4-16c-13-10-22-28-22-50 0-34 22-58 52-58Z" fill="url(#meshFade)" />
      <path d="M150 20c30 0 52 24 52 58 0 22-9 40-22 50l4 16c46 10 82 34 92 70l14 206H10l14-206c10-36 46-60 92-70l4-16c-13-10-22-28-22-50 0-34 22-58 52-58Z" fill="url(#mesh)" />
    </svg>
  );
}

function Wave() {
  return (
    <svg className="home-wave" viewBox="0 0 1440 220" preserveAspectRatio="none" aria-hidden="true" focusable="false">
      <defs>
        <linearGradient id="waveGrad" x1="0" x2="1">
          <stop offset="0" stopColor="#1f8bff" />
          <stop offset=".55" stopColor="#4f46e5" />
          <stop offset="1" stopColor="#8b5cf6" />
        </linearGradient>
      </defs>
      <path d="M0 120C260 40 520 210 820 150s460-120 620-60v130H0Z" fill="url(#waveGrad)" opacity=".16" />
      <path d="M0 170c300-80 560 60 860 20s420-90 580-40v70H0Z" fill="url(#waveGrad)" opacity=".28" />
    </svg>
  );
}

export default function HomePage() {
  const root = useRef(null);
  const [color, setColor] = useState('preto');
  useReveal(root);
  const look = color === 'preto' ? 'look-preto' : 'look-branco';
  const label = color === 'preto' ? 'camiseta preta' : 'camiseta branca';

  return (
    <div className="home" ref={root}>
      <section className="home-hero" aria-labelledby="hero-title">
        <div className="home-hero__copy">
          <span className="eyebrow">Provador virtual com inteligência artificial</span>
          <h1 id="hero-title">Veja a roupa <span className="grad">em você</span> antes de decidir.</h1>
          <p className="lead">Envie sua foto e a foto da peça. O VesteIA cria seu avatar base, veste a roupa escolhida e ajuda a comparar tamanhos com medidas reais — sempre com a sua aprovação em cada etapa.</p>
          <div className="home-hero__actions">
            <a className="btn btn-primary" href="#provador"><Icon name="sparkle" size={18} /> Experimentar com IA</a>
            <a className="btn btn-secondary" href="#apresentacao" onClick={e => { e.preventDefault(); document.getElementById('apresentacao')?.scrollIntoView(); document.getElementById('apresentacao-video')?.focus({ preventScroll: true }); }}>
              <Icon name="play" size={16} /> Ver apresentação
            </a>
          </div>
          <ul className="home-trust">
            <li><Icon name="lock" size={16} /> Fotos não ficam salvas</li>
            <li><Icon name="check" size={16} /> Você aprova cada geração</li>
            <li><Icon name="ruler" size={16} /> Tamanhos por medidas</li>
          </ul>
        </div>
        <div className="home-hero__stage">
          <div className="stage-glow" aria-hidden="true" />
          <MeshFigure className="stage-mesh" />
          <figure className="stage-card">
            <img key={color} src={`${A}hero-${color}.webp`} width="1024" height="1536" alt={`Exemplo ilustrativo: avatar de referência vestindo ${label}, calça escura e tênis brancos`} fetchpriority="high" />
            <figcaption><span className="badge">Exemplo ilustrativo</span></figcaption>
          </figure>
          <div className="stage-chip" role="group" aria-label="Cor da camiseta no exemplo">
            <img src={`${A}camiseta-${color === 'preto' ? 'preta' : 'branca'}.webp`} alt="" width="56" height="56" />
            <div>
              <small>Peça do exemplo</small>
              <strong>Camiseta básica</strong>
              <div className="swatches">
                {[['preto', 'Preta'], ['branco', 'Branca']].map(([value, name]) => (
                  <button key={value} className={`swatch swatch--${value}`} aria-pressed={color === value} onClick={() => setColor(value)}>
                    <span className="sr-only">Mostrar exemplo com camiseta {name.toLowerCase()}</span>
                  </button>
                ))}
              </div>
            </div>
          </div>
        </div>
        <Wave />
      </section>

      <section id="apresentacao" className="home-section home-video" aria-labelledby="video-title">
        <div className="section-head" data-reveal>
          <span className="eyebrow">Apresentação</span>
          <h2 id="video-title">Conheça a proposta em 30 segundos.</h2>
          <p>Da escolha da peça à comparação de tamanhos. O vídeo só começa quando você der o play.</p>
        </div>
        <div className="video-frame" data-reveal data-reveal-delay="1">
          <video id="apresentacao-video" controls playsInline preload="none" poster={`${A}apresentacao-capa.webp`} width="1920" height="1080"
            aria-describedby="video-note">
            <source src={`${A}apresentacao.mp4`} type="video/mp4" />
            Seu navegador não reproduz vídeos. <a href={`${A}apresentacao.mp4`}>Baixe a apresentação</a>.
          </video>
        </div>
        <p id="video-note" className="fineprint" data-reveal>Apresentação conceitual com imagens ilustrativas. O projeto está em desenvolvimento.</p>
      </section>

      <section id="como-funciona" className="home-section" aria-labelledby="steps-title">
        <div className="section-head" data-reveal>
          <span className="eyebrow">Como funciona</span>
          <h2 id="steps-title">Seis passos, você no controle.</h2>
          <p>Nada é gerado sem um clique seu. Antes de cada geração, o provador mostra quantas chamadas serão feitas.</p>
        </div>
        <ol className="steps-grid">
          {STEPS.map(([icon, title, body], index) => (
            <li key={title} className="step-card" data-reveal data-reveal-delay={String(index % 3)}>
              <span className="step-card__icon"><Icon name={icon} size={22} /></span>
              <span className="step-card__num">{String(index + 1).padStart(2, '0')}</span>
              <h3>{title}</h3>
              <p>{body}</p>
            </li>
          ))}
        </ol>
        <div className="center" data-reveal><a className="btn btn-primary" href="#provador"><Icon name="sparkle" size={18} /> Experimentar com IA</a></div>
      </section>

      <section className="home-section home-split" aria-labelledby="before-title">
        <div className="section-head" data-reveal>
          <span className="eyebrow">Antes e depois</span>
          <h2 id="before-title">A mesma pessoa, com a peça escolhida.</h2>
          <p>O avatar base preserva rosto, cabelo, tom de pele e proporções visíveis. A peça substitui apenas a roupa da mesma região, mantendo pose, fundo e enquadramento.</p>
          <div className="swatch-row" role="group" aria-label="Cor da camiseta no exemplo">
            <span>Cor da camiseta:</span>
            {[['preto', 'Preta'], ['branco', 'Branca']].map(([value, name]) => (
              <button key={value} className={`swatch swatch--${value}`} aria-pressed={color === value} onClick={() => setColor(value)}>
                <span className="sr-only">Mostrar exemplo com camiseta {name.toLowerCase()}</span>
              </button>
            ))}
          </div>
          <span className="badge badge-warn">Exemplo ilustrativo · imagens geradas previamente, não pela aplicação</span>
        </div>
        <div className="before-after" data-reveal data-reveal-delay="1">
          <figure><img src={`${A}avatar-base.webp`} width="1024" height="1536" loading="lazy" alt="Exemplo ilustrativo de avatar base: homem sem camiseta, de calça escura e tênis brancos" /><figcaption>Avatar base</figcaption></figure>
          <span className="before-after__arrow" aria-hidden="true"><Icon name="arrow" size={22} /></span>
          <figure><img src={`${A}${look}.webp`} width="1024" height="1536" loading="lazy" alt={`Exemplo ilustrativo: a mesma pessoa com ${label}`} /><figcaption>Com a {label}</figcaption></figure>
        </div>
      </section>

      <section className="home-section home-sizes" aria-labelledby="sizes-title">
        <div className="section-head" data-reveal>
          <span className="eyebrow">Comparar tamanhos</span>
          <h2 id="sizes-title">Tamanho é medida, não etiqueta.</h2>
          <p>P nem sempre é justo e GG nem sempre é oversized: depende das medidas da peça e do corpo. O VesteIA compara largura, comprimento, mangas, cintura, quadril e entrepernas — e avisa quando faltar alguma medida, sem inventar centímetros.</p>
        </div>
        <figure className="sizes-figure" data-reveal data-reveal-delay="1">
          <img src={`${A}tamanhos-${color}.webp`} width="1536" height="1024" loading="lazy" alt="Comparação ilustrativa da mesma camiseta nos tamanhos P, M, G e GG" />
          <figcaption><span className="badge badge-warn">Comparação ilustrativa</span> O caimento real depende das medidas da peça e do cliente.</figcaption>
        </figure>
      </section>

      <section className="home-section" aria-labelledby="trust-title">
        <div className="section-head" data-reveal>
          <span className="eyebrow">Transparência</span>
          <h2 id="trust-title">Honesto sobre o que a IA faz.</h2>
        </div>
        <div className="trust-grid">
          {[
            ['shield', 'Consentimento primeiro', 'Antes de processar, você vê se a imagem vai para um serviço local ou externo — e autoriza.'],
            ['lock', 'Sem armazenamento', 'Fotos e resultados ficam só nesta aba. “Limpar sessão” descarta tudo.'],
            ['info', 'Regiões estimadas', 'Se a foto não mostra o corpo inteiro, o restante é estimado e identificado. Selfie não revela medidas.'],
            ['refresh', 'Custo sob controle', 'Gerações só por clique, com limite por sessão e por dia, sem repetição automática.'],
          ].map(([icon, title, body], index) => (
            <article key={title} className="trust-card" data-reveal data-reveal-delay={String(index % 3)}>
              <Icon name={icon} size={22} />
              <h3>{title}</h3>
              <p>{body}</p>
            </article>
          ))}
        </div>
      </section>

      <section className="home-cta" aria-labelledby="cta-title" data-reveal>
        <img src="/assets/brand/vesteia-mark.png" alt="" width="64" height="94" />
        <h2 id="cta-title">Veja. Escolha. Confie.</h2>
        <p>Experimente com a sua foto. Leva poucos minutos e você aprova cada passo.</p>
        <a className="btn btn-light" href="#provador"><Icon name="sparkle" size={18} /> Experimentar com IA</a>
      </section>
    </div>
  );
}
