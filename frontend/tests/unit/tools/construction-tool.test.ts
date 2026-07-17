import { describe, it, expect, vi } from 'vitest';
import { ConstructionTool } from '../../../src/tools/construction-tool';
import { Scene } from '../../../src/scene/scene';
import { world, screen } from '../../../src/geometry/coords';
import type { CatalogEntry } from '../../../src/construction/catalog-types';
import type { ToolContext } from '../../../src/tools/tool';
import type { ObjectId } from '../../../src/geometry/types-object';

function makeCtx(scene: Scene, wx: number, wy: number, shiftKey = false): ToolContext {
  return { scene, world: world(wx, wy), screen: screen(0, 0), scale: 50, shiftKey };
}

// Minimal CatalogEntry builder — callers override only what the test needs.
function makeEntry(overrides: Partial<CatalogEntry> = {}): CatalogEntry {
  return {
    name: 'test_tool',
    label: 'Test',
    shortcut: 't',
    icon: () => document.createElementNS('http://www.w3.org/2000/svg', 'svg'),
    slots: [],
    edges: [],
    circles: [],
    sketch: () => null,
    ...overrides,
  };
}

// ── currentSlotLabel ─────────────────────────────────────────────────────────

describe('ConstructionTool.currentSlotLabel', () => {
  it('returns null when no construction is in progress (0 slots)', () => {
    const tool = new ConstructionTool(makeEntry({ slots: [] }));
    expect(tool.currentSlotLabel()).toBeNull();
  });

  it('returns the current slot label while in progress', () => {
    const tool = new ConstructionTool(makeEntry({
      slots: [{ name: 'a', kind: 'pick', label: 'Pick first point' }],
    }));
    expect(tool.currentSlotLabel()).toBe('Pick first point');
  });
});

// ── captureState / restoreState ──────────────────────────────────────────────

describe('ConstructionTool.captureState / restoreState', () => {
  it('round-trips bindings, slotIndex, and createdInSlots', () => {
    // 2 slots so the first click doesn't trigger completion + reset
    const tool = new ConstructionTool(makeEntry({
      slots: [
        { name: 'a', kind: 'pick', label: 'A' },
        { name: 'b', kind: 'pick', label: 'B' },
      ],
    }));
    const scene = new Scene();
    const id = scene.addPoint(0, 0);
    tool.onClick(makeCtx(scene, 0, 0)); // fills slot 0 (snaps to existing)

    const state = tool.captureState();
    expect(state.currentSlotIndex).toBe(1);
    expect(state.bindings['a']).toBe(id);

    const fresh = new ConstructionTool(makeEntry({
      slots: [{ name: 'a', kind: 'pick', label: 'A' }],
    }));
    fresh.restoreState(state);
    const restored = fresh.captureState();
    expect(restored).toEqual(state);
  });

  it('restoreState with no createdInSlots array defaults to empty set', () => {
    const tool = new ConstructionTool(makeEntry());
    tool.restoreState({ bindings: {}, currentSlotIndex: 0, createdInSlots: [] });
    expect(tool.captureState().createdInSlots).toEqual([]);
  });

  it('restoreState with undefined createdInSlots uses ?? [] fallback', () => {
    const tool = new ConstructionTool(makeEntry());
    // Simulate old snapshot without createdInSlots field
    tool.restoreState({ bindings: {}, currentSlotIndex: 0, createdInSlots: undefined as never });
    expect(tool.captureState().createdInSlots).toEqual([]);
  });
});

// ── onClick: 'pick' slot ─────────────────────────────────────────────────────

