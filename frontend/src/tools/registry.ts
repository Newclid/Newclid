import type { Tool } from './tool';
import { ConstructionTool } from './construction-tool';
import { CONSTRUCTION_CATALOG } from '../construction/catalog';

// Cache so the same ConstructionTool instance is reused across tool switches;
// onDeactivate already resets transient state.
const constructionToolCache = new Map<string, Tool>();

/**
Look up a tool by name. Every tool — including select, point and circle — is a
catalog entry driven by ConstructionTool. Returns undefined for unknown names.
**/
export function getTool(name: string): Tool | undefined {
  let t = constructionToolCache.get(name);
  if (!t) {
    const entry = CONSTRUCTION_CATALOG[name];
    if (!entry) return undefined;
    t = new ConstructionTool(entry);
    constructionToolCache.set(name, t);
  }
  return t;
}
