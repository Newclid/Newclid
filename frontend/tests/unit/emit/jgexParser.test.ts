import { describe, it, expect } from 'vitest';
import {
  parseConstructionSignature,
  expandJgexPredicates,
  geomFromSignatures,
  parseJgexGeometry,
} from '../../../src/emit/jgexParser';

describe('parseConstructionSignature', () => {
  it('returns null for an empty string', () => {
    expect(parseConstructionSignature('')).toBeNull();
  });

  it('returns null for a single token (no args)', () => {
    expect(parseConstructionSignature('midpoint')).toBeNull();
  });

  it('parses a well-formed signature', () => {
    expect(parseConstructionSignature('midpoint c a b')).toEqual({
      kind: 'midpoint',
      args: ['c', 'a', 'b'],
    });
  });

  it('handles extra surrounding and internal whitespace', () => {
    expect(parseConstructionSignature('  segment  a  b  ')).toEqual({
      kind: 'segment',
      args: ['a', 'b'],
    });
  });
});

describe('expandJgexPredicates', () => {
  it('returns the string unchanged when there is no "?" separator', () => {
    const s = 'a = free a; b = free b';
    expect(expandJgexPredicates(s)).toBe(s);
  });

  it('does not expand a coll goal with 3 or fewer args', () => {
    const s = 'a = free a ? coll a b c';
    expect(expandJgexPredicates(s)).toBe(s);
  });

  it('expands a coll goal with 4 args into sliding windows of 3', () => {
    const out = expandJgexPredicates('a = free a ? coll a b c d');
    expect(out).toBe('a = free a ? coll a b c; coll b c d');
  });

  it('expands a cyclic goal with 5 args into windows of 4', () => {
    const out = expandJgexPredicates('a = free a ? cyclic a b c d e');
    expect(out).toBe('a = free a ? cyclic a b c d; cyclic b c d e');
  });

  it('expands a circle goal (center + 4 points) into windows of 3 over non-center args', () => {
    const out = expandJgexPredicates('a = free a ? circle o a b c d');
    expect(out).toBe('a = free a ? circle o a b c; circle o b c d');
  });

  it('passes through a non-expandable goal unchanged', () => {
    const s = 'a = free a ? para a b c d';
    expect(expandJgexPredicates(s)).toBe(s);
  });

  it('does not expand setup clauses that contain "="', () => {
    const s = 'c = midpoint c a b ? coll a b c';
    const out = expandJgexPredicates(s);
    expect(out.split(' ? ')[0]).toBe('c = midpoint c a b');
  });
});

describe('geomFromSignatures', () => {
  it('returns an empty array for an empty input', () => {
    expect(geomFromSignatures([])).toEqual([]);
  });

  it('returns an empty array for an unknown predicate', () => {
    expect(geomFromSignatures(['unknown a b c'])).toEqual([]);
  });

  it('midp produces a line through the two endpoint args', () => {
    expect(geomFromSignatures(['midp m a b'])).toEqual([
      { kind: 'line', p1: 'a', p2: 'b' },
    ]);
  });

  it('coll produces a line through the first two args', () => {
    expect(geomFromSignatures(['coll a b'])).toEqual([
      { kind: 'line', p1: 'a', p2: 'b' },
    ]);
  });

  it('perp produces two lines', () => {
    const result = geomFromSignatures(['perp a b c d']);
    expect(result).toHaveLength(2);
    expect(result.every(g => g.kind === 'line')).toBe(true);
  });

  it('cong produces two segments', () => {
    const result = geomFromSignatures(['cong a b c d']);
    expect(result).toHaveLength(2);
    expect(result.every(g => g.kind === 'segment')).toBe(true);
  });

  it('cyclic produces a circumcircle', () => {
    expect(geomFromSignatures(['cyclic a b c'])).toEqual([
      { kind: 'circumcircle', p1: 'a', p2: 'b', p3: 'c' },
    ]);
  });

  it('eqangle produces four lines', () => {
    const result = geomFromSignatures(['eqangle a b c d e f g h']);
    expect(result).toHaveLength(4);
    expect(result.every(g => g.kind === 'line')).toBe(true);
  });

  it('eqratio produces four segments', () => {
    const result = geomFromSignatures(['eqratio a b c d e f g h']);
    expect(result).toHaveLength(4);
    expect(result.every(g => g.kind === 'segment')).toBe(true);
  });
});

describe('parseJgexGeometry', () => {
  it('returns an empty array for an empty string', () => {
    expect(parseJgexGeometry('')).toEqual([]);
  });

  it('returns an empty array when the setup part is empty (only goal)', () => {
    expect(parseJgexGeometry('? coll a b c')).toEqual([]);
  });

  it('returns an empty array for a free construction', () => {
    expect(parseJgexGeometry('a = free a')).toEqual([]);
  });

  it('parses a segment construction', () => {
    expect(parseJgexGeometry('a = segment a b')).toEqual([
      { kind: 'segment', p1: 'a', p2: 'b' },
    ]);
  });

  it('parses a triangle construction into three segments', () => {
    const result = parseJgexGeometry('a = triangle a b c');
    expect(result).toHaveLength(3);
    expect(result.every(g => g.kind === 'segment')).toBe(true);
  });

  it('parses a midpoint construction as a line through the two base points', () => {
    expect(parseJgexGeometry('m = midpoint m a b')).toEqual([
      { kind: 'line', p1: 'a', p2: 'b' },
    ]);
  });

  it('parses on_pline as two lines', () => {
    const result = parseJgexGeometry('x = on_pline x y a b');
    expect(result).toHaveLength(2);
    expect(result.every(g => g.kind === 'line')).toBe(true);
  });

  it('parses a circle construction as a circle plus triangle', () => {
    const result = parseJgexGeometry('x = circle x a b c');
    expect(result.some(g => g.kind === 'circle')).toBe(true);
    expect(result.filter(g => g.kind === 'segment')).toHaveLength(3);
  });

  it('parses on_circle as a single circle', () => {
    expect(parseJgexGeometry('x = on_circle x o a')).toEqual([
      { kind: 'circle', center: 'o', through: 'a' },
    ]);
  });

  it('ignores everything after "?"', () => {
    const withGoal = parseJgexGeometry('m = midpoint m a b ? coll a b m');
    const withoutGoal = parseJgexGeometry('m = midpoint m a b');
    expect(withGoal).toEqual(withoutGoal);
  });

  it('ignores everything after "|"', () => {
    const withAux = parseJgexGeometry('m = midpoint m a b | aux');
    const withoutAux = parseJgexGeometry('m = midpoint m a b');
    expect(withAux).toEqual(withoutAux);
  });

  it('handles multiple clauses and returns geometry from each', () => {
    const result = parseJgexGeometry('a = free a; b = free b; m = midpoint m a b');
    // free produces nothing; midpoint produces a line
    expect(result).toEqual([{ kind: 'line', p1: 'a', p2: 'b' }]);
  });

  it('handles a comma-joined combine block (intersection_lc style)', () => {
    const result = parseJgexGeometry('x = on_line x a b, on_circle x o ra');
    expect(result.some(g => g.kind === 'line')).toBe(true);
    expect(result.some(g => g.kind === 'circle')).toBe(true);
  });
});
