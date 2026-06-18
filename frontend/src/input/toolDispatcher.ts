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
  // Redo the last onMove preview computation. Pan/zoom don't fire pointermove,
  // so panZoom.ts calls this after moving the viewport to keep the preview
  // (and the grid-snap ring in particular) tracking the cursor's world position.
  refreshPreview(): void;
}

export function attachToolDispatcher(
  target: SVGSVGElement,
  viewport: Viewport,
  scene: Scene,
  requestRedraw: () => void,
  appStore?: AppStore,
  opts?: { selectMenuCallback?: (pointId: string, x: number, y: number) => void },
): ToolDispatcherHandle {
  const toLocal = (e: { clientX: number; clientY: number }) => {
    const r = target.getBoundingClientRect();
    return { x: e.clientX - r.left, y: e.clientY - r.top };
  };

  const buildCtx = (e: { clientX: number; clientY: number; shiftKey: boolean }) => {
    const local = toLocal(e);
    const sp = screen(local.x, local.y);
    const raw = viewport.screenToWorld(sp);
    // Shift is the escape hatch for precise placement — skip grid snap so
    // ctx.world is the exact cursor position.
    const wp = e.shiftKey ? raw : applyGridSnap(raw, viewport.scale);
    return {
      scene,
      world: wp,
      screen: sp,
      scale: viewport.scale,
      shiftKey: e.shiftKey,
    };
  };

  // Last pointer position seen by onPointerMove. Pan/zoom mutate the viewport
  // without firing pointermove, so they call refreshPreview() (below) to redo
  // this computation against the new viewport — otherwise the preview ring
  // drifts away from the cursor as the canvas moves under it.
  let lastMove: { clientX: number; clientY: number; shiftKey: boolean } | null = null;

  const onClick = (e: MouseEvent) => {
    if (e.button !== 0 || appStore?.proofMode) return;
    if (appStore?.proofByPointsMode) {
      const ctx = buildCtx(e);
      appStore.goalPickCallback?.(ctx.world.x, ctx.world.y, ctx.scale);
      return;
    }
    if (scene.tool === 'select' && !appStore?.activeToolGroup) {
      const hovered = scene.previews.find(p => p.kind === 'selectHoverPoint') as
        ({ kind: 'selectHoverPoint'; pos: { x: number; y: number }; pointId: string } | undefined);
      if (hovered) {
        const local = toLocal(e);
        opts?.selectMenuCallback?.(hovered.pointId, local.x, local.y);
      }
      return;
    }
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
      const toolName = scene.tool;
      scene.pushUndo(before, toolBefore ? () => {
        if (scene.tool === toolName) tool.restoreState?.(toolBefore);
      } : undefined);
      scene.setSlotError(null);
    }
    if (toolBefore && toolAfter) {
      const justCompleted = toolBefore.currentSlotIndex > 0
        && toolAfter.currentSlotIndex === 0
        && Object.keys(toolAfter.bindings).length === 0;
      scene.setSlotHint(justCompleted ? null : (tool.currentSlotLabel?.() ?? null));
    }
  };

  // Shared by onPointerMove and refreshPreview — same logic, different trigger.
  const updatePreview = (e: { clientX: number; clientY: number; shiftKey: boolean }) => {
    if (appStore?.proofMode) return;
    if (appStore?.proofByPointsMode) {
      const ctx = buildCtx(e);
      const nearest = pickNearestPoint(scene.objects, ctx.world, { tolerancePx: 12, scale: ctx.scale });
      scene.setPreviews(nearest ? [{ kind: 'highlightPoint', pos: { x: nearest.x, y: nearest.y } }] : []);
      requestRedraw();
      return;
    }
    if (scene.tool === 'select' && !appStore?.activeToolGroup) {
      const ctx = buildCtx(e);
      const nearest = pickNearestPoint(scene.objects, ctx.world, { tolerancePx: 12, scale: ctx.scale });
      if (nearest) {
        scene.setPreviews([{ kind: 'selectHoverPoint', pos: { x: nearest.x, y: nearest.y }, pointId: nearest.id }]);
        target.style.cursor = 'pointer';
      } else {
        scene.setPreviews([]);
        target.style.cursor = '';
      }
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

  const onPointerMove = (e: PointerEvent) => {
    lastMove = { clientX: e.clientX, clientY: e.clientY, shiftKey: e.shiftKey };
    updatePreview(lastMove);
  };

  const onPointerLeave = () => {
    lastMove = null;
    target.style.cursor = '';
    if (scene.previews.length === 0) return;
    scene.setPreviews([]);
    requestRedraw();
  };

  // Shift press/release doesn't fire pointermove, so the preview ring would
  // stay stale until the next mouse move. Re-run updatePreview immediately
  // with the new shiftKey state so it appears/disappears in real time.
  const onKeyDown = (e: KeyboardEvent) => {
    if (e.key === 'Shift' && lastMove) {
      lastMove = { ...lastMove, shiftKey: true };
      updatePreview(lastMove);
    }
  };
  const onKeyUp = (e: KeyboardEvent) => {
    if (e.key === 'Shift' && lastMove) {
      lastMove = { ...lastMove, shiftKey: false };
      updatePreview(lastMove);
    }
  };

  const refreshPreview = () => {
    if (lastMove) updatePreview(lastMove);
  };

  let prevToolName = scene.tool;
  const unsubscribe = scene.subscribe(() => {
    if (scene.tool !== prevToolName) {
      getTool(prevToolName)?.onDeactivate?.({ scene });
      prevToolName = scene.tool;
    }
  });

  target.addEventListener('click', onClick);
  target.addEventListener('pointermove', onPointerMove);
  target.addEventListener('pointerleave', onPointerLeave);
  window.addEventListener('keydown', onKeyDown);
  window.addEventListener('keyup', onKeyUp);

  return {
    destroy() {
      unsubscribe();
      target.removeEventListener('click', onClick);
      target.removeEventListener('pointermove', onPointerMove);
      target.removeEventListener('pointerleave', onPointerLeave);
      window.removeEventListener('keydown', onKeyDown);
      window.removeEventListener('keyup', onKeyUp);
    },
    refreshPreview,
  };
}
