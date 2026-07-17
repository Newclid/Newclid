import { Viewport } from '../geometry/viewport';
import { screen } from '../geometry/coords';

/**
Bindings: right-click drag or middle-click drag = pan,
ctrlKey+wheel (or pinch) = zoom centered on cursor,
plain wheel (trackpad two-finger scroll) = pan.
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

  let panning: { lastX: number; lastY: number; pointerId: number } | null = null;

  // clientX/Y → SVG-local coords.
  const toLocal = (e: { clientX: number; clientY: number }) => {
    const r = target.getBoundingClientRect();
    return { x: e.clientX - r.left, y: e.clientY - r.top };
  };

  // -------- pointer: pan on right-click (button 2) or middle-click (button 1) --------

  const onPointerDown = (e: PointerEvent) => {
    if (e.button !== 1 && e.button !== 2) return;
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
    target.style.cursor = '';
  };

  // -------- wheel: zoom (ctrlKey/pinch) or pan (two-finger scroll) --------

  /**
  passive: false so preventDefault works, without it the page scrolls
  under us while the user is trying to zoom or pan.
  **/
  const onWheel = (e: WheelEvent) => {
    e.preventDefault();
    if (e.ctrlKey) {
      // Pinch-to-zoom on trackpad, or Ctrl+scroll on mouse.
      // exp() so equal-and-opposite deltas exactly cancel.
      const local = toLocal(e);
      const factor = Math.exp(-e.deltaY * WHEEL_ZOOM_SENSITIVITY);
      viewport.zoomAt(screen(local.x, local.y), factor);
    } else {
      // Trackpad two-finger scroll → pan.
      // Negate so scrolling right moves the canvas left (natural scroll).
      viewport.pan(-e.deltaX, -e.deltaY);
    }
    requestRedraw();
  };

  // -------- suppress browser context menu on the canvas --------

  const onContextMenu = (e: MouseEvent) => {
    e.preventDefault();
  };

  // -------- attach --------

  target.addEventListener('pointerdown', onPointerDown);
  target.addEventListener('pointermove', onPointerMove);
  target.addEventListener('pointerup', endPan);
  target.addEventListener('pointercancel', endPan);
  target.addEventListener('wheel', onWheel, { passive: false });
  target.addEventListener('contextmenu', onContextMenu);

  return {
    destroy() {
      target.removeEventListener('pointerdown', onPointerDown);
      target.removeEventListener('pointermove', onPointerMove);
      target.removeEventListener('pointerup', endPan);
      target.removeEventListener('pointercancel', endPan);
      target.removeEventListener('wheel', onWheel);
      target.removeEventListener('contextmenu', onContextMenu);
    },
  };
}
