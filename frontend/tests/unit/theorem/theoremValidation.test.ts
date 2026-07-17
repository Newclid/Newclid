import { describe, it, expect } from 'vitest';
import {
  validateTheorem,
  THEOREM_NAME_RE,
  POINT_NAME_RE,
  FRACTION_RE,
} from '../../../src/types/theoremValidation';
import type { EditablePredicate } from '../../../src/types/theoremValidation';

const minPremise: EditablePredicate[] = [{ predicateId: 'cong', args: ['A', 'B', 'C', 'D'] }];
const minConclusion: EditablePredicate[] = [{ predicateId: 'para', args: ['A', 'B', 'C', 'D'] }];

describe('THEOREM_NAME_RE', () => {
  it('accepts a single letter', () => {
    expect(THEOREM_NAME_RE.test('A')).toBe(true);
  });

  it('accepts an underscore-led name', () => {
    expect(THEOREM_NAME_RE.test('_private')).toBe(true);
  });

  it('accepts alphanumeric with hyphens and underscores', () => {
    expect(THEOREM_NAME_RE.test('my-theorem_1')).toBe(true);
  });

  it('accepts an all-caps name', () => {
    expect(THEOREM_NAME_RE.test('PYTHAGOREAN')).toBe(true);
  });

  it('rejects an empty string', () => {
    expect(THEOREM_NAME_RE.test('')).toBe(false);
  });

  it('rejects a name starting with a digit', () => {
    expect(THEOREM_NAME_RE.test('1abc')).toBe(false);
  });

  it('rejects a name containing a space', () => {
    expect(THEOREM_NAME_RE.test('my theorem')).toBe(false);
  });

  it('rejects a name containing a dot', () => {
    expect(THEOREM_NAME_RE.test('my.theorem')).toBe(false);
  });
});

describe('POINT_NAME_RE', () => {
  it('accepts a single lowercase letter', () => {
    expect(POINT_NAME_RE.test('a')).toBe(true);
  });

  it('accepts a single uppercase letter', () => {
    expect(POINT_NAME_RE.test('Z')).toBe(true);
  });

  it('rejects an empty string', () => {
    expect(POINT_NAME_RE.test('')).toBe(false);
  });

  it('rejects two letters', () => {
    expect(POINT_NAME_RE.test('AB')).toBe(false);
  });

  it('rejects a digit', () => {
    expect(POINT_NAME_RE.test('1')).toBe(false);
  });

  it('rejects a space', () => {
    expect(POINT_NAME_RE.test(' ')).toBe(false);
  });
});

describe('FRACTION_RE', () => {
  it('accepts a plain integer', () => {
    expect(FRACTION_RE.test('3')).toBe(true);
  });

  it('accepts a negative integer', () => {
    expect(FRACTION_RE.test('-3')).toBe(true);
  });

  it('accepts a simple fraction', () => {
    expect(FRACTION_RE.test('1/2')).toBe(true);
  });

  it('accepts a negative numerator fraction', () => {
    expect(FRACTION_RE.test('-1/2')).toBe(true);
  });

  it('accepts a fraction with negative denominator', () => {
    expect(FRACTION_RE.test('1/-2')).toBe(true);
  });

  it('accepts a pi fraction — pi/4', () => {
    expect(FRACTION_RE.test('pi/4')).toBe(true);
  });

  it('accepts a pi fraction — 11pi/36', () => {
    expect(FRACTION_RE.test('11pi/36')).toBe(true);
  });

  it('accepts pi with no coefficient — pi/2', () => {
    expect(FRACTION_RE.test('pi/2')).toBe(true);
  });

  it('rejects a float', () => {
    expect(FRACTION_RE.test('1.5')).toBe(false);
  });

  it('rejects bare pi without a denominator', () => {
    expect(FRACTION_RE.test('pi')).toBe(false);
  });

  it('rejects an empty string', () => {
    expect(FRACTION_RE.test('')).toBe(false);
  });

  it('rejects a plain word', () => {
    expect(FRACTION_RE.test('half')).toBe(false);
  });
});

