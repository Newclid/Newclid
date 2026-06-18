import { describe, it, expect } from 'vitest';
import { Scene } from '../../../../src/scene/scene';
import { addPoints } from '../../../helpers/scene';
import { tangentLine } from '../../../../src/construction/entries/tangent_line';

describe('tangent_line entry slots', () => {
  it('has two pick slots and no edges or circles', () => {
    expect(tangentLine.slots.map(s => s.kind)).toEqual(['pick', 'pick']);
    expect(tangentLine.edges).toEqual([]);
    expect(tangentLine.circles).toEqual([]);
  });
});

describe('tangent_line entry sketch', () => {
  it('creates the tangent at a to the circle with centre o', () => {
    const scene = new Scene();
    // Circle: center o=(0,0), tangency point a=(3,0): radius=3, tangent is vertical
    const { a, o } = addPoints(scene, { a: [3, 0], o: [0, 0] });
    const result = tangentLine.sketch({ a, o }, scene);

    expect(result).toMatchObject({
      kind: 'construction',
      name: 'lc_tangent',
      bindings: { a, o },
      edges: [[o, a]],
    });

    // x is the second point on the tangent line, perpendicular to radius o-a
    const xId = (result as { bindings: Record<string, string> }).bindings.x;
    const x = scene.objects.get(xId)!;
    expect(x.kind).toBe('point');
    if (x.kind === 'point') {
      // Tangent to circle at (3,0): should be vertical, so x is at (3, ±3)
      expect(x.x).toBeCloseTo(3);
    }

    const lines = (result as { lines?: [string, string][] }).lines;
    expect(lines).toEqual([[a, xId]]);

    // Should also emit the circle
    const circles = (result as { circles: { center: string; radius: number }[] }).circles;
    expect(circles).toHaveLength(1);
    expect(circles[0].center).toBe(o);
    expect(circles[0].radius).toBeCloseTo(3);
  });
});

describe('tangent_line entry preview', () => {
  it('previews the circle and tangent line through the cursor', () => {
    const scene = new Scene();
    const { a } = addPoints(scene, { a: [3, 0] });
    const cursor = { x: 0, y: 0, _kind: 'world' as const };
    const prev = tangentLine.preview!({ a }, scene, cursor);
    expect(prev).toHaveLength(2);
    expect(prev[0].kind).toBe('circle');
    expect(prev[1].kind).toBe('auxLine');
  });

  it('previews nothing before a is placed', () => {
    const scene = new Scene();
    const cursor = { x: 0, y: 0, _kind: 'world' as const };
    expect(tangentLine.preview!({}, scene, cursor)).toEqual([]);
  });

  it('previews nothing when cursor equals a (zero radius)', () => {
    const scene = new Scene();
    const { a } = addPoints(scene, { a: [3, 0] });
    const cursor = { x: 3, y: 0, _kind: 'world' as const };
    expect(tangentLine.preview!({ a }, scene, cursor)).toEqual([]);
  });
});

describe('tangent_line entry validate', () => {
  it('rejects a === o', () => {
    const scene = new Scene();
    const { a } = addPoints(scene, { a: [3, 0] });
    expect(tangentLine.validate!({ a, o: a }, scene)).toMatch(/distinct/i);
  });

  it('accepts distinct a and o', () => {
    const scene = new Scene();
    const { a, o } = addPoints(scene, { a: [3, 0], o: [0, 0] });
    expect(tangentLine.validate!({ a, o }, scene)).toBeNull();
  });

  it('accepts partial binding', () => {
    const scene = new Scene();
    expect(tangentLine.validate!({}, scene)).toBeNull();
  });
});
