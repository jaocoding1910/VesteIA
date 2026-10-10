import AvatarView from './AvatarView';
import { garmentDimensions, garmentAppearance } from './garmentModel';
import { measureLabels } from '../catalog/catalogModel';
export default function SizeCard({
  product,
  variant,
  size,
  firstSize,
  profile,
  fit,
  details,
  active,
  recommended,
  onSelect,
  look,
  showProduct,
  frame,
  loading,
  visualMode
}) {
  const dims = garmentDimensions({
      product,
      variant,
      size,
      fit
    }),
    base = garmentDimensions({
      product,
      variant,
      size: firstSize
    }),
    appearance = garmentAppearance({
      product,
      variant,
      size
    }),
    difference = dims.width - base.width;
  return <article className={`size-card ${active ? 'selected' : ''} ${recommended ? 'recommended' : ''}`} data-size={size.label}><button className="size-card-select" aria-label={`Selecionar tamanho ${size.label}`} aria-pressed={active} onClick={onSelect}><div className="size-card-top"><strong>{size.label}</strong>{recommended ? <span>Sugerido</span> : active ? <span>Selecionado</span> : null}</div><div className="avatar-stage"><AvatarView profile={profile} product={product} variant={variant} size={size} fit={fit} look={look} showProduct={showProduct} frame={frame} visualMode={visualMode} /></div><div className="fit-label"><span className="fit-dot" />{loading ? 'Comparando…' : details?.caimento && details.caimento !== 'Sem medidas suficientes' ? details.caimento : 'Prévia do tamanho'}</div></button><div className="card-size-summary">{dims.hasWidth && <span>{dims.width} cm de largura</span>}{dims.hasLength && <span>{dims.length} cm de {product.categoria === 'calcado' ? 'pé' : 'comprimento'}</span>}</div><div className="size-delta">{dims.hasWidth ? `${difference > 0 ? '+' : ''}${Number(difference.toFixed(1))} cm de largura vs. ${firstSize.label}` : 'Largura não cadastrada'}</div><details className="card-measures"><summary>Tabela e aparência</summary><dl className="garment-data">{Object.entries(size.medidas || {}).map(([key, value]) => <div key={key}><dt>{measureLabels[key] || key}</dt><dd>{value} cm</dd></div>)}</dl><p>{appearance.printUrl || appearance.printText ? 'Estampa cadastrada' : appearance.textureUrl ? 'Foto projetada em 2D' : 'Cor cadastrada'}</p></details><div className="size-stock">{size.estoque === 0 ? 'Indisponível' : size.estoque == null ? 'Disponibilidade a consultar' : `${size.estoque} disponíveis`}</div></article>;
}
