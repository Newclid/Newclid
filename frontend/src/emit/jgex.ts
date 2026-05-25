import type { Scene } from '../scene/scene';
import type { JgexBlock, JgexEmit } from '../construction/catalog-types';
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
 * Walk the scene in insertion order, emit one JGEX clause per JgexBlock,
 * and join them with "; ".
 *
 * Free points (plain PointObjects not produced by any construction) are the
 * "given" points — they appear as inputs to the first construction that
 * references them and need no explicit declaration in JGEX.
 *
 * The result is the "setup" half of a JGEX problem string.  The caller
 * (sendToBackend.ts) appends " ? <goal>" when needed.
 */
export function emitScene(scene: Scene): string {
  const nameTable = buildNameTable(scene);
  const clauses: string[] = [];

  for (const obj of scene.objects.values()) {
    if (obj.kind !== 'construction') continue;

    const entry = CONSTRUCTION_CATALOG[obj.name];
    if (!entry?.jgex?.length) continue;

    // Resolve every bound slot to its JGEX name.
    // ConstructionObject.bindings is Record<string, ObjectId> — all IDs.
    // Scalar slots (JgexEmit.scalars) would be numeric literals; if the
    // binding value isn't in the nameTable we fall back to the raw value
    // string so scalar-holding constructions still emit correctly once
    // ConstructionObject is extended to carry scalars.
    const resolved: Record<string, string> = {};
    for (const [slot, id] of Object.entries(obj.bindings)) {
      resolved[slot] = nameTable.get(id) ?? String(id);
    }

    for (const block of entry.jgex) {
      clauses.push(emitBlock(block, resolved));
    }
  }

  return clauses.join('; ');
}
