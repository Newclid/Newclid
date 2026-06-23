import { describe, it, expect } from 'vitest';
import {
  PREDICATE_DEFINITIONS,
  PREDICATE_BY_ID,
  predicateToJgex,
  extraArgLabel,
} from '../../../src/types/theorem';

describe('PREDICATE_BY_ID', () => {
  it('size equals PREDICATE_DEFINITIONS length', () => {
    expect(PREDICATE_BY_ID.size).toBe(PREDICATE_DEFINITIONS.length);
  });

  it('every map key matches the entry id', () => {
    for (const [key, def] of PREDICATE_BY_ID.entries()) {
      expect(key).toBe(def.id);
    }
  });

  it('all PREDICATE_DEFINITIONS ids appear in the map', () => {
    for (const def of PREDICATE_DEFINITIONS) {
      expect(PREDICATE_BY_ID.has(def.id)).toBe(true);
    }
  });

  it('cong has jgexName cong and minArgs 4', () => {
    const def = PREDICATE_BY_ID.get('cong');
    expect(def?.jgexName).toBe('cong');
    expect(def?.minArgs).toBe(4);
  });

  it('eqangle6 and eqangle8 both have jgexName eqangle', () => {
    expect(PREDICATE_BY_ID.get('eqangle6')?.jgexName).toBe('eqangle');
    expect(PREDICATE_BY_ID.get('eqangle8')?.jgexName).toBe('eqangle');
  });

  it('coll, cyclic, and circumcenter have variableArgs true', () => {
    expect(PREDICATE_BY_ID.get('coll')?.variableArgs).toBe(true);
    expect(PREDICATE_BY_ID.get('cyclic')?.variableArgs).toBe(true);
    expect(PREDICATE_BY_ID.get('circumcenter')?.variableArgs).toBe(true);
  });

  it('exactly rconst, r2const, lconst, l2const, aconst have a fraction argType', () => {
    const fractionIds = PREDICATE_DEFINITIONS
      .filter((def) => def.argTypes.includes('fraction'))
      .map((def) => def.id)
      .sort();
    expect(fractionIds).toEqual(['aconst', 'l2const', 'lconst', 'r2const', 'rconst']);
  });
});