describe('ConstructionTool.onClick – pick slot', () => {
  it('snaps to an existing point within range', () => {
    const scene = new Scene();
    const existingId = scene.addPoint(1, 1);
    // 2 slots so the first click doesn't trigger completion + reset
    const tool = new ConstructionTool(makeEntry({
      slots: [
        { name: 'a', kind: 'pick', label: 'A' },
        { name: 'b', kind: 'pick', label: 'B' },
      ],
    }));
    tool.onClick(makeCtx(scene, 1, 1));
    expect(tool.captureState().bindings['a']).toBe(existingId);
    expect(scene.objects.size).toBe(1); // no extra point created
  });

  it('creates a new point when nothing is nearby', () => {
    const scene = new Scene();
    const tool = new ConstructionTool(makeEntry({
      slots: [
        { name: 'a', kind: 'pick', label: 'A' },
        { name: 'b', kind: 'pick', label: 'B' },
      ],
    }));
    tool.onClick(makeCtx(scene, 100, 200));
    expect(scene.objects.size).toBe(1);
    expect(tool.captureState().currentSlotIndex).toBe(1);
  });

  it('validates and sets slot error without leaking the point', () => {
    const scene = new Scene();
    const tool = new ConstructionTool(makeEntry({
      slots: [{ name: 'a', kind: 'pick', label: 'A' }],
      validate: () => 'bad pick',
    }));
    tool.onClick(makeCtx(scene, 100, 200));
    expect(scene.slotError).toBe('bad pick');
    expect(scene.objects.size).toBe(0); // created point was removed
    expect(tool.captureState().currentSlotIndex).toBe(0); // slot not advanced
  });

  it('validates error when snapping to existing point (wasCreated=false, no removal)', () => {
    const scene = new Scene();
    scene.addPoint(1, 1); // point already in scene
    const tool = new ConstructionTool(makeEntry({
      slots: [{ name: 'a', kind: 'pick', label: 'A' }],
      validate: () => 'bad snap',
    }));
    tool.onClick(makeCtx(scene, 1, 1));
    expect(scene.slotError).toBe('bad snap');
    expect(scene.objects.size).toBe(1); // original point still there
  });

  it('calls onSlotFilled after binding a slot', () => {
    const scene = new Scene();
    const onSlotFilled = vi.fn();
    const tool = new ConstructionTool(makeEntry({
      slots: [{ name: 'a', kind: 'pick', label: 'A' }],
      onSlotFilled,
    }));
    tool.onClick(makeCtx(scene, 0, 0));
    expect(onSlotFilled).toHaveBeenCalledOnce();
    expect(onSlotFilled.mock.calls[0][0]).toBe('a');
  });
});

// ── onClick: 'pick-existing' slot ────────────────────────────────────────────

describe('ConstructionTool.onClick – pick-existing slot', () => {
  it('sets slot error when cursor is over empty space', () => {
    const scene = new Scene();
    const tool = new ConstructionTool(makeEntry({
      slots: [{ name: 'a', kind: 'pick-existing', label: 'A' }],
    }));
    tool.onClick(makeCtx(scene, 50, 50));
    expect(scene.slotError).toBe('Click on an existing point');
    expect(tool.captureState().currentSlotIndex).toBe(0);
  });

  it('advances slot when cursor is on an existing point', () => {
    const scene = new Scene();
    const id = scene.addPoint(0, 0);
    const tool = new ConstructionTool(makeEntry({
      slots: [
        { name: 'a', kind: 'pick-existing', label: 'A' },
        { name: 'b', kind: 'pick', label: 'B' },
      ],
    }));
    tool.onClick(makeCtx(scene, 0, 0));
    expect(tool.captureState().bindings['a']).toBe(id);
    expect(tool.captureState().currentSlotIndex).toBe(1);
  });
});

// ── onClick: 'place-free' slot ────────────────────────────────────────────────

describe('ConstructionTool.onClick – place-free slot', () => {
  it('always drops a new point regardless of nearby points', () => {
    const scene = new Scene();
    const existingId = scene.addPoint(5, 5);
    const tool = new ConstructionTool(makeEntry({
      slots: [{ name: 'a', kind: 'place-free', label: 'A' }],
    }));
    tool.onClick(makeCtx(scene, 5, 5));
    expect(scene.objects.size).toBe(2); // new point created alongside existing
    const newId = tool.captureState().bindings['a'];
    expect(newId).not.toBe(existingId);
  });
});

// ── onClick: 'derive' slot ────────────────────────────────────────────────────

describe('ConstructionTool.onClick – derive slot', () => {
  it('projects the cursor and creates a point at the projected position', () => {
    const scene = new Scene();
    const baseId = scene.addPoint(0, 0);
    // 3 slots so derive click doesn't trigger completion + reset
    const tool = new ConstructionTool(makeEntry({
      slots: [
        { name: 'base', kind: 'pick', label: 'Base' },
        {
          name: 'derived',
          kind: 'derive',
          label: 'Derived',
          preview: () => [],
          project: (_b, _s, cursor) => world(cursor.x, 0), // project onto x-axis
        },
        { name: 'extra', kind: 'pick', label: 'Extra' },
      ],
    }));
    tool.onClick(makeCtx(scene, 0, 0)); // fill 'base' by snapping to existing
    expect(tool.captureState().bindings['base']).toBe(baseId);
    tool.onClick(makeCtx(scene, 3, 7)); // cursor at (3,7) → projected to (3,0)
    const state = tool.captureState();
    expect(state.currentSlotIndex).toBe(2);
    const derivedId = state.bindings['derived'];
    const derived = scene.objects.get(derivedId);
    expect(derived?.kind).toBe('point');
    if (derived?.kind === 'point') {
      expect(derived.x).toBe(3);
      expect(derived.y).toBe(0);
    }
  });
});

