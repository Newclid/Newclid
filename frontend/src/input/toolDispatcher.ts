/**
Routes canvas pointer events to the active tool via toolRegistry.
Suppresses click/onMove while space is held so panZoom owns the gesture.
**/

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
  requestRedraw: () => void,
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

  const buildCtx = (e: MouseEvent) => {
    const local = toLocal(e);
    const sp = screen(local.x, local.y);
    const wp = viewport.screenToWorld(sp);
    return {
      scene,
      world: wp,
      screen: sp,
      scale: viewport.scale,
      shiftKey: e.shiftKey,
    };
  };

  const onClick = (e: MouseEvent) => {
    if (e.button !== 0 || spaceHeld) return;
    const tool = toolRegistry[scene.tool];
    tool.onClick(buildCtx(e));
  };

  const onPointerMove = (e: PointerEvent) => {
    if (spaceHeld) return;
    const tool = toolRegistry[scene.tool];
    const previews = tool.onMove(buildCtx(e));
    scene.setPreviews(previews);
    /**
    setPreviews doesn't emit. Nudge the renderer directly so a
    pointermove burst doesn't re-run every subscriber.
    **/
    requestRedraw();
  };

  const onPointerLeave = () => {
    if (scene.previews.length === 0) return;
    scene.setPreviews([]);
    requestRedraw();
  };

  window.addEventListener('keydown', onKeyDown);
  window.addEventListener('keyup', onKeyUp);
  target.addEventListener('click', onClick);
  target.addEventListener('pointermove', onPointerMove);
  target.addEventListener('pointerleave', onPointerLeave);

  return {
    destroy() {
      window.removeEventListener('keydown', onKeyDown);
      window.removeEventListener('keyup', onKeyUp);
      target.removeEventListener('click', onClick);
      target.removeEventListener('pointermove', onPointerMove);
      target.removeEventListener('pointerleave', onPointerLeave);
    },
  };
}
