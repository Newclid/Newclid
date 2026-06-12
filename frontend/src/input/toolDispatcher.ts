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
import { applyGridSnap } from '../tools/sharedHelpers';
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
    const wp = applyGridSnap(viewport.screenToWorld(sp), viewport.scale);
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
    // Allow canvas interaction when a tool group is open OR when a non-select
    // tool is active (e.g. activated via keyboard shortcut without opening a group).
    if (!appStore?.activeToolGroup && scene.tool === 'select') return;
    const tool = getTool(scene.tool);
    if (!tool) return;
    // Capture state before the click so we can record one undo step and update
    // the hint label, even for clicks that advance a slot without mutating the
    // scene (e.g. snapping to an existing point via pick-existing).
    const before = scene.snapshot();
    const rev = scene.revision;
    const toolBefore = tool.captureState?.();
    tool.onClick(buildCtx(e));
    const toolAfter = tool.captureState?.();
    const slotChanged = toolAfter?.currentSlotIndex !== toolBefore?.currentSlotIndex;
    // Construction tools (captureState defined): accept only when slot advanced so
    // validation rejections don't clear the error or push a spurious undo entry.
    // Other tools: accept when the scene actually changed.
    const clickAccepted = slotChanged || (!toolBefore && scene.revision !== rev);
    if (clickAccepted) {
      scene.pushUndo(before, toolBefore ? () => tool.restoreState?.(toolBefore) : undefined);
      scene.setSlotError(null);
    }
    if (toolBefore && toolAfter) {
      const justCompleted = toolBefore.currentSlotIndex > 0
        && toolAfter.currentSlotIndex === 0
        && Object.keys(toolAfter.bindings).length === 0;
      scene.setSlotHint(justCompleted ? null : (tool.currentSlotLabel?.() ?? null));
    }
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
    if (!appStore?.activeToolGroup) {
      if (scene.previews.length > 0) { scene.setPreviews([]); requestRedraw(); }
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
