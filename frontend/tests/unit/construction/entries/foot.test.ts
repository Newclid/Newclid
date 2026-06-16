import { describe, it, expect } from 'vitest';
import { Scene } from '../../../../src/scene/scene';
import { addPoints } from '../../../helpers/scene';
import { foot } from '../../../../src/construction/entries/foot';

describe('foot entry slots', () => {
  it('has three pick slots and no edges or circles', () => {
    expect(foot.slots.map(s => s.kind)).toEqual(['pick', 'pick', 'pick']);
    expect(foot.edges).toEqual([]);
  });
});

describe('foot entry sketch', () => {
  it('drops a perpendicular from p to the horizontal line a-b', () => {
    const scene = new Scene();
    const { a, b, p } = addPoints(scene, { a: [0, 0], b: [6, 0], p: [3, 4] });
    const result = foot.sketch({ a, b, p }, scene);

    expect(result).toMatchObject({
      kind: 'construction',
      name: 'foot',
      bindings: { a, b, p },
      circles: [],
    });

    const fId = (result as { bindings: Record<string, string> }).bindings.f;
    const f = scene.objects.get(fId)!;
    expect(f.kind).toBe('point');
    if (f.kind === 'point') {
      expect(f.x).toBeCloseTo(3);
      expect(f.y).toBeCloseTo(0);
    }

    const edges = (result as { edges: [string, string][] }).edges;
    expect(edges).toEqual([[p, fId]]);
  });

  it('projects correctly onto a diagonal line', () => {
    const scene = new Scene();
    // Line y = x through origin: a=(0,0), b=(4,4), p=(0,4)
    const { a, b, p } = addPoints(scene, { a: [0, 0], b: [4, 4], p: [0, 4] });
    const result = foot.sketch({ a, b, p }, scene);
    const fId = (result as { bindings: Record<string, string> }).bindings.f;
    const f = scene.objects.get(fId)!;
    if (f.kind === 'point') {
      expect(f.x).toBeCloseTo(2);
      expect(f.y).toBeCloseTo(2);
    }
  });

  it('colors the foot point red', () => {
    const scene = new Scene();
    const { a, b, p } = addPoints(scene, { a: [0, 0], b: [6, 0], p: [3, 4] });
    const result = foot.sketch({ a, b, p }, scene);
    const fId = (result as { bindings: Record<string, string> }).bindings.f;
    const f = scene.objects.get(fId)!;
    if (f.kind === 'point') expect(f.color).toBe('red');
  });
});

describe('foot entry preview', () => {
  it('shows the drop from cursor to its foot when a and b are set', () => {
    const scene = new Scene();
    const { a, b } = addPoints(scene, { a: [0, 0], b: [6, 0] });
    const cursor = { x: 3, y: 4, _kind: 'world' as const };
    const prev = foot.preview!({ a, b }, scene, cursor);
    expect(prev).toHaveLength(1);
    expect(prev[0].kind).toBe('auxLine');
  });

  it('shows nothing when a or b is missing', () => {
    const scene = new Scene();
    const cursor = { x: 3, y: 4, _kind: 'world' as const };
    expect(foot.preview!({}, scene, cursor)).toEqual([]);
  });

  it('shows nothing when a and b are the same point (degenerate reference line)', () => {
    const scene = new Scene();
    const { a } = addPoints(scene, { a: [0, 0] });
    const cursor = { x: 3, y: 4, _kind: 'world' as const };
    expect(foot.preview!({ a, b: a }, scene, cursor)).toEqual([]);
  });
});

describe('foot entry validate', () => {
  it('rejects a === b', () => {
    const scene = new Scene();
    const { a } = addPoints(scene, { a: [0, 0] });
    expect(foot.validate!({ a, b: a }, scene)).toMatch(/distinct/i);
  });

  it('rejects p on the reference line', () => {
    const scene = new Scene();
    const { a, b, p } = addPoints(scene, { a: [0, 0], b: [4, 0], p: [2, 0] });
    expect(foot.validate!({ a, b, p }, scene)).toMatch(/not lie on/i);
  });

  it('accepts p off the reference line', () => {
    const scene = new Scene();
    const { a, b, p } = addPoints(scene, { a: [0, 0], b: [4, 0], p: [2, 3] });
    expect(foot.validate!({ a, b, p }, scene)).toBeNull();
  });

  it('accepts partial binding', () => {
    const scene = new Scene();
    expect(foot.validate!({}, scene)).toBeNull();
  });
});
