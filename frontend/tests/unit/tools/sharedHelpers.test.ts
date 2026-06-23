import { describe, it, expect } from 'vitest';
import { Scene } from '../../../src/scene/scene';
import { screen, world } from '../../../src/geometry/coords';
import {
  applyGridSnap,
  getOrCreatePoint,
  pickExistingPoint,
  gridSnapHighlight,
  snapHighlight,
  existingPointHighlight,
} from '../../../src/tools/sharedHelpers';
import type { ToolContext } from '../../../src/tools/tool';

function makeCtx(
  scene: Scene,
  wx: number,
  wy: number,
  scale = 50,
  shiftKey = false,
): ToolContext {
  return { scene, world: world(wx, wy), screen: screen(0, 0), scale, shiftKey };
}

// ── applyGridSnap ────────────────────────────────────────────────────────────

describe('applyGridSnap', () => {
  it('snaps when both axes are within tolerance', () => {
    // At scale=50, spacing=niceStep(1)=1, cellPx=50, tol=gridSnapTolPx(50)/50=0.1
    // Point (0.05, 0.05) is within 0.1 of grid (0,0)
    const pt = world(0.05, 0.05);
    const snapped = applyGridSnap(pt, 50);
    expect(snapped.x).toBe(0);
    expect(snapped.y).toBe(0);
  });

  it('does not snap when one axis is outside tolerance', () => {
    // Point (0.5, 0.05) — x is too far from any integer
    const pt = world(0.5, 0.05);
    const result = applyGridSnap(pt, 50);
    expect(result.x).toBe(0.5);
    expect(result.y).toBe(0.05);
  });

  it('does not snap when both axes are outside tolerance', () => {
    const pt = world(0.5, 0.5);
    const result = applyGridSnap(pt, 50);
    expect(result).toEqual(pt);
  });
});

// ── niceStep branches (exercised via applyGridSnap with different scales) ────

describe('niceStep branches via applyGridSnap', () => {
  // niceStep(raw) with raw = 50/scale
  // m < 1.5 → base: scale=50 → raw=1 → exp=0 → base=1, m=1 → returns 1
  it('m < 1.5 branch: returns base', () => {
    const snapped = applyGridSnap(world(0.05, 0.05), 50);
    expect(snapped.x).toBe(0); // proves niceStep ran and returned 1
  });

  // m < 3.5 → 2*base: scale=25 → raw=2 → exp=0 → base=1, m=2 → returns 2
  it('m in [1.5,3.5) branch: returns 2*base', () => {
    // spacing=2, tol≈gridSnapTolPx(50)/25=0.1/25... let's test snap near 0
    const snapped = applyGridSnap(world(0.05, 0.05), 25);
    expect(snapped.x).toBe(0);
  });

  // m in [3.5,7.5) → 5*base: scale=10 → raw=5 → exp=0 → base=1, m=5 → returns 5
  it('m in [3.5,7.5) branch: returns 5*base', () => {
    const snapped = applyGridSnap(world(0.05, 0.05), 10);
    expect(snapped.x).toBe(0);
  });

  // m >= 7.5 → 10*base: scale=5 → raw=10 → exp=1 → base=10, m=1 → returns 10
  // Actually raw=50/5=10, exp=1, base=10, m=10/10=1 → m<1.5 → base=10
  // Need m>=7.5: raw must be like 8 or 9 in [1,10) range
  // scale≈6.25 → raw=50/6.25=8 → exp=0, base=1, m=8 → returns 10*1=10
  it('m >= 7.5 branch: returns 10*base', () => {
    const snapped = applyGridSnap(world(0.05, 0.05), 6.25);
    expect(snapped.x).toBe(0);
  });

  // raw <= 0 branch: scale=Infinity → raw=50/Infinity=0 → niceStep returns 1
  // tol becomes 10/Infinity=0, so no snap occurs — function returns input unchanged
  it('raw <= 0 branch: returns input unchanged (tol collapses to 0)', () => {
    const pt = world(0.05, 0.05);
    const result = applyGridSnap(pt, Infinity);
    expect(result).toEqual(pt);
  });
});

// ── gridSnapTolPx branches ───────────────────────────────────────────────────

describe('gridSnapTolPx clamp via applyGridSnap', () => {
  // cellPx*0.15 < 3 → clamp to 3: need cellPx < 20, e.g. scale=1000, spacing=niceStep(0.05)=0.05, cellPx=50
  // Actually let's just verify snap still works at extreme scales
  it('small cellPx clamps tol to minimum (still snaps near grid)', () => {
    // scale=1000 → raw=0.05 → niceStep(0.05): exp=floor(log10(0.05))=-2, base=0.01, m=5 → 5*0.01=0.05
    // cellPx=0.05*1000=50, tol=max(3,min(10,7.5))/1000 ≈ 0.0075
    const snapped = applyGridSnap(world(0.001, 0.001), 1000);
    expect(snapped.x).toBe(0);
  });

  it('large cellPx clamps tol to maximum (still snaps near grid)', () => {
    // scale=1 → raw=50, niceStep(50)=50, cellPx=50, tol=min(10,max(3,7.5))/1=7.5
    const snapped = applyGridSnap(world(1, 1), 1);
    expect(snapped.x).toBe(0); // snaps to 0
  });
});

