import type { Scene } from '../scene/scene';
import type { ObjectId } from '../geometry/types-object';
import type { JgexBlock, JgexEmit, JgexEmit as JgexEmitType } from '../construction/catalog-types';
import { CONSTRUCTION_CATALOG } from '../construction/catalog';
import { buildNameTable } from './names';

/**
 * Render one JGEX clause, e.g. "midpoint c a b".
 * `resolved` maps slot names to their JGEX point names (already looked up
 * through the name table) or literal scalar strings.
 */
function emitClause(emit: JgexEmit, resolved: Record<string, string>): string {
  const args = emit.signature.map(slot => resolved[slot] ?? slot);
  return `${emit.def} ${args.join(' ')}`;
}

/**
 * Render one JgexBlock:
 *   - JgexEmit  → single clause "def a b c"
 *   - intersect → comma-joined clauses "def1 p a b, def2 p c d"
 */
function emitBlock(block: JgexBlock, resolved: Record<string, string>): string {
  if ('combine' in block) {
    return block.clauses.map(c => emitClause(c, resolved)).join(', ');
  }
  return emitClause(block, resolved);
}

/**
 * Return the space-joined names of all points produced by a block, e.g. "c"
 * or "a b c" for multi-output constructions.  Returns null if no produces.
 */
function producedNames(block: JgexBlock, resolved: Record<string, string>): string | null {
  const emits: JgexEmitType[] = 'combine' in block ? block.clauses : [block];
  const seen = new Set<string>();
  const names: string[] = [];
  for (const emit of emits) {
    for (const slot of emit.produces) {
      if (!seen.has(slot)) {
        seen.add(slot);
        const name = resolved[slot];
        if (name) names.push(name);
      }
    }
  }
  return names.length > 0 ? names.join(' ') : null;
}

/**
 * Walk the scene in insertion order and emit a complete JGEX setup string.
 *
 * Free points (PointObjects not produced by any construction) are emitted as
 * "name = free name" before constructions that reference them.
 *
 * Each construction clause is emitted as "produced = def produced inputs…"
 * so the backend can identify the output point.
 *
 * The result is the "setup" half of a JGEX problem string.  The caller
 * appends " ? <goal>" when needed.
 */
export function emitScene(scene: Scene): string {
  const nameTable = buildNameTable(scene);

  // Collect the set of point IDs produced by any construction so we can
  // skip emitting them as free points.
  const producedIds = new Set<ObjectId>();
  for (const obj of scene.objects.values()) {
    if (obj.kind !== 'construction') continue;
    const entry = CONSTRUCTION_CATALOG[obj.name];
    if (!entry?.jgex?.length) continue;
    for (const block of entry.jgex) {
      const emits: JgexEmitType[] = 'combine' in block ? block.clauses : [block];
      for (const emit of emits) {
        for (const slot of emit.produces) {
          const id = obj.bindings[slot];
          if (id) producedIds.add(id);
        }
      }
    }
  }

  const clauses: string[] = [];

  for (const obj of scene.objects.values()) {
    if (obj.kind === 'point') {
      // Free point — not produced by any construction.
      if (!producedIds.has(obj.id)) {
        const name = nameTable.get(obj.id);
        if (name) clauses.push(`${name} = free ${name}`);
      }
      continue;
    }

    if (obj.kind !== 'construction') continue;

    const entry = CONSTRUCTION_CATALOG[obj.name];
    if (!entry?.jgex?.length) continue;

    // Resolve every bound slot to its JGEX name.
    const resolved: Record<string, string> = {};
    for (const [slot, id] of Object.entries(obj.bindings)) {
      resolved[slot] = nameTable.get(id) ?? String(id);
    }

    for (const block of entry.jgex) {
      // Skip a block whose output point was never created, e.g. when two
      // circles are tangent or a line is tangent to a circle.
      const emits: JgexEmitType[] = 'combine' in block ? block.clauses : [block];
      const producedSlots = emits.flatMap(e => e.produces);
      if (producedSlots.length > 0 && producedSlots.some(slot => !obj.bindings[slot])) continue;

      const body = emitBlock(block, resolved);
      const lhs = producedNames(block, resolved);
      clauses.push(lhs ? `${lhs} = ${body}` : body);
    }
  }

  return clauses.join('; ');
}