// ── onClick: unknown slot kind ────────────────────────────────────────────────

describe('ConstructionTool.onClick – unknown slot kind', () => {
  it('warns and returns without advancing', () => {
    const scene = new Scene();
    const warn = vi.spyOn(console, 'warn').mockImplementation(() => {});
    const tool = new ConstructionTool(makeEntry({
      slots: [{ name: 'a', kind: 'scalar' as never, label: 'A' }],
    }));
    tool.onClick(makeCtx(scene, 0, 0));
    expect(warn).toHaveBeenCalled();
    expect(tool.captureState().currentSlotIndex).toBe(0);
    warn.mockRestore();
  });
});

// ── onClick: construction completion ─────────────────────────────────────────

describe('ConstructionTool.onClick – completion', () => {
  it('calls sketch and addObject when all slots are filled', () => {
    const scene = new Scene();
    const addObject = vi.spyOn(scene, 'addObject');
    const tool = new ConstructionTool(makeEntry({
      slots: [{ name: 'a', kind: 'place-free', label: 'A' }],
      sketch: (b) => ({ kind: 'circle', mode: 'center-through' as const, center: b['a'] as ObjectId, through: b['a'] as ObjectId }),
    }));
    tool.onClick(makeCtx(scene, 0, 0));
    expect(addObject).toHaveBeenCalled();
    expect(tool.captureState().currentSlotIndex).toBe(0); // reset after completion
  });

  it('resets after sketch returns null (sketch created everything)', () => {
    const scene = new Scene();
    const tool = new ConstructionTool(makeEntry({
      slots: [{ name: 'a', kind: 'place-free', label: 'A' }],
      sketch: () => null,
    }));
    tool.onClick(makeCtx(scene, 0, 0));
    expect(tool.captureState().currentSlotIndex).toBe(0);
    expect(tool.captureState().bindings).toEqual({});
  });

  it('detects circle duplicate on completion and sets error', () => {
    const scene = new Scene();
    // Pre-populate a circle in the scene
    const centerId = scene.addPoint(0, 0);
    const throughId = scene.addPoint(3, 0);
    scene.addObject({ kind: 'circle', mode: 'center-through', center: centerId, through: throughId });

    const tool = new ConstructionTool(makeEntry({
      slots: [
        { name: 'center', kind: 'pick', label: 'Center' },
        { name: 'through', kind: 'pick', label: 'Through' },
      ],
      sketch: (b) => ({
        kind: 'circle',
        mode: 'center-through' as const,
        center: b['center'] as ObjectId,
        through: b['through'] as ObjectId,
      }),
    }));

    tool.onClick(makeCtx(scene, 0, 0));  // snap to centerId
    tool.onClick(makeCtx(scene, 3, 0));  // snap to throughId → same circle → duplicate
    expect(scene.slotError).toBe('This construction already exists');
    expect(tool.captureState().currentSlotIndex).toBe(0); // reset
  });

  it('isDuplicateConstruction returns false when new circle has nonexistent center/through', () => {
    const scene = new Scene();
    // Pre-populate a real circle so the loop runs at least once
    const c = scene.addPoint(0, 0);
    const t = scene.addPoint(1, 0);
    scene.addObject({ kind: 'circle', mode: 'center-through', center: c, through: t });

    const badId = 'nonexistent_id' as ObjectId;
    const tool = new ConstructionTool(makeEntry({
      slots: [{ name: 'a', kind: 'place-free', label: 'A' }],
      sketch: () => ({
        kind: 'circle' as const,
        mode: 'center-through' as const,
        center: badId,   // nonexistent → !center → return false
        through: badId,
      }),
    }));
    tool.onClick(makeCtx(scene, 5, 5, true));
    // isDuplicateConstruction returns false (center not found), so no duplicate error
    expect(scene.slotError).not.toBe('This construction already exists');
  });

  it('circle with invalid center/through IDs in existing circle is skipped (continue branch)', () => {
    const scene = new Scene();
    // Add a circle with nonexistent point IDs — the duplicate check must skip it gracefully
    scene.addObject({ kind: 'circle', mode: 'center-through', center: 'bad1' as ObjectId, through: 'bad2' as ObjectId });

    const centerId = scene.addPoint(0, 0);
    const throughId = scene.addPoint(3, 0);

    const tool = new ConstructionTool(makeEntry({
      slots: [
        { name: 'center', kind: 'place-free', label: 'Center' },
        { name: 'through', kind: 'place-free', label: 'Through' },
      ],
      sketch: (b) => ({
        kind: 'circle',
        mode: 'center-through' as const,
        center: b['center'] as ObjectId,
        through: b['through'] as ObjectId,
      }),
    }));

    // Place fresh points (not snapping to existing)
    tool.onClick(makeCtx(scene, 0, 0, true));   // shift → always creates
    tool.onClick(makeCtx(scene, 3, 0, true));

    // New circle (center=0,0, r=3) doesn't match the bad-IDs one → no duplicate error
    expect(scene.slotError).not.toBe('This construction already exists');
    // Suppress unused variable warnings
    void centerId; void throughId;
  });

  it('detects duplicate construction via coordinate multiset match', () => {
    const scene = new Scene();
    const p1 = scene.addPoint(1, 0);
    const p2 = scene.addPoint(2, 0);
    // Pre-populate a matching construction
    scene.addObject({
      kind: 'construction',
      name: 'test_tool',
      bindings: { a: p1, b: p2 },
      edges: [],
      circles: [],
    });

    const tool = new ConstructionTool(makeEntry({
      slots: [
        { name: 'a', kind: 'pick', label: 'A' },
        { name: 'b', kind: 'pick', label: 'B' },
      ],
      sketch: (b) => ({
        kind: 'construction' as const,
        name: 'test_tool',
        bindings: b as Record<string, ObjectId>,
        edges: [],
        circles: [],
      }),
    }));

    tool.onClick(makeCtx(scene, 1, 0)); // snaps to p1
    tool.onClick(makeCtx(scene, 2, 0)); // snaps to p2 → same coords → duplicate
    expect(scene.slotError).toBe('This construction already exists');
  });

  it('detects construction duplicate via line geometry (linesAllMatch)', () => {
    const scene = new Scene();
    // p1, p2, p3 all on x-axis — p1-p2 and p1-p3 define the same infinite line
    const p1 = scene.addPoint(0, 0);
    scene.addPoint(4, 0);
    const p3 = scene.addPoint(2, 0);

    // Existing construction with different bindings ({a: p1, b: p3}) but same line
    scene.addObject({
      kind: 'construction',
      name: 'test_tool',
      bindings: { a: p1, b: p3 },
      edges: [],
      circles: [],
      lines: [[p1, p3]],
    });

    const tool = new ConstructionTool(makeEntry({
      slots: [
        { name: 'a', kind: 'pick', label: 'A' },
        { name: 'b', kind: 'pick', label: 'B' },
      ],
      sketch: (b) => ({
        kind: 'construction' as const,
        name: 'test_tool',
        bindings: b as Record<string, ObjectId>,
        edges: [],
        circles: [],
        lines: [[b['a'] as ObjectId, b['b'] as ObjectId]],
      }),
    }));

    tool.onClick(makeCtx(scene, 0, 0)); // snap p1
    tool.onClick(makeCtx(scene, 4, 0)); // snap p2 → coords differ from (p1,p3) but line matches
    expect(scene.slotError).toBe('This construction already exists');
  });

  it('does not flag duplicate when lines do not match', () => {
    const scene = new Scene();
    const p1 = scene.addPoint(0, 0);
    scene.addPoint(4, 0);
    const p3 = scene.addPoint(0, 5); // off x-axis

    // Existing construction with perpendicular line (different geometry)
    scene.addObject({
      kind: 'construction',
      name: 'test_tool',
      bindings: { a: p3 },
      edges: [],
      circles: [],
      lines: [[p3, p1]],
    });

    const tool = new ConstructionTool(makeEntry({
      slots: [
        { name: 'a', kind: 'pick', label: 'A' },
        { name: 'b', kind: 'pick', label: 'B' },
      ],
      sketch: (b) => ({
        kind: 'construction' as const,
        name: 'test_tool',
        bindings: b as Record<string, ObjectId>,
        edges: [],
        circles: [],
        lines: [[b['a'] as ObjectId, b['b'] as ObjectId]],
      }),
    }));

    tool.onClick(makeCtx(scene, 0, 0)); // snap p1
    tool.onClick(makeCtx(scene, 4, 0)); // snap p2 → x-axis line; existing is vertical → no duplicate
    expect(scene.slotError).not.toBe('This construction already exists');
  });

  it('linesAllMatch returns false when new line endpoints do not exist in scene', () => {
    const scene = new Scene();
    scene.addPoint(0, 0);
    scene.addPoint(4, 0);

    // Existing construction whose bindings produce different coords
    const p3 = scene.addPoint(10, 10);
    scene.addObject({
      kind: 'construction',
      name: 'test_tool',
      bindings: { a: p3 },
      edges: [],
      circles: [],
      lines: [[p3, p3]],
    });

    const badId = 'nonexistent' as ObjectId;
    const tool = new ConstructionTool(makeEntry({
      slots: [
        { name: 'a', kind: 'pick', label: 'A' },
        { name: 'b', kind: 'pick', label: 'B' },
      ],
      sketch: (b) => ({
        kind: 'construction' as const,
        name: 'test_tool',
        bindings: b as Record<string, ObjectId>,
        edges: [],
        circles: [],
        // lines reference bad IDs → linesAllMatch's p1-not-found branch fires
        lines: [[badId, badId]],
      }),
    }));

    tool.onClick(makeCtx(scene, 0, 0)); // snap p1
    tool.onClick(makeCtx(scene, 4, 0)); // snap p2 → coords differ; lines have bad IDs → not dup
    expect(scene.slotError).not.toBe('This construction already exists');
  });

  it('isDuplicateConstruction: circle in scene does not match new circle (false branch of match check)', () => {
    const scene = new Scene();
    // Existing circle at center (0,0), radius 3
    const c1 = scene.addPoint(0, 0);
    const t1 = scene.addPoint(3, 0);
    scene.addObject({ kind: 'circle', mode: 'center-through', center: c1, through: t1 });

    // New circle has DIFFERENT center (10,10) → not a duplicate
    const c2 = scene.addPoint(10, 10);
    const t2 = scene.addPoint(13, 10);

    const tool = new ConstructionTool(makeEntry({
      slots: [
        { name: 'center', kind: 'pick', label: 'Center' },
        { name: 'through', kind: 'pick', label: 'Through' },
      ],
      sketch: (b) => ({
        kind: 'circle' as const,
        mode: 'center-through' as const,
        center: b['center'] as ObjectId,
        through: b['through'] as ObjectId,
      }),
    }));
    tool.onClick(makeCtx(scene, 10, 10)); // snap to c2
    tool.onClick(makeCtx(scene, 13, 10)); // snap to t2 → different circle → no duplicate
    expect(scene.slotError).not.toBe('This construction already exists');
    void c2; void t2;
  });

  it('isDuplicateConstruction: sketch returns a point (neither circle nor construction) → false', () => {
    const scene = new Scene();
    // Pre-populate so the early `if (!obj)` check doesn't terminate early
    const tool = new ConstructionTool(makeEntry({
      slots: [{ name: 'a', kind: 'place-free', label: 'A' }],
      // sketch returns a point object (not circle/construction)
      sketch: () => ({ kind: 'point' as const, x: 5, y: 5, label: 'X' }),
    }));
    tool.onClick(makeCtx(scene, 99, 99, true));
    // obj.kind is 'point' → falls through both if-blocks → returns false → no duplicate error
    expect(scene.slotError).not.toBe('This construction already exists');
  });

  it('isDuplicateConstruction: constructions with same name, different coords, no lines → no duplicate', () => {
    const scene = new Scene();
    const p1 = scene.addPoint(0, 0);
    const p2 = scene.addPoint(10, 10); // different location

    // Existing construction with no lines array
    scene.addObject({
      kind: 'construction',
      name: 'test_tool',
      bindings: { a: p2 },
      edges: [],
      circles: [],
      // no lines field → obj.lines?.length is falsy → skips linesAllMatch
    });

    const tool = new ConstructionTool(makeEntry({
      slots: [
        { name: 'a', kind: 'pick', label: 'A' },
        { name: 'b', kind: 'pick', label: 'B' },
      ],
      sketch: (b) => ({
        kind: 'construction' as const,
        name: 'test_tool',
        bindings: b as Record<string, ObjectId>,
        edges: [],
        circles: [],
        // no lines field either → both lines?.length falsy → skip linesAllMatch
      }),
    }));

    tool.onClick(makeCtx(scene, 0, 0)); // snap p1
    // We need a second point that doesn't match p2
    const p3 = scene.addPoint(5, 5);
    void p3;
    tool.onClick(makeCtx(scene, 5, 5)); // snap p3 → coords differ, no lines → not duplicate
    expect(scene.slotError).not.toBe('This construction already exists');
    void p1;
  });

  it('linesAllMatch: existing construction line has bad IDs (inner continue branch)', () => {
    const scene = new Scene();
    scene.addPoint(0, 0);
    scene.addPoint(4, 0);
    const p3 = scene.addPoint(10, 10); // different coords from (p1,p2)

    const badId = 'bad' as ObjectId;
    scene.addObject({
      kind: 'construction',
      name: 'test_tool',
      bindings: { a: p3 },
      edges: [],
      circles: [],
      lines: [[badId, badId]], // existing line has bad IDs → inner !p2||!q2 branch
    });

    const tool = new ConstructionTool(makeEntry({
      slots: [
        { name: 'a', kind: 'pick', label: 'A' },
        { name: 'b', kind: 'pick', label: 'B' },
      ],
      sketch: (b) => ({
        kind: 'construction' as const,
        name: 'test_tool',
        bindings: b as Record<string, ObjectId>,
        edges: [],
        circles: [],
        lines: [[b['a'] as ObjectId, b['b'] as ObjectId]],
      }),
    }));

    tool.onClick(makeCtx(scene, 0, 0)); // snap p1
    tool.onClick(makeCtx(scene, 4, 0)); // snap p2
    // coords differ from (p3) → not coord-match; lines check runs but bad existing IDs → no match → no dup
    expect(scene.slotError).not.toBe('This construction already exists');
  });

  it('removes derive-slot points when duplicate is detected', () => {
    const scene = new Scene();
    const p1 = scene.addPoint(0, 0);
    scene.addObject({
      kind: 'construction',
      name: 'test_tool',
      bindings: { base: p1 },
      edges: [],
      circles: [],
    });

    let sketchCreatedId: ObjectId | undefined;
    const tool = new ConstructionTool(makeEntry({
      slots: [
        { name: 'base', kind: 'pick', label: 'Base' },
        {
          name: 'derived',
          kind: 'derive',
          label: 'Derived',
          preview: () => [],
          project: () => world(0, 0),
        },
      ],
      sketch: (_b, s) => {
        // sketch creates an extra point and returns a construction
        sketchCreatedId = s.addPoint(99, 99);
        return {
          kind: 'construction' as const,
          name: 'test_tool',
          bindings: { base: p1 },
          edges: [],
          circles: [],
        };
      },
    }));

    tool.onClick(makeCtx(scene, 0, 0)); // snap to p1
    tool.onClick(makeCtx(scene, 1, 0)); // derive step → completion → duplicate detected

    expect(scene.slotError).toBe('This construction already exists');
    // sketch-created point must be cleaned up
    if (sketchCreatedId) expect(scene.objects.has(sketchCreatedId)).toBe(false);
  });
});

