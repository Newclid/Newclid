import { Viewport } from '../geometry/viewport';
import { screen } from '../geometry/coords';

/**
Bindings: Space + left-drag, wheel = zoom centered on cursor.
Bare left-click stays unbound so construction tools can claim it.
**/

// Roughly a 5% scale step per wheel detent on common trackpads/mice.
const WHEEL_ZOOM_SENSITIVITY = 0.0015;

export interface PanZoomHandle {
  // Detach all listeners.
  destroy(): void;
}

export function attachPanZoom(
  target: SVGSVGElement,
  viewport: Viewport,
  onChange: () => void,
): PanZoomHandle {
  // redraw at most once per animation frame.
  let frameQueued = false;
  const requestRedraw = () => {
    if (frameQueued) return;
    frameQueued = true;
    requestAnimationFrame(() => {
      frameQueued = false;
      onChange();
    });
  };

  // -------- pan state --------

  let spaceHeld = false;
  let panning: { lastX: number; lastY: number; pointerId: number } | null = null;

  // clientX/Y → SVG-local coords.
  const toLocal = (e: { clientX: number; clientY: number }) => {
    const r = target.getBoundingClientRect();
    return { x: e.clientX - r.left, y: e.clientY - r.top };
  };

  // -------- spacebar latch --------

  const onKeyDown = (e: KeyboardEvent) => {
    if (e.code !== 'Space' || e.repeat) return;
   
    const t = e.target as HTMLElement | null;
    if (t?.tagName === 'INPUT' || t?.tagName === 'TEXTAREA') return;
    spaceHeld = true;
    target.style.cursor = 'grab';
    // Without preventDefault, space scrolls the page when body has focus.
    e.preventDefault();
  };

  const onKeyUp = (e: KeyboardEvent) => {
    if (e.code !== 'Space') return;
    spaceHeld = false;
    // Don't reset cursor mid-drag; pointerup will handle it.
    if (!panning) target.style.cursor = '';
  };

  // -------- pointer: pan while space is held --------

  const onPointerDown = (e: PointerEvent) => {
    if (e.button !== 0 || !spaceHeld) return;
    const local = toLocal(e);
    panning = { lastX: local.x, lastY: local.y, pointerId: e.pointerId };
    /**
    Capture so move/up keep firing when the cursor leaves the SVG bounds —
    otherwise a fast drag past the window edge drops mid-pan.
    **/
    target.setPointerCapture(e.pointerId);
    target.style.cursor = 'grabbing';
    e.preventDefault();
  };

  const onPointerMove = (e: PointerEvent) => {
    if (!panning || e.pointerId !== panning.pointerId) return;
    const local = toLocal(e);
    const dx = local.x - panning.lastX;
    const dy = local.y - panning.lastY;
    panning.lastX = local.x;
    panning.lastY = local.y;
    viewport.pan(dx, dy);
    requestRedraw();
  };

  const endPan = (e: PointerEvent) => {
    if (!panning || e.pointerId !== panning.pointerId) return;
    target.releasePointerCapture(panning.pointerId);
    panning = null;
    target.style.cursor = spaceHeld ? 'grab' : '';
  };

  // -------- wheel: zoom centered on cursor --------

  /**
  passive: false so preventDefault works, without it the page scrolls
  under us while the user is trying to zoom.
  **/
  const onWheel = (e: WheelEvent) => {
    e.preventDefault();
    const local = toLocal(e);
    // exp() so equal-and-opposite deltas exactly cancel.
    const factor = Math.exp(-e.deltaY * WHEEL_ZOOM_SENSITIVITY);
    viewport.zoomAt(screen(local.x, local.y), factor);
    requestRedraw();
  };

  // -------- attach --------

  window.addEventListener('keydown', onKeyDown);
  window.addEventListener('keyup', onKeyUp);
  target.addEventListener('pointerdown', onPointerDown);
  target.addEventListener('pointermove', onPointerMove);
  target.addEventListener('pointerup', endPan);
  target.addEventListener('pointercancel', endPan);
  target.addEventListener('wheel', onWheel, { passive: false });

  return {
    destroy() {
      window.removeEventListener('keydown', onKeyDown);
      window.removeEventListener('keyup', onKeyUp);
      target.removeEventListener('pointerdown', onPointerDown);
      target.removeEventListener('pointermove', onPointerMove);
      target.removeEventListener('pointerup', endPan);
      target.removeEventListener('pointercancel', endPan);
      target.removeEventListener('wheel', onWheel);
    },
  };
}
