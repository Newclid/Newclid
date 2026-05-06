import { Viewport } from '../geometry/viewport';
import { screen } from '../geometry/coords';

// Pan/zoom input handling. Mutates the Viewport in response to pointer
// and wheel input, then asks the host to redraw.
//
// Bindings:
//   Hold Space, then left-drag → pan
//   Wheel scroll                → zoom centered on cursor
//
// Bare left-click is left unbound on purpose so construction tools can
// claim it later — same reason we don't pan on plain left-drag.

// Wheel sensitivity. Browser deltaY varies by deltaMode (pixel/line/page)
// and device, but for trackpads and standard mice this gives roughly a
// 5% scale step per detent, which feels neither sluggish nor jumpy.
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
  // rAF coalescing: pointermove and wheel can fire many times per frame.
  // The viewport mutates synchronously so any reader sees the latest
  // state, but we redraw at most once per animation frame.
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

  // clientX/Y -> coords local to the SVG (its top-left = 0,0). We re-read
  // the bounding rect on every event because the SVG can move (page
  // scroll, layout shift) without notifying us.
  const toLocal = (e: { clientX: number; clientY: number }) => {
    const r = target.getBoundingClientRect();
    return { x: e.clientX - r.left, y: e.clientY - r.top };
  };

  // -------- spacebar latch --------

  const onKeyDown = (e: KeyboardEvent) => {
    if (e.code !== 'Space' || e.repeat) return;
    // Don't hijack space typed into form inputs (search boxes etc).
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
    // setPointerCapture so pointermove/up keep firing on this element
    // even when the cursor leaves the SVG bounds — without it a fast
    // drag past the window edge drops mid-pan.
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

  // passive: false so preventDefault works — without it the page
  // scrolls under us while the user is trying to zoom.
  const onWheel = (e: WheelEvent) => {
    e.preventDefault();
    const local = toLocal(e);
    // exp() so equal-and-opposite deltas exactly cancel — scrolling up
    // then down by the same amount restores the original scale, which
    // a linear factor wouldn't.
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
