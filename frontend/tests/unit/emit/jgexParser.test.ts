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

  it('expands a bare setup clause without "=" via expandGoal', () => {
    // A raw predicate in the setup (no "=") should be passed through expandGoal.
    // coll with 4 args expands into windows.
    const out = expandJgexPredicates('coll a b c d ? perp a b c d');
    expect(out.startsWith('coll a b c; coll b c d')).toBe(true);
  });

  it('filters out empty goal clauses', () => {
    // trailing separator produces an empty goal token which is dropped
    const out = expandJgexPredicates('a = free a ? coll a b c; ');
    expect(out.endsWith('coll a b c')).toBe(true);
  });

  it('does not expand a cyclic goal with 4 or fewer args', () => {
    const s = 'a = free a ? cyclic a b c d';
    expect(expandJgexPredicates(s)).toBe(s);
  });

  it('does not expand a circle goal with 4 or fewer args', () => {
    const s = 'a = free a ? circle o a b c d';
    // 4 non-center args → args.length (5) > 4, so this WILL expand
    // use 3 non-center args to stay at ≤4:
    const s2 = 'a = free a ? circle o a b c';
    expect(expandJgexPredicates(s2)).toBe(s2);
  });
});

describe('geomFromSignatures', () => {
  it('returns an empty array for an empty input', () => {
    expect(geomFromSignatures([])).toEqual([]);
  });

  it('skips a signature that is empty or whitespace-only', () => {
    expect(geomFromSignatures([''])).toEqual([]);
    expect(geomFromSignatures(['   '])).toEqual([]);
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

  it('para produces two lines', () => {
    const result = geomFromSignatures(['para a b c d']);
    expect(result).toHaveLength(2);
    expect(result.every(g => g.kind === 'line')).toBe(true);
  });

  it('circle predicate produces a circle', () => {
    expect(geomFromSignatures(['circle o a'])).toEqual([
      { kind: 'circle', center: 'o', through: 'a' },
    ]);
  });

  it('simtri predicate produces six segments (two triangles)', () => {
    expect(geomFromSignatures(['simtri a b c d e f'])).toHaveLength(6);
  });

  it('contri predicate produces six segments (two triangles)', () => {
    expect(geomFromSignatures(['contri a b c d e f'])).toHaveLength(6);
  });

  it('eqangle returns empty when fewer than 8 args', () => {
    expect(geomFromSignatures(['eqangle a b c d'])).toEqual([]);
  });

  it('eqratio returns empty when fewer than 8 args', () => {
    expect(geomFromSignatures(['eqratio a b c d'])).toEqual([]);
  });

  it('midp returns empty when endpoint args are missing', () => {
    expect(geomFromSignatures(['midp m'])).toEqual([]);
  });

  it('coll returns empty when fewer than 2 args', () => {
    expect(geomFromSignatures(['coll a'])).toEqual([]);
  });

  it('perp returns empty when any of the four args is missing', () => {
    expect(geomFromSignatures(['perp a b c'])).toEqual([]);
  });

  it('cong returns empty when any of the four args is missing', () => {
    expect(geomFromSignatures(['cong a b c'])).toEqual([]);
  });

  it('cyclic returns empty when fewer than 3 args', () => {
    expect(geomFromSignatures(['cyclic a b'])).toEqual([]);
  });

  it('circle predicate returns empty when fewer than 2 args', () => {
    expect(geomFromSignatures(['circle o'])).toEqual([]);
  });

  it('simtri predicate returns empty when fewer than 6 args', () => {
    expect(geomFromSignatures(['simtri a b c d e'])).toEqual([]);
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

  // --- geomForConstruction: remaining switch arms ---

  it('acute_triangle falls through to the triangle case → 3 segments', () => {
    expect(parseJgexGeometry('a = acute_triangle a b c')).toHaveLength(3);
  });

  it('triangle12 falls through to the triangle case → 3 segments', () => {
    expect(parseJgexGeometry('a = triangle12 a b c')).toHaveLength(3);
  });

  it('iso_triangle produces a triangle', () => {
    expect(parseJgexGeometry('c = iso_triangle c a b')).toHaveLength(3);
  });

  it('iso_triangle0 produces a triangle', () => {
    expect(parseJgexGeometry('c = iso_triangle0 c a b')).toHaveLength(3);
  });

  it('iso_triangle_vertex produces a triangle', () => {
    expect(parseJgexGeometry('c = iso_triangle_vertex c a b')).toHaveLength(3);
  });

  it('r_triangle produces a triangle (3 segments)', () => {
    expect(parseJgexGeometry('c = r_triangle c a b')).toHaveLength(3);
  });

  it('quadrangle produces a quadrilateral (4 segments)', () => {
    expect(parseJgexGeometry('a = quadrangle a b c d')).toHaveLength(4);
  });

  it('rectangle produces a quadrilateral', () => {
    expect(parseJgexGeometry('a = rectangle a b c d')).toHaveLength(4);
  });

  it('square produces a quadrilateral', () => {
    expect(parseJgexGeometry('a = square a b c d')).toHaveLength(4);
  });

  it('pentagon produces 5 segments', () => {
    expect(parseJgexGeometry('a = pentagon a b c d e')).toHaveLength(5);
  });

  it('circumcenter produces a circle plus triangle (same as circle case)', () => {
    const result = parseJgexGeometry('x = circumcenter x a b c');
    expect(result.some(g => g.kind === 'circle')).toBe(true);
    expect(result.filter(g => g.kind === 'segment')).toHaveLength(3);
  });

  it('circle with missing args returns empty', () => {
    expect(parseJgexGeometry('x = circle x a b')).toEqual([]);
  });

  it('on_circum produces a circumcircle plus triangle', () => {
    const result = parseJgexGeometry('x = on_circum x a b c');
    expect(result.some(g => g.kind === 'circumcircle')).toBe(true);
    expect(result.filter(g => g.kind === 'segment')).toHaveLength(3);
  });

  it('between produces a line', () => {
    expect(parseJgexGeometry('m = between m a b')).toEqual([{ kind: 'line', p1: 'a', p2: 'b' }]);
  });

  it('between_bound produces a line', () => {
    expect(parseJgexGeometry('m = between_bound m a b')).toEqual([{ kind: 'line', p1: 'a', p2: 'b' }]);
  });

  it('trisegment produces a line', () => {
    expect(parseJgexGeometry('m = trisegment m a b')).toEqual([{ kind: 'line', p1: 'a', p2: 'b' }]);
  });

  it('on_line produces a line', () => {
    expect(parseJgexGeometry('x = on_line x a b')).toEqual([{ kind: 'line', p1: 'a', p2: 'b' }]);
  });

  it('on_pline0 produces two lines', () => {
    const result = parseJgexGeometry('x = on_pline0 x y a b');
    expect(result).toHaveLength(2);
    expect(result.every(g => g.kind === 'line')).toBe(true);
  });

  it('on_tline produces two lines', () => {
    const result = parseJgexGeometry('x = on_tline x y a b');
    expect(result).toHaveLength(2);
    expect(result.every(g => g.kind === 'line')).toBe(true);
  });

  it('angle_bisector produces three lines', () => {
    const result = parseJgexGeometry('x = angle_bisector x a b c');
    expect(result).toHaveLength(3);
    expect(result.every(g => g.kind === 'line')).toBe(true);
  });

  it('on_dia produces two lines', () => {
    const result = parseJgexGeometry('x = on_dia x a b');
    expect(result).toHaveLength(2);
    expect(result.every(g => g.kind === 'line')).toBe(true);
  });

  it('foot produces two lines (altitude and base)', () => {
    const result = parseJgexGeometry('f = foot f a b c');
    expect(result).toHaveLength(2);
    expect(result.every(g => g.kind === 'line')).toBe(true);
  });

  it('intersection_ll produces two lines', () => {
    const result = parseJgexGeometry('x = intersection_ll x a b c d');
    expect(result).toHaveLength(2);
    expect(result.every(g => g.kind === 'line')).toBe(true);
  });

  it('intersection_lp produces two lines', () => {
    const result = parseJgexGeometry('x = intersection_lp x a b c m n');
    expect(result).toHaveLength(2);
    expect(result.every(g => g.kind === 'line')).toBe(true);
  });

  it('intersection_pp produces two lines and two segments', () => {
    const result = parseJgexGeometry('x = intersection_pp x a b c d e f');
    expect(result.filter(g => g.kind === 'line')).toHaveLength(2);
    expect(result.filter(g => g.kind === 'segment')).toHaveLength(2);
  });

  it('intersection_lt produces three lines', () => {
    const result = parseJgexGeometry('x = intersection_lt x a b c d e');
    expect(result).toHaveLength(3);
    expect(result.every(g => g.kind === 'line')).toBe(true);
  });

  it('intersection_tt produces four lines', () => {
    const result = parseJgexGeometry('x = intersection_tt x a b c d e f');
    expect(result).toHaveLength(4);
    expect(result.every(g => g.kind === 'line')).toBe(true);
  });

  it('intersection_lc (via geomForConstruction) produces a line, circle, and segment', () => {
    const result = parseJgexGeometry('intersection_lc x a o b');
    expect(result.some(g => g.kind === 'line')).toBe(true);
    expect(result.some(g => g.kind === 'circle')).toBe(true);
    expect(result.some(g => g.kind === 'segment')).toBe(true);
  });

  it('intersection_cc produces two circles and two segments', () => {
    const result = parseJgexGeometry('x = intersection_cc x o w a');
    expect(result.filter(g => g.kind === 'circle')).toHaveLength(2);
    expect(result.filter(g => g.kind === 'segment')).toHaveLength(2);
  });

  it('incenter produces triangle sides plus three lines to the incenter', () => {
    const result = parseJgexGeometry('d = incenter d a b c');
    expect(result).toHaveLength(6);
  });

  it('excenter produces the same shape as incenter', () => {
    const result = parseJgexGeometry('d = excenter d a b c');
    expect(result).toHaveLength(6);
  });

  it('simtri produces two triangles (6 segments)', () => {
    expect(parseJgexGeometry('r = simtri r a b c p q')).toHaveLength(6);
  });

  it('simtrir produces two triangles (6 segments)', () => {
    expect(parseJgexGeometry('r = simtrir r a b c p q')).toHaveLength(6);
  });

  it('contri produces two triangles (6 segments)', () => {
    expect(parseJgexGeometry('q = contri q r a b c p')).toHaveLength(6);
  });

  it('contrir produces two triangles (6 segments)', () => {
    expect(parseJgexGeometry('q = contrir q r a b c p')).toHaveLength(6);
  });

  it('shift produces two segments', () => {
    const result = parseJgexGeometry('x = shift x b c d');
    expect(result).toHaveLength(2);
    expect(result.every(g => g.kind === 'segment')).toBe(true);
  });

  it('mirror produces two segments', () => {
    const result = parseJgexGeometry('x = mirror x a b');
    expect(result).toHaveLength(2);
    expect(result.every(g => g.kind === 'segment')).toBe(true);
  });

  it('reflect produces a line and a segment', () => {
    const result = parseJgexGeometry('x = reflect x a b c');
    expect(result.some(g => g.kind === 'line')).toBe(true);
    expect(result.some(g => g.kind === 'segment')).toBe(true);
  });

  it('clause without "=" is parsed as a bare construction name', () => {
    expect(parseJgexGeometry('segment a b')).toEqual([
      { kind: 'segment', p1: 'a', p2: 'b' },
    ]);
  });

  it('skips empty comma-split tokens within a clause', () => {
    // A trailing comma produces an empty token after split; the words.length guard skips it.
    const withTrailing = parseJgexGeometry('a = segment a b,');
    const withoutTrailing = parseJgexGeometry('a = segment a b');
    expect(withTrailing).toEqual(withoutTrailing);
  });
});
