const UPPER=new Set(['camiseta','camisa','blusa','regata','casaco','jaqueta']);
export function sizeIllustration(size,category,body={}){
 const measures=size.medidas||{};
 const positive=value=>typeof value==='number'&&Number.isFinite(value)&&value>0&&value<=300?value:null;
 const width=positive(measures.largura_cm),length=positive(measures.comprimento_cm);
 let garment=null,person=null,label='';
 if(UPPER.has(category)||category==='vestido'){
  garment=positive(measures.torax_cm)||(width?width*2:null);person=positive(body.torax_cm);label='Tórax';
 }else if(['calca','bermuda','short','saia'].includes(category)){
  garment=positive(measures.quadril_cm);person=positive(body.quadril_cm);label='Quadril';
 }else if(category==='calcado'){
  garment=positive(measures.pe_cm);person=positive(body.pe_cm);label='Pé';
 }
 const difference=garment!==null&&person!==null?garment-person:null;
 return {width,length,garment,person,label,difference,caption:difference===null?'Informe a medida corporal correspondente.':`${label}: peça ${garment} cm − corpo ${person} cm = ${difference>0?'+':''}${Math.round(difference*10)/10} cm.`};
}
