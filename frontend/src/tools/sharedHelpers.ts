import { ToolContext, ToolPreview } from './tool';
import { pickNearestPoint } from '../geometry/hitTest';
import type { ObjectId } from '../geometry/types-object';
import type { WorldPoint } from '../geometry/coords';

const SNAP_PX = 12;

// Keep this in sync with renderer.ts — both use niceStep(50 / scale) so snap targets land on visible grid lines.
function niceStep(raw: number): number {
  if (raw <= 0) return 1;
  const exp = Math.floor(Math.log10(raw));
  const base = Math.pow(10, exp);
  const m = raw / base;
  if (m < 1.5) return base;
  if (m < 3.5) return 2 * base;
  if (m < 7.5) return 5 * base;
  return 10 * base;
}

// Snaps x and y independently to the nearest grid multiple when the cursor is within SNAP_PX of one.
export function applyGridSnap(pt: WorldPoint, scale: number): WorldPoint {
  const spacing = niceStep(50 / scale);
  const tol = SNAP_PX / scale;
  const snapX = Math.round(pt.x / spacing) * spacing;
  const snapY = Math.round(pt.y / spacing) * spacing;
  return {
    ...pt,
    x: Math.abs(pt.x - snapX) <= tol ? snapX : pt.x,
    y: Math.abs(pt.y - snapY) <= tol ? snapY : pt.y,
  };
}

// Snaps to an existing point if one is within range, otherwise drops a new one at the cursor.
export function getOrCreatePoint(ctx: ToolContext): ObjectId {
  const hit = pickNearestPoint(ctx.scene.objects, ctx.world, {
    tolerancePx: SNAP_PX,
    scale: ctx.scale,
  });
  if (hit) return hit.id;
  return ctx.scene.addPoint(ctx.world.x, ctx.world.y);
}

/**
 * Like getOrCreatePoint but read-only — only returns an existing point's id.
 * Returns null when the cursor isn't near anything, so pick-existing slots
 * can reject the click without creating a stray point.
 */
export function pickExistingPoint(ctx: ToolContext): ObjectId | null {
  const hit = pickNearestPoint(ctx.scene.objects, ctx.world, {
    tolerancePx: SNAP_PX,
    scale: ctx.scale,
  });
  return hit?.id ?? null;
}

/**
 * Returns a highlight ring for onMove previews.
 * Existing point snap takes priority; if nothing is nearby, falls back to a
 * ring at the nearest grid intersection when the cursor is within SNAP_PX of one.
 * Works because buildCtx pre-snaps ctx.world, so the delta to the nearest grid
 * multiple is ~0 when snapping is active and > tol when the cursor is far from any line.
 */
export function snapHighlight(ctx: ToolContext): ToolPreview[] {
  const hit = pickNearestPoint(ctx.scene.objects, ctx.world, {
    tolerancePx: SNAP_PX,
    scale: ctx.scale,
  });
  if (hit) return [{ kind: 'highlightPoint', pos: { x: hit.x, y: hit.y } }];

  const spacing = niceStep(50 / ctx.scale);
  const tol = SNAP_PX / ctx.scale;
  const snapX = Math.round(ctx.world.x / spacing) * spacing;
  const snapY = Math.round(ctx.world.y / spacing) * spacing;
  const nearX = Math.abs(ctx.world.x - snapX) <= tol;
  const nearY = Math.abs(ctx.world.y - snapY) <= tol;
  if (nearX || nearY) {
    return [{ kind: 'highlightPoint', pos: {
      x: nearX ? snapX : ctx.world.x,
      y: nearY ? snapY : ctx.world.y,
    }}];
  }
  return [];
}