// ── onClick: empty entry (no slots) ──────────────────────────────────────────

describe('ConstructionTool.onClick – no slot defined', () => {
  it('returns immediately when currentSlotIndex is out of bounds', () => {
    const scene = new Scene();
    const tool = new ConstructionTool(makeEntry({ slots: [] }));
    // Should not throw; no state change
    expect(() => tool.onClick(makeCtx(scene, 0, 0))).not.toThrow();
  });
});

// ── onDeactivate ─────────────────────────────────────────────────────────────

describe('ConstructionTool.onDeactivate', () => {
  it('removes points created during slots and resets state', () => {
    const scene = new Scene();
    const tool = new ConstructionTool(makeEntry({
      slots: [
        { name: 'a', kind: 'place-free', label: 'A' },
        { name: 'b', kind: 'place-free', label: 'B' },
      ],
    }));
    tool.onClick(makeCtx(scene, 10, 20)); // creates point a
    expect(scene.objects.size).toBe(1);

    tool.onDeactivate({ scene });

    expect(scene.objects.size).toBe(0); // created point removed
    expect(tool.captureState().currentSlotIndex).toBe(0);
    expect(tool.captureState().bindings).toEqual({});
  });

  it('does not remove snapped-to existing points', () => {
    const scene = new Scene();
    const existingId = scene.addPoint(1, 1);
    const tool = new ConstructionTool(makeEntry({
      slots: [{ name: 'a', kind: 'pick', label: 'A' }],
    }));
    tool.onClick(makeCtx(scene, 1, 1)); // snap to existing

    tool.onDeactivate({ scene });

    expect(scene.objects.has(existingId)).toBe(true);
  });
});

