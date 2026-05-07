// Routes pointer events on the canvas to the active tool: a click
// resolves `scene.tool` against the registry and calls that tool's
// `onClick`.
//
// Coexists with panZoom: while space is held the user is panning, so we
// suppress the click. Space state is tracked here rather than read from
// panZoom — the duplicated key listener keeps the two modules
// decoupled.

import { Viewport } from '../geometry/viewport';
import { screen } from '../geometry/coords';
import { Scene } from '../scene/scene';
import { toolRegistry } from '../tools/registry';

export interface ToolDispatcherHandle {
  destroy(): void;
}

export function attachToolDispatcher(
  target: SVGSVGElement,
  viewport: Viewport,
  scene: Scene,
): ToolDispatcherHandle {
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
    const sp = screen(local.x, local.y);
    const wp = viewport.screenToWorld(sp);
    const tool = toolRegistry[scene.tool];
    tool.onClick({
      scene,
      world: wp,
      screen: sp,
      scale: viewport.scale,
      shiftKey: e.shiftKey,
    });
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
