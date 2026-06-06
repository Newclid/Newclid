export type ArgType = 'point' | 'fraction';

export interface ArgSpec {
  label: string;
  type: ArgType;
}

export interface PredicateDef {
  id: string;
  jgexName: string;
  label: string;
  shorthand: string;
  icon: string;
  minArgs: number;
  argLabels: string[];
  argTypes: ArgType[];
  variableArgs?: boolean;
  groups?: { label: string; count: number }[];
}

export interface TheoremPredicate {
  predicateId: string;
  args: string[];
}

export interface CustomTheorem {
  id: string;
  name: string;
  description: string;
  premises: TheoremPredicate[];
  conclusions: TheoremPredicate[];
  createdAt: number;
}

export const PREDICATE_DEFINITIONS: PredicateDef[] = [
  // --- Fixed arity: points only ---
  {
    id: 'cong', jgexName: 'cong',
    label: 'Equal Length', shorthand: '|AB| = |CD|', icon: '=',
    minArgs: 4, argLabels: ['A', 'B', 'C', 'D'],
    argTypes: ['point', 'point', 'point', 'point'],
    groups: [{ label: 'Segment 1', count: 2 }, { label: 'Segment 2', count: 2 }],
  },
  {
    id: 'para', jgexName: 'para',
    label: 'Parallel', shorthand: 'AB ∥ CD', icon: '∥',
    minArgs: 4, argLabels: ['A', 'B', 'C', 'D'],
    argTypes: ['point', 'point', 'point', 'point'],
    groups: [{ label: 'Line 1', count: 2 }, { label: 'Line 2', count: 2 }],
  },
  {
    id: 'perp', jgexName: 'perp',
    label: 'Perpendicular', shorthand: 'AB ⊥ CD', icon: '⊥',
    minArgs: 4, argLabels: ['A', 'B', 'C', 'D'],
    argTypes: ['point', 'point', 'point', 'point'],
    groups: [{ label: 'Line 1', count: 2 }, { label: 'Line 2', count: 2 }],
  },
  {
    id: 'midp', jgexName: 'midp',
    label: 'Midpoint', shorthand: 'M midpoint of AB', icon: '⊕',
    minArgs: 3, argLabels: ['M', 'A', 'B'],
    argTypes: ['point', 'point', 'point'],
    groups: [{ label: 'Midpoint', count: 1 }, { label: 'Segment', count: 2 }],
  },
  {
    id: 'eqangle6', jgexName: 'eqangle',
    label: 'Equal Angles', shorthand: '∠ABC = ∠DEF', icon: '∠',
    minArgs: 6, argLabels: ['A', 'B', 'C', 'D', 'E', 'F'],
    argTypes: ['point', 'point', 'point', 'point', 'point', 'point'],
    groups: [{ label: 'Angle 1', count: 3 }, { label: 'Angle 2', count: 3 }],
  },
  {
    id: 'eqangle8', jgexName: 'eqangle',
    label: 'Equal Angles (line)', shorthand: '∠(AB,CD) = ∠(EF,GH)', icon: '∠∠',
    minArgs: 8, argLabels: ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H'],
    argTypes: ['point', 'point', 'point', 'point', 'point', 'point', 'point', 'point'],
    groups: [{ label: 'Angle 1', count: 4 }, { label: 'Angle 2', count: 4 }],
  },
  {
    id: 'eqratio', jgexName: 'eqratio',
    label: 'Equal Ratios', shorthand: 'AB/CD = EF/GH', icon: '∝',
    minArgs: 8, argLabels: ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H'],
    argTypes: ['point', 'point', 'point', 'point', 'point', 'point', 'point', 'point'],
    groups: [{ label: 'Ratio 1', count: 4 }, { label: 'Ratio 2', count: 4 }],
  },
  {
    id: 'simtri', jgexName: 'simtri',
    label: 'Similar Triangles', shorthand: '△ABC ~ △DEF', icon: '~△',
    minArgs: 6, argLabels: ['A', 'B', 'C', 'D', 'E', 'F'],
    argTypes: ['point', 'point', 'point', 'point', 'point', 'point'],
    groups: [{ label: 'Triangle 1', count: 3 }, { label: 'Triangle 2', count: 3 }],
  },
  {
    id: 'simtrir', jgexName: 'simtrir',
    label: 'Similar Tri. (rev)', shorthand: '△ABC ~ᵣ △DEF', icon: '~ᵣ',
    minArgs: 6, argLabels: ['A', 'B', 'C', 'D', 'E', 'F'],
    argTypes: ['point', 'point', 'point', 'point', 'point', 'point'],
    groups: [{ label: 'Triangle 1', count: 3 }, { label: 'Triangle 2', count: 3 }],
  },
  {
    id: 'contri', jgexName: 'contri',
    label: 'Congruent Triangles', shorthand: '△ABC ≅ △DEF', icon: '≅△',
    minArgs: 6, argLabels: ['A', 'B', 'C', 'D', 'E', 'F'],
    argTypes: ['point', 'point', 'point', 'point', 'point', 'point'],
    groups: [{ label: 'Triangle 1', count: 3 }, { label: 'Triangle 2', count: 3 }],
  },
  {
    id: 'contrir', jgexName: 'contrir',
    label: 'Congruent Tri. (rev)', shorthand: '△ABC ≅ᵣ △DEF', icon: '≅ᵣ',
    minArgs: 6, argLabels: ['A', 'B', 'C', 'D', 'E', 'F'],
    argTypes: ['point', 'point', 'point', 'point', 'point', 'point'],
    groups: [{ label: 'Triangle 1', count: 3 }, { label: 'Triangle 2', count: 3 }],
  },
  {
    id: 'sameclock', jgexName: 'sameclock',
    label: 'Same Orientation', shorthand: 'clock(ABC) = clock(DEF)', icon: '↻',
    minArgs: 6, argLabels: ['A', 'B', 'C', 'D', 'E', 'F'],
    argTypes: ['point', 'point', 'point', 'point', 'point', 'point'],
    groups: [{ label: 'Triangle 1', count: 3 }, { label: 'Triangle 2', count: 3 }],
  },
  {
    id: 'obtuse_angle', jgexName: 'obtuse_angle',
    label: 'Obtuse Angle', shorthand: '∠ABC is obtuse', icon: '∢',
    minArgs: 3, argLabels: ['A', 'B', 'C'],
    argTypes: ['point', 'point', 'point'],
  },
  {
    id: 'sameside', jgexName: 'sameside',
    label: 'Same Side', shorthand: 'A,B same side of CD w.r.t. EF', icon: '||',
    minArgs: 6, argLabels: ['A', 'B', 'C', 'D', 'E', 'F'],
    argTypes: ['point', 'point', 'point', 'point', 'point', 'point'],
  },
  {
    id: 'nsameside', jgexName: 'nsameside',
    label: 'Different Side', shorthand: 'A,B diff. sides of CD', icon: '|≠|',
    minArgs: 6, argLabels: ['A', 'B', 'C', 'D', 'E', 'F'],
    argTypes: ['point', 'point', 'point', 'point', 'point', 'point'],
  },
  // --- Fixed arity: points + fraction constant ---
  {
    id: 'rconst', jgexName: 'rconst',
    label: 'Ratio Dist = Const', shorthand: 'AB/CD = k', icon: 'r=k',
    minArgs: 5, argLabels: ['A', 'B', 'C', 'D', 'k'],
    argTypes: ['point', 'point', 'point', 'point', 'fraction'],
    groups: [{ label: 'Ratio', count: 4 }, { label: 'Constant', count: 1 }],
  },
  {
    id: 'r2const', jgexName: 'r2const',
    label: 'Ratio² Dist = Const', shorthand: 'AB²/CD² = k', icon: 'r²=k',
    minArgs: 5, argLabels: ['A', 'B', 'C', 'D', 'k'],
    argTypes: ['point', 'point', 'point', 'point', 'fraction'],
    groups: [{ label: 'Ratio', count: 4 }, { label: 'Constant', count: 1 }],
  },
  {
    id: 'lconst', jgexName: 'lconst',
    label: 'Distance = Const', shorthand: '|AB| = k', icon: 'd=k',
    minArgs: 3, argLabels: ['A', 'B', 'k'],
    argTypes: ['point', 'point', 'fraction'],
    groups: [{ label: 'Segment', count: 2 }, { label: 'Constant', count: 1 }],
  },
  {
    id: 'l2const', jgexName: 'l2const',
    label: 'Distance² = Const', shorthand: '|AB|² = k', icon: 'd²=k',
    minArgs: 3, argLabels: ['A', 'B', 'k'],
    argTypes: ['point', 'point', 'fraction'],
    groups: [{ label: 'Segment', count: 2 }, { label: 'Constant', count: 1 }],
  },
  {
    id: 'aconst', jgexName: 'aconst',
    label: 'Line Angle = Const', shorthand: '∠(AB,CD) = k', icon: '∠=k',
    minArgs: 5, argLabels: ['A', 'B', 'C', 'D', 'k'],
    argTypes: ['point', 'point', 'point', 'point', 'fraction'],
    groups: [{ label: 'Angle', count: 4 }, { label: 'Constant', count: 1 }],
  },
  // --- Variable-length (points only) ---
  {
    id: 'coll', jgexName: 'coll',
    label: 'Collinear', shorthand: 'A, B, C, … on line', icon: '—',
    minArgs: 3, argLabels: ['A', 'B', 'C'],
    argTypes: ['point', 'point', 'point'],
    variableArgs: true,
  },
  {
    id: 'cyclic', jgexName: 'cyclic',
    label: 'Concyclic', shorthand: 'A, B, C, D, … on circle', icon: '○',
    minArgs: 4, argLabels: ['A', 'B', 'C', 'D'],
    argTypes: ['point', 'point', 'point', 'point'],
    variableArgs: true,
  },
  {
    id: 'circumcenter', jgexName: 'circumcenter',
    label: 'Circumcenter', shorthand: 'O = circumcenter(△ABC…)', icon: '⊙',
    minArgs: 4, argLabels: ['O', 'A', 'B', 'C'],
    argTypes: ['point', 'point', 'point', 'point'],
    variableArgs: true,
    groups: [{ label: 'Center', count: 1 }, { label: 'Triangle', count: 3 }],
  },
];

export const PREDICATE_BY_ID = new Map(PREDICATE_DEFINITIONS.map((p) => [p.id, p]));

export function predicateToJgex(pred: TheoremPredicate): string {
  const def = PREDICATE_BY_ID.get(pred.predicateId);
  if (!def) throw new Error(`Unknown predicate: ${pred.predicateId}`);
  return `${def.jgexName} ${pred.args.join(' ')}`;
}

export function extraArgLabel(argIdx: number): string {
  return argIdx < 26 ? String.fromCharCode(65 + argIdx) : `P${argIdx}`;
}
