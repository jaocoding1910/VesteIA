// Validação local de imagens antes do envio (o backend valida de novo).
const SIGNATURES = [
  { type: 'image/jpeg', test: b => b[0] === 0xff && b[1] === 0xd8 && b[2] === 0xff },
  { type: 'image/png', test: b => b[0] === 0x89 && b[1] === 0x50 && b[2] === 0x4e && b[3] === 0x47 },
  { type: 'image/webp', test: b => b[0] === 0x52 && b[1] === 0x49 && b[2] === 0x46 && b[3] === 0x46 && b[8] === 0x57 && b[9] === 0x45 && b[10] === 0x42 && b[11] === 0x50 },
];

export class FileProblem extends Error {}

export async function inspectImage(file, { maxMb = 8, minSide = 256, label = 'imagem' } = {}) {
  if (!file) throw new FileProblem(`Escolha uma ${label}.`);
  if (file.size > maxMb * 1024 * 1024) throw new FileProblem(`A ${label} tem ${(file.size / 1048576).toFixed(1)} MB. O limite é ${maxMb} MB.`);
  const head = new Uint8Array(await file.slice(0, 16).arrayBuffer());
  const kind = SIGNATURES.find(s => s.test(head));
  if (!kind) throw new FileProblem(`A ${label} precisa ser JPEG, PNG ou WEBP.`);
  let width, height;
  try {
    // Respeita a orientação EXIF da câmera do celular.
    const bitmap = await createImageBitmap(file, { imageOrientation: 'from-image' });
    width = bitmap.width; height = bitmap.height; bitmap.close?.();
  } catch {
    throw new FileProblem(`Não foi possível abrir a ${label}. O arquivo pode estar corrompido.`);
  }
  if (Math.min(width, height) < minSide) throw new FileProblem(`A ${label} é pequena demais (${width}×${height}). Use pelo menos ${minSide} px no menor lado.`);
  return { type: kind.type, width, height, url: URL.createObjectURL(file) };
}

export async function dataUrlToBlob(dataUrl) {
  const response = await fetch(dataUrl);
  return response.blob();
}

export function download(dataUrl, name) {
  const link = document.createElement('a');
  link.href = dataUrl;
  link.download = name;
  document.body.appendChild(link);
  link.click();
  link.remove();
}
