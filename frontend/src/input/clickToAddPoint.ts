import { Viewport } from '../geometry/viewport';
import { screen } from '../geometry/coords';
import { Scene } from '../scene/scene';

// Bare left-click on the canvas places a new point.
//
// Coexists with panZoom: while space is held the user is panning, so we
// suppress the click. We track space state independently rather than
// reaching into panZoom — keeps modules decoupled at the cost of a
// duplicated key listener.

export interface ClickToAddPointHandle {
  destroy(): void;
}

export function attachClickToAddPoint(
  target: SVGSVGElement,
  viewport: Viewport,
  scene: Scene,
  onChange: () => void,
): ClickToAddPointHandle {
  let spaceHeld = false;

  const onKeyDown = (e: KeyboardEvent) => {
    if (e.code !== 'Space' || e.repeat) return;
    const t = e.target as HTMLElement | null;
    if (t?.tagName === 'INPUT' || t?.tagName === 'TEXTAREA') return;
    spaceHeld = true;
  };

  const onKeyUp = (e: KeyboardEvent) => {
    if (e.code === 'Space') spaceHeld = false;
  };

  const toLocal = (e: { clientX: number; clientY: number }) => {
    const r = target.getBoundingClientRect();
    return { x: e.clientX - r.left, y: e.clientY - r.top };
  };

  const onClick = (e: MouseEvent) => {
    if (e.button !== 0 || spaceHeld) return;
    const local = toLocal(e);
    const w = viewport.screenToWorld(screen(local.x, local.y));
    scene.addPoint(w.x, w.y);
    onChange();
  };

  window.addEventListener('keydown', onKeyDown);
  window.addEventListener('keyup', onKeyUp);
  target.addEventListener('click', onClick);

  return {
    destroy() {
      window.removeEventListener('keydown', onKeyDown);
      window.removeEventListener('keyup', onKeyUp);
      target.removeEventListener('click', onClick);
    },
  };
}
