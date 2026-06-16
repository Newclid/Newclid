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

/**
 * Grid-snap radius as a fraction of the on-screen cell size, not a fixed pixel
 * value. niceStep's 1/2/5/10 rounding means cell size on screen actually varies
 * (roughly 29–71px) as you zoom, so a fixed radius either barely works on big
 * cells or swallows most of a small one. Clamped so it never gets imperceptibly
 * small or large enough to dominate a small cell.
 */
function gridSnapTolPx(cellPx: number): number {
  return Math.min(10, Math.max(3, cellPx * 0.15));
}

// Single source of truth for "what grid intersection is pt closest to, and how
// close does it need to be" — applyGridSnap and the preview must agree exactly.
function gridSnapTarget(pt: WorldPoint, scale: number): { snapX: number; snapY: number; tol: number } {
  const spacing = niceStep(50 / scale);
  const cellPx = spacing * scale;
  return {
    snapX: Math.round(pt.x / spacing) * spacing,
    snapY: Math.round(pt.y / spacing) * spacing,
    tol: gridSnapTolPx(cellPx) / scale,
  };
}

/**
 * Snaps to the nearest grid intersection when the cursor is within tolerance on
 * both axes. Both axes must be close — snap only triggers at the corners of grid
 * squares, not anywhere along a line.
 */
export function applyGridSnap(pt: WorldPoint, scale: number): WorldPoint {
  const { snapX, snapY, tol } = gridSnapTarget(pt, scale);
  if (Math.abs(pt.x - snapX) <= tol && Math.abs(pt.y - snapY) <= tol) {
    return { ...pt, x: snapX, y: snapY };
  }
  return pt;
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
 * Ring at the nearest grid intersection, with no existing-point check. Used by
 * place-free slots, which never snap to existing points but do snap to grid.
 * ctx.world is already grid-snapped by buildCtx, so the delta to the nearest
 * intersection is ~0 when snapping is active and > tol otherwise — that's
 * what lets this tell "snapped" from "not snapped" without a separate flag.
 */
export function gridSnapHighlight(ctx: ToolContext): ToolPreview[] {
  const { snapX, snapY, tol } = gridSnapTarget(ctx.world, ctx.scale);
  if (Math.abs(ctx.world.x - snapX) <= tol && Math.abs(ctx.world.y - snapY) <= tol) {
    return [{ kind: 'highlightPoint', pos: { x: snapX, y: snapY } }];
  }
  return [];
}

/**
 * Returns a highlight ring for onMove previews.
 * Existing point snap takes priority; falls back to the grid intersection ring.
 */
export function snapHighlight(ctx: ToolContext): ToolPreview[] {
  const hit = pickNearestPoint(ctx.scene.objects, ctx.world, {
    tolerancePx: SNAP_PX,
    scale: ctx.scale,
  });
  if (hit) return [{ kind: 'highlightPoint', pos: { x: hit.x, y: hit.y } }];
  return gridSnapHighlight(ctx);
}
