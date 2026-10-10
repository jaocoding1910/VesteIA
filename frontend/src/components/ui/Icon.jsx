const paths = {
  search: 'm21 21-5.2-5.2 M19 10.5a8.5 8.5 0 1 1-17 0 8.5 8.5 0 0 1 17 0',
  heart: 'M20.8 4.6a5.5 5.5 0 0 0-7.8 0L12 5.7l-1.1-1.1a5.5 5.5 0 0 0-7.8 7.8L12 21l8.8-8.6a5.5 5.5 0 0 0 0-7.8',
  cart: 'M2 3h3l3 13h11l3-9H6 M9 21h.01 M18 21h.01',
  user: 'M20 21v-2a7 7 0 0 0-14 0v2 M16 7a4 4 0 1 1-8 0 4 4 0 0 1 8 0',
  star: 'm12 2 3 6.2 7 .9-5 4.9 1.2 7-6.2-3.3-6.2 3.3 1.2-7-5-4.9 7-.9Z',
  check: 'm5 12 4 4L19 6',
  arrow: 'M5 12h14m-5-5 5 5-5 5',
  back: 'M19 12H5m5-5-5 5 5 5',
  close: 'm6 6 12 12M6 18 18 6',
  edit: 'm16 3 5 5-12 12-6 1 1-6Z',
  shield: 'm12 2 9 4v6c0 5-9 10-9 10S3 17 3 12V6Z m-4 10 3 3 5-6',
  sparkle: 'm12 2 2.5 7.5L22 12l-7.5 2.5L12 22l-2.5-7.5L2 12l7.5-2.5Z',
  bag: 'M5 7h14l1 14H4Z M9 7V5a3 3 0 0 1 6 0v2',
  camera: 'M3 7h4l2-3h6l2 3h4v14H3Z M16 13a4 4 0 1 1-8 0 4 4 0 0 1 8 0',
  info: 'M12 10v7 M12 6h.01 M22 12a10 10 0 1 1-20 0 10 10 0 0 1 20 0',
  menu: 'M3 6h18M3 12h18M3 18h18',
  upload: 'M12 16V4m-5 5 5-5 5 5 M4 16v3a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2v-3',
  image: 'M4 4h16v16H4Z m0 12 5-5 4 4 2-2 5 5 M15.5 8.5h.01',
  shirt: 'M8 3 3 6l2 5 3-1v11h8V10l3 1 2-5-5-3a4 4 0 0 1-8 0',
  ruler: 'M3 17 17 3l4 4L7 21Z m4-4 2 2 m1-5 2 2 m1-5 2 2',
  play: 'M7 4v16l13-8Z',
  download: 'M12 4v12m-5-5 5 5 5-5 M4 20h16',
  trash: 'M4 7h16 M10 11v6 M14 11v6 M6 7l1 13h10l1-13 M9 7V4h6v3',
  refresh: 'M20 11a8 8 0 0 0-14.9-3.9L3 9 M3 4v5h5 M4 13a8 8 0 0 0 14.9 3.9L21 15 M21 20v-5h-5',
  lock: 'M6 11h12v10H6Z M8 11V7a4 4 0 0 1 8 0v4',
  layers: 'm12 3 9 5-9 5-9-5Z m-9 9 9 5 9-5 M3 16l9 5 9-5',
  alert: 'M12 3 2 21h20Z M12 10v5 M12 18h.01',
  eye: 'M2 12s4-7 10-7 10 7 10 7-4 7-10 7S2 12 2 12 M15 12a3 3 0 1 1-6 0 3 3 0 0 1 6 0',
  plus: 'M12 5v14M5 12h14',
  compare: 'M12 3v18 M4 6h5v12H4Z M15 6h5v12h-5Z',
  wand: 'm4 20 10-10 m2-6 1 2 2 1-2 1-1 2-1-2-2-1 2-1Z M18 12l.7 1.3L20 14l-1.3.7L18 16l-.7-1.3L16 14l1.3-.7Z',
};

export default function Icon({ name, size = 20, ...props }) {
  return (
    <svg width={size} height={size} viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.7"
      strokeLinecap="round" strokeLinejoin="round" aria-hidden="true" focusable="false" {...props}>
      <path d={paths[name] || paths.sparkle} />
    </svg>
  );
}
