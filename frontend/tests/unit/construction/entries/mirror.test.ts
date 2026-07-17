import { describe, it, expect } from 'vitest';
import { Scene } from '../../../../src/scene/scene';
import { addPoints } from '../../../helpers/scene';
import { mirror } from '../../../../src/construction/entries/mirror';

describe('mirror entry slots', () => {
  it('has two pick slots and no edges or circles', () => {
    expect(mirror.slots.map(s => s.kind)).toEqual(['pick', 'pick']);
    expect(mirror.edges).toEqual([]);
    expect(mirror.circles).toEqual([]);
  });
});

describe('mirror entry sketch', () => {
  it('places the reflected image at 2b - a', () => {
    const scene = new Scene();
    const { a, b } = addPoints(scene, { a: [0, 0], b: [3, 0] });
    const result = mirror.sketch({ a, b }, scene);

    expect(result).toMatchObject({
      kind: 'construction',
      name: 'mirror',
      bindings: { a, b },
      edges: [[a, expect.any(String)]],
      circles: [],
    });

    const xId = (result as { bindings: Record<string, string> }).bindings.x;
    const x = scene.objects.get(xId)!;
    expect(x.kind).toBe('point');
    if (x.kind === 'point') {
      expect(x.x).toBeCloseTo(6);
      expect(x.y).toBeCloseTo(0);
    }
  });

  it('handles non-horizontal reflection', () => {
    const scene = new Scene();
    const { a, b } = addPoints(scene, { a: [1, 2], b: [4, 5] });
    const result = mirror.sketch({ a, b }, scene);
    const xId = (result as { bindings: Record<string, string> }).bindings.x;
    const x = scene.objects.get(xId)!;
    if (x.kind === 'point') {
      expect(x.x).toBeCloseTo(7); // 2*4 - 1
      expect(x.y).toBeCloseTo(8); // 2*5 - 2
    }
  });
});

describe('mirror entry preview', () => {
  it('previews the reflected image and auxiliary lines once a is placed', () => {
    const scene = new Scene();
    const { a } = addPoints(scene, { a: [0, 0] });
    const cursor = { x: 3, y: 0, _kind: 'world' as const };
    const prev = mirror.preview!({ a }, scene, cursor);
    // Should emit an auxLine, a point for the cursor (center), and a point for the image
    expect(prev.length).toBe(3);
    expect(prev[0].kind).toBe('auxLine');
    expect(prev[1].kind).toBe('point');
    expect(prev[2].kind).toBe('point');
  });

  it('previews nothing before a is placed', () => {
    const scene = new Scene();
    const cursor = { x: 3, y: 0, _kind: 'world' as const };
    expect(mirror.preview!({}, scene, cursor)).toEqual([]);
  });
});

describe('mirror entry validate', () => {
  it('rejects a === b', () => {
    const scene = new Scene();
    const { a } = addPoints(scene, { a: [0, 0] });
    expect(mirror.validate!({ a, b: a }, scene)).toMatch(/distinct/i);
  });

  it('accepts distinct points', () => {
    const scene = new Scene();
    const { a, b } = addPoints(scene, { a: [0, 0], b: [1, 0] });
    expect(mirror.validate!({ a, b }, scene)).toBeNull();
  });

  it('accepts partial binding', () => {
    const scene = new Scene();
    expect(mirror.validate!({}, scene)).toBeNull();
  });
});
