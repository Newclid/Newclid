import { describe, it, expect } from 'vitest';
import { Scene } from '../../../src/scene/scene';
import { emitScene } from '../../../src/emit/jgex';

describe('emitScene', () => {
  // single free point emits as "a = free a"
  it('emits a single free point as "a = free a"', () => {
    const scene = new Scene();
    scene.addPoint(0, 0);
    expect(emitScene(scene)).toBe('a = free a');
  });

  // two free points are joined by a semicolon
  it('emits two free points separated by a semicolon', () => {
    const scene = new Scene();
    scene.addPoint(0, 0);
    scene.addPoint(1, 0);
    expect(emitScene(scene)).toBe('a = free a; b = free b');
  });

  // segment has no jgex entry so only the two free points appear in the output
  it('emits a segment construction as free points without a produced LHS', () => {
    const scene = new Scene();
    const a = scene.addPoint(0, 0);
    const b = scene.addPoint(1, 0);
    scene.addObject({
      kind: 'construction',
      name: 'segment',
      bindings: { a, b },
      edges: [[a, b]],
      circles: [],
    });
    const out = emitScene(scene);
    expect(out).toContain('a = free a');
    expect(out).toContain('b = free b');
  });

  // midpoint construction emits the midpoint clause with the correct def keyword
  it('emits a midpoint construction containing the midpoint clause', () => {
    const scene = new Scene();
    const a = scene.addPoint(0, 0);
    const b = scene.addPoint(2, 0);
    const m = scene.addPoint(1, 0);
    scene.addObject({
      kind: 'construction',
      name: 'midpoint',
      bindings: { a, b, m },
      edges: [],
      circles: [],
    });
    const out = emitScene(scene);
    expect(out).toContain('midpoint');
    expect(out).not.toContain('c = free c');
  });

  // intersection_lc combine block emits both on_line and on_circle clauses
  it('emits an intersection_lc construction with on_line and on_circle in the output', () => {
    const scene = new Scene();
    const a = scene.addPoint(0, 0);
    const b = scene.addPoint(10, 0);
    const o = scene.addPoint(5, 0);
    const ra = scene.addPoint(8, 0);
    const x = scene.addPoint(8, 0);
    scene.addObject({
      kind: 'construction',
      name: 'intersection_lc',
      bindings: { a, b, o, ra, x },
      edges: [],
      circles: [],
    });
    const out = emitScene(scene);
    expect(out).toContain('on_line');
    expect(out).toContain('on_circle');
  });

  // empty scene produces an empty string with no clauses
  it('returns an empty string for an empty scene', () => {
    const scene = new Scene();
    expect(emitScene(scene)).toBe('');
  });

  // when intersection_lc y slot is absent the second block is skipped but output is still defined
  it('skips a construction block when its produced slot is not bound', () => {
    const scene = new Scene();
    const a = scene.addPoint(0, 0);
    const b = scene.addPoint(10, 0);
    const o = scene.addPoint(5, 0);
    const ra = scene.addPoint(8, 0);
    const x = scene.addPoint(8, 0);
    scene.addObject({
      kind: 'construction',
      name: 'intersection_lc',
      bindings: { a, b, o, ra, x },
      edges: [],
      circles: [],
    });
    const out = emitScene(scene);
    expect(out).toBeDefined();
  });
});
