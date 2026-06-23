import { describe, it, expect } from 'vitest';
import { Scene } from '../../../src/scene/scene';
import { buildNameTable } from '../../../src/emit/names';

describe('buildNameTable', () => {
  // names the first 26 points a through z
  it('names the first 26 points a through z', () => {
    const scene = new Scene();
    for (let i = 0; i < 26; i++) scene.addPoint(i, 0);
    const table = buildNameTable(scene);
    const names = [...table.values()];
    expect(names[0]).toBe('a');
    expect(names[25]).toBe('z');
  });

  // names the 27th point a1 and the 28th b1, covering the suffix case
  it('names the 27th point a1 and the 28th b1', () => {
    const scene = new Scene();
    for (let i = 0; i < 28; i++) scene.addPoint(i, 0);
    const table = buildNameTable(scene);
    const names = [...table.values()];
    expect(names[26]).toBe('a1');
    expect(names[27]).toBe('b1');
  });

  // skips non-point objects when building the name table
  it('skips non-point objects (circles)', () => {
    const scene = new Scene();
    const a = scene.addPoint(0, 0);
    const b = scene.addPoint(1, 0);
    scene.addObject({ kind: 'circle', mode: 'center-through', center: a, through: b });
    const table = buildNameTable(scene);
    expect(table.size).toBe(2); // only two points
  });
});
