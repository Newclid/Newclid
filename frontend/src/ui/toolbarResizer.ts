const MIN_WIDTH = 180; // keep icon + label + shortcut readable
const MAX_WIDTH = 420; // don't let the toolbar eat the canvas

interface ResizerOptions {
  app: HTMLElement;
  toolbar: HTMLElement;
}

export function attachToolbarResizer(opts: ResizerOptions): () => void {
  const { app, toolbar } = opts;

  const handle = document.createElement('div');
  handle.className = 'toolbar-resizer';
  handle.setAttribute('role', 'separator');
  handle.setAttribute('aria-orientation', 'vertical');
  toolbar.appendChild(handle);

  let startX = 0;
  let startWidth = 0;

  const onMove = (e: PointerEvent) => {
    const next = Math.min(MAX_WIDTH, Math.max(MIN_WIDTH, startWidth + (e.clientX - startX)));
    app.style.setProperty('--toolbar-width', `${next}px`);
  };

  const onUp = (e: PointerEvent) => {
    handle.releasePointerCapture(e.pointerId);
    handle.classList.remove('is-active');
    document.body.classList.remove('is-resizing');
    handle.removeEventListener('pointermove', onMove);
    handle.removeEventListener('pointerup', onUp);
  };

  const onDown = (e: PointerEvent) => {
    startX = e.clientX;
    startWidth = toolbar.getBoundingClientRect().width;
    // Capture so the drag keeps tracking even when the pointer leaves the 6px strip.
    handle.setPointerCapture(e.pointerId);
    handle.classList.add('is-active');
    document.body.classList.add('is-resizing');
    handle.addEventListener('pointermove', onMove);
    handle.addEventListener('pointerup', onUp);
    e.preventDefault();
  };

  handle.addEventListener('pointerdown', onDown);

  return () => {
    handle.removeEventListener('pointerdown', onDown);
    handle.remove();
  };
}
