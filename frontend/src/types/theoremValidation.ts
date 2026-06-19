import { PREDICATE_BY_ID } from './theorem';

export interface EditablePredicate {
  predicateId: string;
  args: string[];
}

export const THEOREM_NAME_RE = /^[A-Za-z_][A-Za-z0-9_-]*$/;
export const POINT_NAME_RE = /^[A-Za-z]$/;
// Accepts plain rationals (1/2, 3) and angle constants as fractions of π (pi/4, 11pi/36).
export const FRACTION_RE = /^-?[0-9]+(\/-?[0-9]+)?$|^-?[0-9]*pi\/-?[0-9]+$/;

export function validateTheorem(
  name: string,
  premises: EditablePredicate[],
  conclusions: EditablePredicate[],
): string | null {
  if (!THEOREM_NAME_RE.test(name.trim())) {
    return 'Name must start with a letter or underscore and contain only letters, digits, underscores, or hyphens (no spaces).';
  }
  if (premises.length === 0) return 'Add at least one premise.';
  if (conclusions.length === 0) return 'Add at least one conclusion.';

  const sections: [string, EditablePredicate[]][] = [
    ['Premise', premises],
    ['Conclusion', conclusions],
  ];
  for (const [sectionLabel, list] of sections) {
    for (const ep of list) {
      const def = PREDICATE_BY_ID.get(ep.predicateId);
      if (!def) return `Unknown predicate: ${ep.predicateId}`;
      for (let i = 0; i < ep.args.length; i++) {
        const val = ep.args[i].trim();
        const type = i < def.argTypes.length ? def.argTypes[i] : 'point';
        if (!val) return `${sectionLabel} "${def.label}": all arguments must be filled.`;
        if (type === 'point' && !POINT_NAME_RE.test(val)) {
          return `${sectionLabel} "${def.label}": point "${val}" must be a single letter (A–Z or a–z).`;
        }
        if (type === 'fraction' && !FRACTION_RE.test(val)) {
          return `${sectionLabel} "${def.label}": constant "${val}" must be an integer or fraction like 1/2.`;
        }
      }
    }
  }
  return null;
}
