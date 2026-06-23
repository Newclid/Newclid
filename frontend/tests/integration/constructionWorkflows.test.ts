import { describe, it, expect, beforeEach } from 'vitest';
import { Scene } from '../../src/scene/scene';
import { ConstructionTool } from '../../src/tools/construction-tool';
import { CONSTRUCTION_CATALOG } from '../../src/construction/catalog';
import { emitScene } from '../../src/emit/jgex';
import type { ToolContext } from '../../src/tools/tool';
import { world, screen } from '../../src/geometry/coords';

// Mirrors the accept/undo logic from toolDispatcher.ts so undo tracking is real.
function click(
  tool: ConstructionTool,
  scene: Scene,
  worldPt: { x: number; y: number },
  opts?: { shiftKey?: boolean; scale?: number },
): boolean {
  const scale = opts?.scale ?? 1;
  const ctx: ToolContext = {
    scene,
    world: world(worldPt.x, worldPt.y),
    screen: screen(worldPt.x * scale, worldPt.y * scale),
    scale,
    shiftKey: opts?.shiftKey ?? false,
  };

  const before = scene.snapshot();
  const toolBefore = tool.captureState();

  tool.onClick(ctx);

  const toolAfter = tool.captureState();
  const slotChanged = toolAfter.currentSlotIndex !== toolBefore.currentSlotIndex;
  // toolDispatcher uses slotChanged for tools with captureState (which ConstructionTool always has).
  // The revision fallback only applies to tools without captureState (e.g. select).
  const accepted = slotChanged;

  if (accepted) {
    scene.pushUndo(before, () => {
      if (scene.tool === tool.name) tool.restoreState(toolBefore);
    });
    scene.setSlotError(null);
  }

  return accepted;
}