describe('validateTheorem — name validation', () => {
  it('returns null for valid name, premises, and conclusions', () => {
    expect(validateTheorem('my_theorem', minPremise, minConclusion)).toBeNull();
  });

  it('trims whitespace from name before validating', () => {
    expect(validateTheorem('  valid_name  ', minPremise, minConclusion)).toBeNull();
  });

  it('returns an error when name is empty', () => {
    const result = validateTheorem('', minPremise, minConclusion);
    expect(result).not.toBeNull();
    expect(result).toMatch(/letter or underscore/);
  });

  it('returns an error when name starts with a digit', () => {
    expect(validateTheorem('1abc', minPremise, minConclusion)).not.toBeNull();
  });

  it('returns an error when name contains a space', () => {
    expect(validateTheorem('my theorem', minPremise, minConclusion)).not.toBeNull();
  });

  it('returns an error for whitespace-only name (trims to empty)', () => {
    expect(validateTheorem('   ', minPremise, minConclusion)).not.toBeNull();
  });
});

describe('validateTheorem — structural checks', () => {
  it('returns the premises error when premises is empty', () => {
    expect(validateTheorem('ok', [], minConclusion)).toBe('Add at least one premise.');
  });

  it('returns the conclusions error when conclusions is empty', () => {
    expect(validateTheorem('ok', minPremise, [])).toBe('Add at least one conclusion.');
  });

  it('returns premises error when both are empty (premises checked first)', () => {
    expect(validateTheorem('ok', [], [])).toBe('Add at least one premise.');
  });

  it('validates name before premises (bad name + empty premises → name error)', () => {
    const result = validateTheorem('1invalid', [], []);
    expect(result).toMatch(/letter or underscore/);
  });
});

describe('validateTheorem — predicate id checks', () => {
  it('returns an error for unknown predicateId in premises', () => {
    const result = validateTheorem('ok', [{ predicateId: 'bogus', args: ['A', 'B'] }], minConclusion);
    expect(result).toMatch(/Unknown predicate: bogus/);
  });

  it('returns an error for unknown predicateId in conclusions', () => {
    const result = validateTheorem('ok', minPremise, [{ predicateId: 'bogus', args: [] }]);
    expect(result).toMatch(/Unknown predicate: bogus/);
  });

  it('error message includes the unknown id', () => {
    const result = validateTheorem('ok', [{ predicateId: 'xyz', args: [] }], minConclusion);
    expect(result).toContain('xyz');
  });
});

describe('validateTheorem — empty argument validation', () => {
  it('returns an error when a point arg is empty string', () => {
    const result = validateTheorem(
      'ok',
      [{ predicateId: 'cong', args: ['A', '', 'C', 'D'] }],
      minConclusion,
    );
    expect(result).toContain('all arguments must be filled');
    expect(result).toContain('Equal Length');
  });

  it('returns an error when a fraction arg is empty', () => {
    const result = validateTheorem(
      'ok',
      [{ predicateId: 'rconst', args: ['A', 'B', 'C', 'D', ''] }],
      minConclusion,
    );
    expect(result).not.toBeNull();
  });

  it('treats whitespace-only args as empty', () => {
    const result = validateTheorem(
      'ok',
      [{ predicateId: 'cong', args: ['A', '  ', 'C', 'D'] }],
      minConclusion,
    );
    expect(result).toContain('all arguments must be filled');
  });
});