// ── onMove ────────────────────────────────────────────────────────────────────

describe('ConstructionTool.onMove', () => {
  it('returns [] when no slots defined', () => {
    const scene = new Scene();
    const tool = new ConstructionTool(makeEntry({ slots: [] }));
    expect(tool.onMove(makeCtx(scene, 0, 0))).toEqual([]);
  });

  it('pick slot returns snapHighlight', () => {
    const scene = new Scene();
    scene.addPoint(0, 0);
    const tool = new ConstructionTool(makeEntry({
      slots: [{ name: 'a', kind: 'pick', label: 'A' }],
    }));
    const previews = tool.onMove(makeCtx(scene, 0, 0));
    expect(previews.some(p => p.kind === 'highlightPoint')).toBe(true);
  });

  it('pick-existing slot returns existingPointHighlight', () => {
    const scene = new Scene();
    scene.addPoint(0, 0);
    const tool = new ConstructionTool(makeEntry({
      slots: [{ name: 'a', kind: 'pick-existing', label: 'A' }],
    }));
    const previews = tool.onMove(makeCtx(scene, 0, 0));
    expect(previews.some(p => p.kind === 'highlightPoint')).toBe(true);
  });

  it('place-free slot returns gridSnapHighlight', () => {
    const scene = new Scene();
    const tool = new ConstructionTool(makeEntry({
      slots: [{ name: 'a', kind: 'place-free', label: 'A' }],
    }));
    // Near grid intersection (0,0) at scale=50
    const previews = tool.onMove(makeCtx(scene, 0.05, 0.05));
    expect(previews.some(p => p.kind === 'highlightPoint')).toBe(true);
  });

  it('derive slot: shows preview aux geometry + projected highlight', () => {
    const scene = new Scene();
    const baseId = scene.addPoint(0, 0);
    const tool = new ConstructionTool(makeEntry({
      slots: [
        { name: 'base', kind: 'pick', label: 'Base' },
        {
          name: 'derived',
          kind: 'derive',
          label: 'Derived',
          preview: () => [
            { kind: 'auxLine', from: world(0, 0), to: world(1, 0) },
            { kind: 'circle', center: world(0, 0), through: world(1, 0) },
            { kind: 'point', at: world(0.5, 0) },
          ],
          project: (_b, _s, cursor) => cursor,
        },
      ],
    }));
    tool.onClick(makeCtx(scene, 0, 0)); // fills 'base'
    expect(tool.captureState().bindings['base']).toBe(baseId);

    const previews = tool.onMove(makeCtx(scene, 2, 3));
    const kinds = previews.map(p => p.kind);
    expect(kinds).toContain('auxLine');
    expect(kinds).toContain('rubberCircle');
    expect(kinds).toContain('highlightPoint');
  });

  it('entry-level preview emits auxLine, rubberCircle, and highlightPoint', () => {
    const scene = new Scene();
    const tool = new ConstructionTool(makeEntry({
      slots: [{ name: 'a', kind: 'pick', label: 'A' }],
      preview: () => [
        { kind: 'auxLine', from: world(0, 0), to: world(1, 0) },
        { kind: 'circle', center: world(0, 0), through: world(1, 0) },
        { kind: 'point', at: world(0, 0) },
      ],
    }));
    const previews = tool.onMove(makeCtx(scene, 0, 0));
    const kinds = previews.map(p => p.kind);
    expect(kinds).toContain('auxLine');
    expect(kinds).toContain('rubberCircle');
    expect(kinds).toContain('highlightPoint');
  });

  it('partial edges are emitted for already-bound slots', () => {
    // Use 3 slots so both a and b can be bound without triggering completion,
    // then onMove shows the partialEdge between them.
    const scene = new Scene();
    const p1 = scene.addPoint(0, 0);
    const p2 = scene.addPoint(3, 0);
    const tool = new ConstructionTool(makeEntry({
      slots: [
        { name: 'a', kind: 'pick', label: 'A' },
        { name: 'b', kind: 'pick', label: 'B' },
        { name: 'c', kind: 'pick', label: 'C' }, // extra slot so completion doesn't fire yet
      ],
      edges: [{ pointIds: ['a', 'b'] }],
    }));
    tool.onClick(makeCtx(scene, 0, 0)); // fills 'a' (snap to p1)
    tool.onClick(makeCtx(scene, 3, 0)); // fills 'b' (snap to p2) — slotIndex now 2, not complete

    const previews = tool.onMove(makeCtx(scene, 5, 0));
    expect(previews.some(p => p.kind === 'partialEdge')).toBe(true);
    void p1; void p2;
  });

  it('partial edge is skipped when endpoint object is not a point', () => {
    const scene = new Scene();
    // 'a' bound to a point; 'b' not yet bound → no partial edge
    const tool = new ConstructionTool(makeEntry({
      slots: [
        { name: 'a', kind: 'pick', label: 'A' },
        { name: 'b', kind: 'pick', label: 'B' },
      ],
      edges: [{ pointIds: ['a', 'b'] }],
    }));
    // Nothing in scene, fresh cursor far from grid
    const previews = tool.onMove(makeCtx(scene, 50, 50));
    expect(previews.filter(p => p.kind === 'partialEdge')).toHaveLength(0);
  });

  it('derive slot: unknown aux.kind hits the implicit-else of the point branch', () => {
    const scene = new Scene();
    scene.addPoint(0, 0);
    const tool = new ConstructionTool(makeEntry({
      slots: [
        { name: 'base', kind: 'pick', label: 'Base' },
        {
          name: 'derived',
          kind: 'derive',
          label: 'Derived',
          preview: (() => [{ kind: 'unknown_aux' }]) as never, // none of auxLine/circle/point
          project: (_b, _s, cursor) => cursor,
        },
        { name: 'extra', kind: 'pick', label: 'E' },
      ],
    }));
    tool.onClick(makeCtx(scene, 0, 0));
    // Unknown kind falls through all three else-ifs without error
    expect(() => tool.onMove(makeCtx(scene, 1, 0))).not.toThrow();
  });

  it('entry-level preview: unknown p.kind hits the implicit-else of the point branch', () => {
    const scene = new Scene();
    const tool = new ConstructionTool(makeEntry({
      slots: [{ name: 'a', kind: 'pick', label: 'A' }, { name: 'b', kind: 'pick', label: 'B' }],
      preview: (() => [{ kind: 'unknown_preview' }]) as never,
    }));
    // Unknown kind falls through all three else-ifs without error
    expect(() => tool.onMove(makeCtx(scene, 0, 0))).not.toThrow();
  });

  it('scalar slot produces no cursor preview', () => {
    const scene = new Scene();
    const tool = new ConstructionTool(makeEntry({
      slots: [{ name: 'n', kind: 'scalar', label: 'N' }],
    }));
    // onMove with scalar slot falls through with empty previews
    const previews = tool.onMove(makeCtx(scene, 0, 0));
    expect(previews.filter(p => p.kind !== 'highlightPoint')).toHaveLength(0);
  });

  it('partial edge is skipped when bound id points to a non-point object', () => {
    // Manually inject bindings where 'a' is a circle id (not a point)
    const scene = new Scene();
    const cCenter = scene.addPoint(0, 0);
    const cThrough = scene.addPoint(3, 0);
    const circleId = scene.addObject({ kind: 'circle', mode: 'center-through', center: cCenter, through: cThrough });

    const tool = new ConstructionTool(makeEntry({
      slots: [
        { name: 'a', kind: 'pick', label: 'A' },
        { name: 'b', kind: 'pick', label: 'B' },
        { name: 'c', kind: 'pick', label: 'C' },
      ],
      edges: [{ pointIds: ['a', 'b'] }],
    }));
    // 'a' is a circle id, 'b' is a valid point
    tool.restoreState({ bindings: { a: circleId as never, b: cThrough }, currentSlotIndex: 2, createdInSlots: [] });

    const previews = tool.onMove(makeCtx(scene, 0, 0));
    expect(previews.filter(p => p.kind === 'partialEdge')).toHaveLength(0);
  });
});