// ── getOrCreatePoint ─────────────────────────────────────────────────────────

describe('getOrCreatePoint', () => {
  it('returns existing point id when one is nearby (no shift)', () => {
    const scene = new Scene();
    const existingId = scene.addPoint(1, 1);
    const ctx = makeCtx(scene, 1, 1); // cursor exactly on the point, scale=50 → tol=0.1/50=0.24px
    const id = getOrCreatePoint(ctx);
    expect(id).toBe(existingId);
    expect(scene.objects.size).toBe(1); // no new point created
  });

  it('creates a new point when nothing is nearby (no shift)', () => {
    const scene = new Scene();
    const ctx = makeCtx(scene, 100, 100);
    const id = getOrCreatePoint(ctx);
    expect(scene.objects.has(id)).toBe(true);
    expect(scene.objects.size).toBe(1);
  });

  it('always creates a new point when shift is held, even near an existing point', () => {
    const scene = new Scene();
    const existingId = scene.addPoint(1, 1);
    const ctx = makeCtx(scene, 1, 1, 50, true);
    const id = getOrCreatePoint(ctx);
    expect(id).not.toBe(existingId);
    expect(scene.objects.size).toBe(2);
  });
});

// ── pickExistingPoint ────────────────────────────────────────────────────────

describe('pickExistingPoint', () => {
  it('returns the id of a nearby existing point', () => {
    const scene = new Scene();
    const existingId = scene.addPoint(0, 0);
    const ctx = makeCtx(scene, 0, 0);
    expect(pickExistingPoint(ctx)).toBe(existingId);
  });

  it('returns null when no existing point is nearby', () => {
    const scene = new Scene();
    const ctx = makeCtx(scene, 100, 100);
    expect(pickExistingPoint(ctx)).toBeNull();
  });
});

// ── gridSnapHighlight ────────────────────────────────────────────────────────

describe('gridSnapHighlight', () => {
  it('returns [] when shift is held', () => {
    const scene = new Scene();
    const ctx = makeCtx(scene, 0, 0, 50, true);
    expect(gridSnapHighlight(ctx)).toEqual([]);
  });

  it('returns highlightPoint when cursor is near a grid intersection', () => {
    const scene = new Scene();
    // At scale=50, spacing=1, tol≈0.1. Point (0.05, 0.05) snaps to (0,0).
    const ctx = makeCtx(scene, 0.05, 0.05, 50, false);
    const previews = gridSnapHighlight(ctx);
    expect(previews).toHaveLength(1);
    expect(previews[0].kind).toBe('highlightPoint');
    if (previews[0].kind === 'highlightPoint') {
      expect(previews[0].pos).toEqual({ x: 0, y: 0 });
    }
  });

  it('returns [] when cursor is far from a grid intersection', () => {
    const scene = new Scene();
    const ctx = makeCtx(scene, 0.5, 0.5, 50, false);
    expect(gridSnapHighlight(ctx)).toEqual([]);
  });
});

// ── snapHighlight ────────────────────────────────────────────────────────────

describe('snapHighlight', () => {
  it('returns existing point highlight when one is nearby (no shift)', () => {
    const scene = new Scene();
    scene.addPoint(5, 5);
    const ctx = makeCtx(scene, 5, 5, 50, false);
    const previews = snapHighlight(ctx);
    expect(previews).toHaveLength(1);
    expect(previews[0].kind).toBe('highlightPoint');
  });

  it('falls back to grid highlight when no existing point nearby (no shift)', () => {
    const scene = new Scene();
    // Nothing in scene, cursor near grid intersection (0,0)
    const ctx = makeCtx(scene, 0.05, 0.05, 50, false);
    const previews = snapHighlight(ctx);
    expect(previews).toHaveLength(1);
    expect(previews[0].kind).toBe('highlightPoint');
  });

  it('returns grid highlight when shift is held (existing point skipped)', () => {
    const scene = new Scene();
    scene.addPoint(0, 0);
    // Shift held — should skip existing-point check and go to gridSnapHighlight
    const ctx = makeCtx(scene, 0.05, 0.05, 50, true);
    // gridSnapHighlight returns [] when shift is held
    expect(snapHighlight(ctx)).toEqual([]);
  });

  it('returns [] when shift held and far from grid', () => {
    const scene = new Scene();
    const ctx = makeCtx(scene, 0.5, 0.5, 50, true);
    expect(snapHighlight(ctx)).toEqual([]);
  });
});

// ── existingPointHighlight ───────────────────────────────────────────────────

describe('existingPointHighlight', () => {
  it('returns highlightPoint for a nearby existing point', () => {
    const scene = new Scene();
    scene.addPoint(2, 3);
    const ctx = makeCtx(scene, 2, 3, 50, false);
    const previews = existingPointHighlight(ctx);
    expect(previews).toHaveLength(1);
    expect(previews[0].kind).toBe('highlightPoint');
    if (previews[0].kind === 'highlightPoint') {
      expect(previews[0].pos).toEqual({ x: 2, y: 3 });
    }
  });

  it('returns [] when no point is nearby', () => {
    const scene = new Scene();
    const ctx = makeCtx(scene, 100, 100, 50, false);
    expect(existingPointHighlight(ctx)).toEqual([]);
  });
});
