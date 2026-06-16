import { describe, it, expect } from 'vitest';
import { Scene } from '../../../../src/scene/scene';
import { select } from '../../../../src/construction/entries/select';

describe('select entry', () => {
  it('has no slots, edges or circles', () => {
    expect(select.slots).toEqual([]);
    expect(select.edges).toEqual([]);
    expect(select.circles).toEqual([]);
  });

  it('never sketches anything', () => {
    const scene = new Scene();
    expect(select.sketch({}, scene)).toBeNull();
  });
});