describe('Construction and scene workflows', () => {
  let scene: Scene;

  beforeEach(() => {
    scene = new Scene();
  });

  describe('line construction', () => {
    it('two clicks on empty scene produce two points and one construction', () => {
      const tool = new ConstructionTool(CONSTRUCTION_CATALOG['line']);
      scene.setTool('line');

      click(tool, scene, { x: 0, y: 0 });
      click(tool, scene, { x: 200, y: 0 });

      expect(scene.objects.size).toBe(3);
      const kinds = [...scene.objects.values()].map(o => o.kind);
      expect(kinds.filter(k => k === 'point')).toHaveLength(2);
      expect(kinds.filter(k => k === 'construction')).toHaveLength(1);
    });

    it('line construction has no JGEX clause (no jgex field in catalog entry)', () => {
      const tool = new ConstructionTool(CONSTRUCTION_CATALOG['line']);
      scene.setTool('line');

      click(tool, scene, { x: 0, y: 0 });
      click(tool, scene, { x: 200, y: 0 });

      expect(emitScene(scene)).toBe('a = free a; b = free b');
    });
  });

  describe('circle construction', () => {
    it('two clicks produce a center point, a through point, and a circle object', () => {
      const tool = new ConstructionTool(CONSTRUCTION_CATALOG['circle']);
      scene.setTool('circle');

      click(tool, scene, { x: 0, y: 0 });
      click(tool, scene, { x: 100, y: 0 });

      expect(scene.objects.size).toBe(3);
      const kinds = [...scene.objects.values()].map(o => o.kind);
      expect(kinds.filter(k => k === 'point')).toHaveLength(2);
      expect(kinds.filter(k => k === 'circle')).toHaveLength(1);
    });
  });

  describe('midpoint construction', () => {
    it('snapping to two existing points produces a midpoint and construction without new base points', () => {
      scene.addPoint(0, 0);
      scene.addPoint(200, 0);

      const tool = new ConstructionTool(CONSTRUCTION_CATALOG['midpoint']);
      scene.setTool('midpoint');

      // Click exactly on the existing points — both snap (distance 0 < 12px threshold)
      click(tool, scene, { x: 0, y: 0 });
      click(tool, scene, { x: 200, y: 0 });

      // 2 base + 1 midpoint + 1 construction = 4
      expect(scene.objects.size).toBe(4);
      const points = [...scene.objects.values()].filter(o => o.kind === 'point');
      expect(points).toHaveLength(3);
    });

    it('midpoint x-coordinate equals the average of the two base points', () => {
      scene.addPoint(0, 0);
      scene.addPoint(200, 0);

      const tool = new ConstructionTool(CONSTRUCTION_CATALOG['midpoint']);
      scene.setTool('midpoint');

      click(tool, scene, { x: 0, y: 0 });
      click(tool, scene, { x: 200, y: 0 });

      const pointXs = [...scene.objects.values()]
        .filter(o => o.kind === 'point')
        .map(o => (o as { x: number }).x);
      expect(pointXs).toContain(100);
    });
  });

  describe('rectangle construction', () => {
    it('two clicks produce four corner points and a construction', () => {
      const tool = new ConstructionTool(CONSTRUCTION_CATALOG['rectangle']);
      scene.setTool('rectangle');

      click(tool, scene, { x: 0, y: 0 });
      click(tool, scene, { x: 100, y: 50 });

      // 2 placed + 2 derived corners + 1 construction = 5
      expect(scene.objects.size).toBe(5);
      const kinds = [...scene.objects.values()].map(o => o.kind);
      expect(kinds.filter(k => k === 'point')).toHaveLength(4);
      expect(kinds.filter(k => k === 'construction')).toHaveLength(1);
    });

    it('emits a rectangle clause in JGEX with no free-point clauses', () => {
      const tool = new ConstructionTool(CONSTRUCTION_CATALOG['rectangle']);
      scene.setTool('rectangle');

      click(tool, scene, { x: 0, y: 0 });
      click(tool, scene, { x: 100, y: 50 });

      const jgex = emitScene(scene);
      expect(jgex).toContain('rectangle');
      // All four corners are produced by the construction — none should be "free"
      expect(jgex).not.toContain('free');
    });
  });

  describe('snapping — reuse existing point', () => {
    it('second click within 12px of an existing point snaps to it without creating a new point', () => {
      scene.addPoint(100, 0); // pre-existing point B
      const tool = new ConstructionTool(CONSTRUCTION_CATALOG['line']);
      scene.setTool('line');

      // First click far from B — creates point A
      click(tool, scene, { x: 0, y: 0 });
      expect(scene.objects.size).toBe(2);

      // Second click ~5px from B — should snap to B, not create a third point
      click(tool, scene, { x: 101, y: 5 });

      const pointCount = [...scene.objects.values()].filter(o => o.kind === 'point').length;
      expect(pointCount).toBe(2); // still A and B, no third point
      expect(scene.objects.size).toBe(3); // + line construction
    });
  });

  describe('snapping — Shift bypasses snap', () => {
    it('Shift-click near an existing point creates a distinct new point instead of snapping', () => {
      scene.addPoint(0, 0);
      const tool = new ConstructionTool(CONSTRUCTION_CATALOG['line']);
      scene.setTool('line');

      // (5, 0) is within the 12px snap radius of (0, 0) without Shift
      // Shift disables both existing-point snap and grid snap
      click(tool, scene, { x: 5, y: 0 }, { shiftKey: true });

      const pointCount = [...scene.objects.values()].filter(o => o.kind === 'point').length;
      expect(pointCount).toBe(2); // original (0,0) + new point at (5,0)
    });
  });

  describe('validation — reject invalid construction', () => {
    it('selecting the same point twice for a line sets slotError and creates no line', () => {
      const tool = new ConstructionTool(CONSTRUCTION_CATALOG['line']);
      scene.setTool('line');

      // First click at (0,0) — creates point A, slot accepted
      const accepted1 = click(tool, scene, { x: 0, y: 0 });
      expect(accepted1).toBe(true);
      expect(scene.objects.size).toBe(1);

      // Second click at (5,0) — snaps back to A (within 12px), validate rejects same-point
      const accepted2 = click(tool, scene, { x: 5, y: 0 });
      expect(accepted2).toBe(false);
      expect(scene.slotError).not.toBeNull();

      // No line created; only the one original point
      expect(scene.objects.size).toBe(1);
      const kinds = [...scene.objects.values()].map(o => o.kind);
      expect(kinds).not.toContain('construction');
    });

    it('a zero-area rectangle is rejected with slotError', () => {
      const tool = new ConstructionTool(CONSTRUCTION_CATALOG['rectangle']);
      scene.setTool('rectangle');

      click(tool, scene, { x: 0, y: 0 });
      // Second corner on same row — zero-area, should be rejected
      const accepted = click(tool, scene, { x: 100, y: 0 });

      expect(accepted).toBe(false);
      expect(scene.slotError).not.toBeNull();
    });
  });

  describe('cancel mid-construction (onDeactivate)', () => {
    it('onDeactivate rolls back any point created during the in-progress construction', () => {
      const tool = new ConstructionTool(CONSTRUCTION_CATALOG['line']);
      scene.setTool('line');

      click(tool, scene, { x: 0, y: 0 }); // creates point A, slot 1 of 2
      expect(scene.objects.size).toBe(1);

      tool.onDeactivate({ scene });
      expect(scene.objects.size).toBe(0); // A was rolled back
    });

    it('after onDeactivate the tool slot resets to 0', () => {
      const tool = new ConstructionTool(CONSTRUCTION_CATALOG['line']);
      scene.setTool('line');

      click(tool, scene, { x: 0, y: 0 });
      tool.onDeactivate({ scene });

      expect(tool.captureState().currentSlotIndex).toBe(0);
    });

    it('onDeactivate preserves pre-existing points that were snapped to (not created)', () => {
      scene.addPoint(0, 0); // pre-existing — not in createdInSlots
      const tool = new ConstructionTool(CONSTRUCTION_CATALOG['line']);
      scene.setTool('line');

      // Click exactly on the pre-existing point: snaps, does not create a new point
      click(tool, scene, { x: 0, y: 0 });
      expect(scene.objects.size).toBe(1); // still just the pre-existing point

      tool.onDeactivate({ scene });
      expect(scene.objects.size).toBe(1); // pre-existing point survives
    });
  });

  describe('undo', () => {
    it('undo after the first click of a line removes the created point and resets the slot', () => {
      const tool = new ConstructionTool(CONSTRUCTION_CATALOG['line']);
      scene.setTool('line');

      click(tool, scene, { x: 0, y: 0 });
      expect(scene.objects.size).toBe(1);

      scene.undo();

      expect(scene.objects.size).toBe(0);
      expect(tool.captureState().currentSlotIndex).toBe(0);
    });

    it('undo after completing a line removes the construction and the last-placed point', () => {
      const tool = new ConstructionTool(CONSTRUCTION_CATALOG['line']);
      scene.setTool('line');

      click(tool, scene, { x: 0, y: 0 });
      click(tool, scene, { x: 200, y: 0 });
      expect(scene.objects.size).toBe(3);

      scene.undo();

      // Reverts to state before second click — only point A remains
      expect(scene.objects.size).toBe(1);
      expect(tool.captureState().currentSlotIndex).toBe(1);
    });

    it('two undos after a complete line restore an empty scene', () => {
      const tool = new ConstructionTool(CONSTRUCTION_CATALOG['line']);
      scene.setTool('line');

      click(tool, scene, { x: 0, y: 0 });
      click(tool, scene, { x: 200, y: 0 });

      scene.undo();
      scene.undo();

      expect(scene.objects.size).toBe(0);
      expect(tool.captureState().currentSlotIndex).toBe(0);
    });

    it('undo on an empty stack returns false', () => {
      expect(scene.undo()).toBe(false);
    });
  });

  describe('JGEX generation', () => {
    it('empty scene emits an empty string', () => {
      expect(emitScene(scene)).toBe('');
    });

    it('two free points emit as "a = free a; b = free b"', () => {
      scene.addPoint(0, 0);
      scene.addPoint(100, 0);

      expect(emitScene(scene)).toBe('a = free a; b = free b');
    });

    it('midpoint construction emits base points as free and midpoint via midpoint clause', () => {
      scene.addPoint(0, 0);
      scene.addPoint(200, 0);

      const tool = new ConstructionTool(CONSTRUCTION_CATALOG['midpoint']);
      scene.setTool('midpoint');

      click(tool, scene, { x: 0, y: 0 });
      click(tool, scene, { x: 200, y: 0 });

      // Name table assigns letters by insertion order: A->(0,0)='a', B->(200,0)='b', M=(midpoint)='c'
      expect(emitScene(scene)).toBe('a = free a; b = free b; c = midpoint c a b');
    });

    it('rectangle emits all four corners in a single clause with no free-point prefix', () => {
      const tool = new ConstructionTool(CONSTRUCTION_CATALOG['rectangle']);
      scene.setTool('rectangle');

      click(tool, scene, { x: 0, y: 0 });
      click(tool, scene, { x: 100, y: 50 });

      // All four corners are "produced" — no free-point clauses
      expect(emitScene(scene)).toBe('a c b d = rectangle a c b d');
    });
  });
});
