export type SketchGeom =
  | { kind: 'segment';      p1: string; p2: string }
  | { kind: 'line';         p1: string; p2: string }
  | { kind: 'circle';       center: string; through: string }
  | { kind: 'circumcircle'; p1: string; p2: string; p3: string };

function seg(p1: string, p2: string): SketchGeom { return { kind: 'segment', p1, p2 }; }
function ln(p1: string, p2: string): SketchGeom  { return { kind: 'line',    p1, p2 }; }
function circ(center: string, through: string): SketchGeom { return { kind: 'circle', center, through }; }
function circumcirc(p1: string, p2: string, p3: string): SketchGeom { return { kind: 'circumcircle', p1, p2, p3 }; }

function triangle(a: string, b: string, c: string): SketchGeom[] {
  return [seg(a, b), seg(b, c), seg(a, c)];
}

function quad(a: string, b: string, c: string, d: string): SketchGeom[] {
  return [seg(a, b), seg(b, c), seg(c, d), seg(d, a)];
}

function geomForConstruction(name: string, args: string[]): SketchGeom[] {
  switch (name) {
    case 'segment': {
      const [a, b] = args;
      return [seg(a, b)];
    }
    case 'triangle':
    case 'acute_triangle':
    case 'triangle12': {
      const [a, b, c] = args;
      return triangle(a, b, c);
    }
    case 'iso_triangle':
    case 'iso_triangle0':
    case 'iso_triangle_vertex': {
      const [v, p1, p2] = args;
      return triangle(v, p1, p2);
    }
    case 'r_triangle': {
      const [x, a, b] = args;
      return triangle(x, a, b);
    }
    case 'quadrangle':
    case 'rectangle':
    case 'isquare':
    case 'square':
    case 'parallelogram':
    case 'trapezoid':
    case 'iso_trapezoid':
    case 'r_trapezoid': {
      const [a, b, c, d] = args;
      return quad(a, b, c, d);
    }
    case 'pentagon': {
      const [a, b, c, d, e] = args;
      return [seg(a,b), seg(b,c), seg(c,d), seg(d,e), seg(e,a)];
    }
    case 'circle':
    case 'circumcenter': {
      // x a b c → circle center x through a + show triangle a,b,c
      const [x, a, b, c] = args;
      return [circ(x, a), ...triangle(a, b, c)];
    }
    case 'on_circle': {
      // _x o a → circle centered at o through a
      const [, o, a] = args;
      return [circ(o, a)];
    }
    case 'on_circum': {
      // _x a b c → circumcircle of a,b,c + triangle
      const [, a, b, c] = args;
      return [circumcirc(a, b, c), ...triangle(a, b, c)];
    }
    case 'midpoint':
    case 'between':
    case 'between_bound':
    case 'trisegment': {
      // x a b → full line through a,b
      const [, a, b] = args;
      return [ln(a, b)];
    }
    case 'on_line': {
      // _x a b → line through a,b
      const [, a, b] = args;
      return [ln(a, b)];
    }
    case 'on_pline':
    case 'on_pline0': {
      // x y a b → line a,b + line x,y (parallel)
      const [x, y, a, b] = args;
      return [ln(a, b), ln(x, y)];
    }
    case 'on_tline': {
      // x y a b → line x,y + line a,b (perpendicular)
      const [x, y, a, b] = args;
      return [ln(x, y), ln(a, b)];
    }
    case 'angle_bisector': {
      // x a b c → arms b,a and b,c + bisector line through vertex b and x
      const [x, a, b, c] = args;
      return [ln(b, a), ln(b, c), ln(b, x)];
    }
    case 'on_dia': {
      // x a b → line x,a + line x,b (right angle at x)
      const [x, a, b] = args;
      return [ln(x, a), ln(x, b)];
    }
    case 'foot': {
      // f a b c → line a,f (the altitude) + line b,c (the base)
      const [f, a, b, c] = args;
      return [ln(a, f), ln(b, c)];
    }
    case 'intersection_ll': {
      // _x a b c d → line a,b + line c,d
      const [, a, b, c, d] = args;
      return [ln(a, b), ln(c, d)];
    }
    case 'intersection_lp': {
      // x a b c m n → line a,b + line m,n
      const [, a, b, , m, n] = args;
      return [ln(a, b), ln(m, n)];
    }
    case 'intersection_pp': {
      // x a b c d e f → line b,c + line e,f + segment a,x + segment d,x
      const [x, a, b, c, d, e, f] = args;
      return [ln(b, c), ln(e, f), seg(a, x), seg(d, x)];
    }
    case 'intersection_lt': {
      // x a b c d e → line a,b + line d,e + line c,x
      const [x, a, b, , d, e] = args;
      // c is args[3]
      const c = args[3];
      return [ln(a, b), ln(d, e), ln(c, x)];
    }
    case 'intersection_tt': {
      // x a b c d e f → line b,c + line e,f + line a,x + line d,x
      const [x, a, b, c, d, e, f] = args;
      return [ln(b, c), ln(e, f), ln(a, x), ln(d, x)];
    }
    case 'intersection_lc': {
      // x a o b → line a,b + circle center o through b + segment o,b
      const [, a, o, b] = args;
      return [ln(a, b), circ(o, b), seg(o, b)];
    }
    case 'intersection_cc': {
      // x o w a → circle(o,a) + circle(w,a) + segment o,a + segment w,a
      const [, o, w, a] = args;
      return [circ(o, a), circ(w, a), seg(o, a), seg(w, a)];
    }
    case 'incenter':
    case 'excenter': {
      // d a b c → triangle a,b,c + lines from each vertex through d
      const [d, a, b, c] = args;
      return [...triangle(a, b, c), ln(a, d), ln(b, d), ln(c, d)];
    }
    case 'simtri':
    case 'simtrir': {
      // r a b c p q → triangles a,b,c and p,q,r
      const [r, a, b, c, p, q] = args;
      return [...triangle(a, b, c), ...triangle(p, q, r)];
    }
    case 'contri':
    case 'contrir': {
      // q r a b c p → triangles a,b,c and p,q,r
      const [q, r, a, b, c, p] = args;
      return [...triangle(a, b, c), ...triangle(p, q, r)];
    }
    case 'shift': {
      // x b c d → segment d,c + segment b,x
      const [x, b, , d] = args;
      const c = args[2];
      return [seg(d, c), seg(b, x)];
    }
    case 'mirror': {
      // x a b → segment b,a + segment b,x
      const [x, a, b] = args;
      return [seg(b, a), seg(b, x)];
    }
    case 'reflect': {
      // x a b c → line b,c + segment x,a
      const [x, a, b, c] = args;
      return [ln(b, c), seg(x, a)];
    }
    case 'free':
    default:
      return [];
  }
}

export function parseJgexGeometry(jgex: string): SketchGeom[] {
  let setup = jgex;
  const goalIdx = setup.indexOf('?');
  if (goalIdx !== -1) setup = setup.slice(0, goalIdx);
  const auxIdx = setup.indexOf('|');
  if (auxIdx !== -1) setup = setup.slice(0, auxIdx);

  const result: SketchGeom[] = [];

  for (const rawClause of setup.split(';')) {
    const clause = rawClause.trim();
    if (!clause) continue;

    const constructionStr = clause.includes('=') ? clause.split('=')[1] : clause;

    for (const rawConstruction of constructionStr.split(',')) {
      const words = rawConstruction.trim().split(/\s+/).filter(Boolean);
      if (words.length < 1) continue;
      const name = words[0];
      const args = words.slice(1);
      result.push(...geomForConstruction(name, args));
    }
  }

  return result;
}