describe('predicateToJgex', () => {
  it('returns "cong A B C D" for cong with four point args', () => {
    expect(predicateToJgex({ predicateId: 'cong', args: ['A', 'B', 'C', 'D'] })).toBe('cong A B C D');
  });

  it('returns "para A B C D" for para', () => {
    expect(predicateToJgex({ predicateId: 'para', args: ['A', 'B', 'C', 'D'] })).toBe('para A B C D');
  });

  it('uses jgexName "eqangle" for predicateId eqangle6', () => {
    expect(predicateToJgex({ predicateId: 'eqangle6', args: ['A', 'B', 'C', 'D', 'E', 'F'] }))
      .toBe('eqangle A B C D E F');
  });

  it('uses jgexName "eqangle" for predicateId eqangle8', () => {
    expect(predicateToJgex({ predicateId: 'eqangle8', args: ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H'] }))
      .toBe('eqangle A B C D E F G H');
  });

  it('joins args with a single space', () => {
    expect(predicateToJgex({ predicateId: 'midp', args: ['M', 'A', 'B'] })).toBe('midp M A B');
  });

  it('works for variable-arg predicate coll with 5 args', () => {
    expect(predicateToJgex({ predicateId: 'coll', args: ['A', 'B', 'C', 'D', 'E'] }))
      .toBe('coll A B C D E');
  });

  it('works for rconst with mixed point and fraction args', () => {
    expect(predicateToJgex({ predicateId: 'rconst', args: ['A', 'B', 'C', 'D', '1/2'] }))
      .toBe('rconst A B C D 1/2');
  });

  it('works for aconst with a pi-fraction constant', () => {
    expect(predicateToJgex({ predicateId: 'aconst', args: ['A', 'B', 'C', 'D', 'pi/4'] }))
      .toBe('aconst A B C D pi/4');
  });

  it('throws Error for an unknown predicateId', () => {
    expect(() => predicateToJgex({ predicateId: 'nonexistent', args: ['A', 'B'] }))
      .toThrow('Unknown predicate: nonexistent');
  });

  it('includes the unknown id in the thrown error message', () => {
    expect(() => predicateToJgex({ predicateId: 'xyz', args: [] }))
      .toThrow(/Unknown predicate: xyz/);
  });

  it('produces a trailing space for empty args (no arity validation in this function)', () => {
    expect(predicateToJgex({ predicateId: 'cong', args: [] })).toBe('cong ');
  });
});

describe('extraArgLabel', () => {
  it('returns A for index 0', () => {
    expect(extraArgLabel(0)).toBe('A');
  });

  it('returns B for index 1', () => {
    expect(extraArgLabel(1)).toBe('B');
  });

  it('returns Z for index 25', () => {
    expect(extraArgLabel(25)).toBe('Z');
  });

  it('returns P26 for index 26 (first index outside the A-Z range)', () => {
    expect(extraArgLabel(26)).toBe('P26');
  });

  it('returns P100 for index 100', () => {
    expect(extraArgLabel(100)).toBe('P100');
  });

  it('boundary: index 24 is Y and index 25 is Z', () => {
    expect(extraArgLabel(24)).toBe('Y');
    expect(extraArgLabel(25)).toBe('Z');
  });
});

describe('PREDICATE_DEFINITIONS shorthand functions', () => {
  // cong formats congruent segments with two segment pairs
  it('cong shorthand with four named args', () => {
    const def = PREDICATE_BY_ID.get('cong')!;
    expect(def.shorthand(['P', 'Q', 'R', 'S'])).toBe('|PQ| = |RS|');
  });

  // para formats parallel lines with two line pairs
  it('para shorthand with four named args', () => {
    const def = PREDICATE_BY_ID.get('para')!;
    expect(def.shorthand(['A', 'B', 'C', 'D'])).toBe('AB ∥ CD');
  });

  // perp formats perpendicular lines with two line pairs
  it('perp shorthand with four named args', () => {
    const def = PREDICATE_BY_ID.get('perp')!;
    expect(def.shorthand(['A', 'B', 'C', 'D'])).toBe('AB ⊥ CD');
  });

  // midp formats midpoint statement with point and segment
  it('midp shorthand with three named args', () => {
    const def = PREDICATE_BY_ID.get('midp')!;
    expect(def.shorthand(['M', 'A', 'B'])).toBe('M midpoint of AB');
  });

  // eqangle6 formats equal angles with vertex notation
  it('eqangle6 shorthand with six named args', () => {
    const def = PREDICATE_BY_ID.get('eqangle6')!;
    expect(def.shorthand(['A', 'B', 'C', 'D', 'E', 'F'])).toBe('∠ABC = ∠DEF');
  });

  // eqangle8 formats equal angles with directed line notation
  it('eqangle8 shorthand with eight named args', () => {
    const def = PREDICATE_BY_ID.get('eqangle8')!;
    expect(def.shorthand(['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H'])).toBe(
      '∠(AB,CD) = ∠(EF,GH)'
    );
  });

  // eqratio formats equal ratios with four segments
  it('eqratio shorthand with eight named args', () => {
    const def = PREDICATE_BY_ID.get('eqratio')!;
    expect(def.shorthand(['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H'])).toBe('AB/CD = EF/GH');
  });

  // simtri formats similar triangles with basic notation
  it('simtri shorthand with six named args', () => {
    const def = PREDICATE_BY_ID.get('simtri')!;
    expect(def.shorthand(['A', 'B', 'C', 'D', 'E', 'F'])).toBe('△ABC ~ △DEF');
  });

  // simtrir formats similar triangles with reversed orientation
  it('simtrir shorthand with six named args', () => {
    const def = PREDICATE_BY_ID.get('simtrir')!;
    expect(def.shorthand(['A', 'B', 'C', 'D', 'E', 'F'])).toBe('△ABC ~ᵣ △DEF');
  });

  // contri formats congruent triangles with standard notation
  it('contri shorthand with six named args', () => {
    const def = PREDICATE_BY_ID.get('contri')!;
    expect(def.shorthand(['A', 'B', 'C', 'D', 'E', 'F'])).toBe('△ABC ≅ △DEF');
  });

  // contrir formats congruent triangles with reversed correspondence
  it('contrir shorthand with six named args', () => {
    const def = PREDICATE_BY_ID.get('contrir')!;
    expect(def.shorthand(['A', 'B', 'C', 'D', 'E', 'F'])).toBe('△ABC ≅ᵣ △DEF');
  });

  // sameclock formats equal orientations for three points each
  it('sameclock shorthand with six named args', () => {
    const def = PREDICATE_BY_ID.get('sameclock')!;
    expect(def.shorthand(['A', 'B', 'C', 'D', 'E', 'F'])).toBe('clock(ABC) = clock(DEF)');
  });

  // obtuse_angle formats angle greater than 90 degrees
  it('obtuse_angle shorthand with three named args', () => {
    const def = PREDICATE_BY_ID.get('obtuse_angle')!;
    expect(def.shorthand(['A', 'B', 'C'])).toBe('∠ABC is obtuse');
  });

  // sameside formats two points on same side of a line
  it('sameside shorthand with six named args', () => {
    const def = PREDICATE_BY_ID.get('sameside')!;
    expect(def.shorthand(['A', 'B', 'C', 'D', 'E', 'F'])).toBe(
      'A,B same side of CD w.r.t. EF'
    );
  });

  // nsameside formats two points on opposite sides of a line
  it('nsameside shorthand with six named args', () => {
    const def = PREDICATE_BY_ID.get('nsameside')!;
    expect(def.shorthand(['A', 'B', 'C', 'D', 'E', 'F'])).toBe(
      'A,B diff. sides of CD w.r.t. EF'
    );
  });

  // rconst formats ratio equal to constant fraction
  it('rconst shorthand with five args including fraction', () => {
    const def = PREDICATE_BY_ID.get('rconst')!;
    expect(def.shorthand(['A', 'B', 'C', 'D', '1/2'])).toBe('AB/CD = 1/2');
  });

  // r2const formats squared ratio equal to constant fraction
  it('r2const shorthand with five args including fraction', () => {
    const def = PREDICATE_BY_ID.get('r2const')!;
    expect(def.shorthand(['A', 'B', 'C', 'D', '3/4'])).toBe('AB²/CD² = 3/4');
  });

  // lconst formats length equal to constant value
  it('lconst shorthand with three args including fraction', () => {
    const def = PREDICATE_BY_ID.get('lconst')!;
    expect(def.shorthand(['A', 'B', '5'])).toBe('|AB| = 5');
  });

  // l2const formats squared length equal to constant value
  it('l2const shorthand with three args including fraction', () => {
    const def = PREDICATE_BY_ID.get('l2const')!;
    expect(def.shorthand(['A', 'B', '4'])).toBe('|AB|² = 4');
  });

  // aconst formats angle equal to constant with pi notation
  it('aconst shorthand with five args including fraction', () => {
    const def = PREDICATE_BY_ID.get('aconst')!;
    expect(def.shorthand(['A', 'B', 'C', 'D', 'pi/4'])).toBe('∠(AB,CD) = pi/4 × π rad');
  });

  // coll formats multiple collinear points joined by commas
  it('coll shorthand with multiple args produces comma-joined collinear string', () => {
    const def = PREDICATE_BY_ID.get('coll')!;
    expect(def.shorthand(['A', 'B', 'C'])).toBe('A, B, C collinear');
  });

  // coll returns generic collinear text when no points given
  it('coll shorthand with empty args returns "collinear"', () => {
    const def = PREDICATE_BY_ID.get('coll')!;
    expect(def.shorthand([])).toBe('collinear');
  });

  // cyclic formats multiple concyclic points joined by commas
  it('cyclic shorthand with multiple args produces comma-joined concyclic string', () => {
    const def = PREDICATE_BY_ID.get('cyclic')!;
    expect(def.shorthand(['A', 'B', 'C', 'D'])).toBe('A, B, C, D concyclic');
  });

  // cyclic returns generic concyclic text when no points given
  it('cyclic shorthand with empty args returns "concyclic"', () => {
    const def = PREDICATE_BY_ID.get('cyclic')!;
    expect(def.shorthand([])).toBe('concyclic');
  });

  // circumcenter formats the circumcenter assignment notation
  it('circumcenter shorthand with four args', () => {
    const def = PREDICATE_BY_ID.get('circumcenter')!;
    expect(def.shorthand(['O', 'A', 'B', 'C'])).toBe('O = circumcenter(ABC)');
  });

  // p() helper fills empty or whitespace arguments with Pn placeholders
  it('shorthand uses placeholder Pn for empty/whitespace-only args', () => {
    const def = PREDICATE_BY_ID.get('cong')!;
    expect(def.shorthand(['', '', '', ''])).toBe('|P1P2| = |P3P4|');
  });
});
