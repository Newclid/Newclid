// Maps a JGEX construction name to the arg-index pairs that form visible segments.
// Indices reference the args as they appear in the construction string (after the name).
const JGEX_SEGMENT_ARGS: Record<string, [number, number][]> = {
  segment:          [[0, 1]],
  between:          [[0, 1], [1, 2]],
  triangle:         [[0, 1], [1, 2], [0, 2]],
  r_triangle:       [[0, 1], [1, 2], [0, 2]],
  acute_triangle:   [[0, 1], [1, 2], [0, 2]],
  iso_triangle:     [[0, 1], [1, 2], [0, 2]],
  eq_triangle:      [[0, 1], [1, 2], [0, 2]],
  quadrangle:       [[0, 1], [1, 2], [2, 3], [3, 0]],
  parallelogram:    [[0, 1], [1, 2], [2, 3], [3, 0]],
  rectangle:        [[0, 1], [1, 2], [2, 3], [3, 0]],
  isquare:          [[0, 1], [1, 2], [2, 3], [3, 0]],
  square:           [[0, 1], [1, 2], [2, 3], [3, 0]],
  trapezoid:        [[0, 1], [1, 2], [2, 3], [3, 0]],
  iso_trapezoid:    [[0, 1], [1, 2], [2, 3], [3, 0]],
  r_trapezoid:      [[0, 1], [1, 2], [2, 3], [3, 0]],
  midpoint:         [[1, 2]],         // m a b  → edge a–b
  on_line:          [[1, 2]],         // d a b  → edge a–b
  on_pline:         [[2, 3]],         // d a b c → edge b–c
  on_tline:         [[2, 3]],         // d a b c → edge b–c
  foot:             [[1, 2]],         // f A B C → edge A–B (shows where foot lands)
  mirror:           [[1, 2]],         // m a b  → edge a–b
  intersection_ll:  [[1, 2], [3, 4]], // e a b c d → lines ab and cd
};

// Parse the setup half of a JGEX problem string into segment pairs (point name pairs).
export function parseJgexSegments(jgex: string): [string, string][] {
  // Strip goal and auxiliary clauses — we only care about the setup.
  let setup = jgex;
  const goalIdx = setup.indexOf('?');
  if (goalIdx !== -1) setup = setup.slice(0, goalIdx);
  const auxIdx = setup.indexOf('|');
  if (auxIdx !== -1) setup = setup.slice(0, auxIdx);

  const segments: [string, string][] = [];

  for (const rawClause of setup.split(';')) {
    const clause = rawClause.trim();
    if (!clause) continue;

    // Strip "points = " prefix if present.
    const constructionStr = clause.includes('=') ? clause.split('=')[1] : clause;

    // A clause can have comma-joined constructions (intersection combos).
    for (const rawConstruction of constructionStr.split(',')) {
      const words = rawConstruction.trim().split(/\s+/).filter(Boolean);
      if (words.length < 2) continue;

      const name = words[0];
      const args = words.slice(1);
      const edgeRules = JGEX_SEGMENT_ARGS[name];
      if (!edgeRules) continue;

      for (const [i, j] of edgeRules) {
        const a = args[i], b = args[j];
        if (a && b && a !== b) segments.push([a, b]);
      }
    }
  }

  return segments;
}
