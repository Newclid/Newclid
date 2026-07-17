import { describe, it, expect } from 'vitest';
import { Scene } from '../../../../src/scene/scene';
import { addPoints } from '../../../helpers/scene';
import { circle } from '../../../../src/construction/entries/circle';

describe('circle entry sketch', () => {
  it('emits a center-through circle from the picked centre and radius point', () => {
    const scene = new Scene();
    const { a, b } = addPoints(scene, { a: [0, 0], b: [3, 0] });
    expect(circle.sketch({ a, b }, scene)).toEqual({
      kind: 'circle', mode: 'center-through', center: a, through: b,
    });
  });
});

describe('circle entry preview', () => {
  it('previews the circle through the cursor once the centre is picked', () => {
    const scene = new Scene();
    const { a } = addPoints(scene, { a: [0, 0] });
    const preview = circle.preview!({ a }, scene, { x: 3, y: 4 } as never);
    expect(preview).toEqual([{ kind: 'circle', center: { x: 0, y: 0 }, through: { x: 3, y: 4 } }]);
  });

  it('previews nothing before the centre is picked', () => {
    const scene = new Scene();
    expect(circle.preview!({}, scene, { x: 3, y: 4 } as never)).toEqual([]);
  });
});

describe('circle entry validate', () => {
  it('rejects the centre and radius point being the same', () => {
    const scene = new Scene();
    const { a } = addPoints(scene, { a: [0, 0] });
    expect(circle.validate!({ a, b: a }, scene)).toMatch(/distinct/);
  });

  it('accepts distinct points', () => {
    const scene = new Scene();
    const { a, b } = addPoints(scene, { a: [0, 0], b: [1, 0] });
    expect(circle.validate!({ a, b }, scene)).toBeNull();
  });

  it('accepts an incomplete binding', () => {
    const scene = new Scene();
    const { a } = addPoints(scene, { a: [0, 0] });
    expect(circle.validate!({ a }, scene)).toBeNull();
  });
});