describe('validateTheorem — point format validation', () => {
  it('accepts a single uppercase letter as a point', () => {
    expect(validateTheorem('ok', [{ predicateId: 'cong', args: ['A', 'B', 'C', 'D'] }], minConclusion))
      .toBeNull();
  });

  it('accepts a single lowercase letter as a point', () => {
    expect(validateTheorem('ok', [{ predicateId: 'cong', args: ['a', 'b', 'c', 'd'] }], minConclusion))
      .toBeNull();
  });

  it('rejects a multi-character point name', () => {
    const result = validateTheorem(
      'ok',
      [{ predicateId: 'cong', args: ['AB', 'B', 'C', 'D'] }],
      minConclusion,
    );
    expect(result).toContain('"AB"');
    expect(result).toContain('single letter');
  });

  it('rejects a digit as a point name', () => {
    const result = validateTheorem(
      'ok',
      [{ predicateId: 'cong', args: ['1', 'B', 'C', 'D'] }],
      minConclusion,
    );
    expect(result).not.toBeNull();
  });

  it('error message includes the predicate label for point errors', () => {
    const result = validateTheorem(
      'ok',
      [{ predicateId: 'cong', args: ['AB', 'B', 'C', 'D'] }],
      minConclusion,
    );
    expect(result).toContain('Equal Length');
  });

  it('labels premise errors with Premise', () => {
    const result = validateTheorem(
      'ok',
      [{ predicateId: 'cong', args: ['AB', 'B', 'C', 'D'] }],
      minConclusion,
    );
    expect(result).toMatch(/^Premise/);
  });

  it('labels conclusion errors with Conclusion', () => {
    const result = validateTheorem(
      'ok',
      minPremise,
      [{ predicateId: 'cong', args: ['AB', 'B', 'C', 'D'] }],
    );
    expect(result).toMatch(/^Conclusion/);
  });
});

describe('validateTheorem — fraction format validation', () => {
  it('accepts an integer as a fraction constant', () => {
    expect(validateTheorem(
      'ok',
      [{ predicateId: 'rconst', args: ['A', 'B', 'C', 'D', '3'] }],
      minConclusion,
    )).toBeNull();
  });

  it('accepts a ratio fraction', () => {
    expect(validateTheorem(
      'ok',
      [{ predicateId: 'rconst', args: ['A', 'B', 'C', 'D', '1/2'] }],
      minConclusion,
    )).toBeNull();
  });

  it('accepts a pi fraction for aconst', () => {
    expect(validateTheorem(
      'ok',
      [{ predicateId: 'aconst', args: ['A', 'B', 'C', 'D', 'pi/4'] }],
      minConclusion,
    )).toBeNull();
  });

  it('rejects a float as a fraction constant', () => {
    const result = validateTheorem(
      'ok',
      [{ predicateId: 'rconst', args: ['A', 'B', 'C', 'D', '1.5'] }],
      minConclusion,
    );
    expect(result).toContain('1.5');
    expect(result).toContain('integer or fraction');
  });

  it('rejects a bare word as a fraction constant', () => {
    const result = validateTheorem(
      'ok',
      [{ predicateId: 'lconst', args: ['A', 'B', 'half'] }],
      minConclusion,
    );
    expect(result).not.toBeNull();
  });

  it('error message includes the predicate label for fraction errors', () => {
    const result = validateTheorem(
      'ok',
      [{ predicateId: 'lconst', args: ['A', 'B', '1.5'] }],
      minConclusion,
    );
    expect(result).toContain('Distance = Const');
  });
});

describe('validateTheorem — variable args default to point type', () => {
  it('extra args beyond argTypes length are validated as points when valid', () => {
    expect(validateTheorem(
      'ok',
      [{ predicateId: 'coll', args: ['A', 'B', 'C', 'D', 'E'] }],
      minConclusion,
    )).toBeNull();
  });

  it('extra args beyond argTypes length reject multi-char values as point names', () => {
    const result = validateTheorem(
      'ok',
      [{ predicateId: 'coll', args: ['A', 'B', 'C', 'D', 'XY'] }],
      minConclusion,
    );
    expect(result).not.toBeNull();
    expect(result).toContain('"XY"');
  });
});

describe('validateTheorem — first error wins', () => {
  it('only the first invalid predicate in premises is reported', () => {
    const result = validateTheorem(
      'ok',
      [
        { predicateId: 'bad1', args: [] },
        { predicateId: 'bad2', args: [] },
      ],
      minConclusion,
    );
    expect(result).toContain('bad1');
    expect(result).not.toContain('bad2');
  });

  it('premise errors are reported before conclusion errors', () => {
    const result = validateTheorem(
      'ok',
      [{ predicateId: 'bogus_p', args: [] }],
      [{ predicateId: 'bogus_c', args: [] }],
    );
    expect(result).toContain('bogus_p');
    expect(result).not.toContain('bogus_c');
  });
});
