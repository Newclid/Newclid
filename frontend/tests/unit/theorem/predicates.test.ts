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
