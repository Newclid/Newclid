/**
Routes canvas pointer events to the active tool via getTool.
Pan gestures (right/middle drag, wheel) are handled exclusively by
panZoom.ts and do not reach this dispatcher.
**/

import { Viewport } from '../geometry/viewport';
import { screen } from '../geometry/coords';
import { Scene } from '../scene/scene';
import { getTool } from '../tools/registry';
import { pickNearestPoint } from '../geometry/hitTest';
import type { AppStore } from '../store/appStore';

export interface ToolDispatcherHandle {
  destroy(): void;
}

export function attachToolDispatcher(
  target: SVGSVGElement,
  viewport: Viewport,
  scene: Scene,
  requestRedraw: () => void,
  appStore?: AppStore,
): ToolDispatcherHandle {
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
    if (e.button !== 0 || appStore?.proofMode) return;
    if (appStore?.proofByPointsMode) {
      const ctx = buildCtx(e);
      appStore.goalPickCallback?.(ctx.world.x, ctx.world.y, ctx.scale);
      return;
    }
    const tool = getTool(scene.tool);
    if (!tool) return;
    tool.onClick(buildCtx(e));
  };

  const onPointerMove = (e: PointerEvent) => {
    if (appStore?.proofMode) return;
    if (appStore?.proofByPointsMode) {
      const ctx = buildCtx(e);
      const nearest = pickNearestPoint(scene.objects, ctx.world, { tolerancePx: 12, scale: ctx.scale });
      scene.setPreviews(nearest ? [{ kind: 'highlightPoint', pos: { x: nearest.x, y: nearest.y } }] : []);
      requestRedraw();
      return;
    }
    const tool = getTool(scene.tool);
    if (!tool) return;
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

  target.addEventListener('click', onClick);
  target.addEventListener('pointermove', onPointerMove);
  target.addEventListener('pointerleave', onPointerLeave);

  return {
    destroy() {
      target.removeEventListener('click', onClick);
      target.removeEventListener('pointermove', onPointerMove);
      target.removeEventListener('pointerleave', onPointerLeave);
    },
  };
}
