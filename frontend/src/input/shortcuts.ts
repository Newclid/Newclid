// Global tool-switching shortcuts.

import { Scene } from '../scene/scene';
import type { ToolName } from '../geometry/types-object';
import { CONSTRUCTION_CATALOG } from '../construction/catalog';
import { getTool } from '../tools/registry';
import type { AppStore } from '../store/appStore';

const SHORTCUTS: Record<string, ToolName> = {};

// Build the shortcut map from the catalog at module init. First-defined wins;
// collisions are warned, not enforced, since shortcuts are static config.
for (const entry of Object.values(CONSTRUCTION_CATALOG)) {
  const key = entry.shortcut.toLowerCase();
  if (SHORTCUTS[key]) {
    console.warn(`Shortcut collision: '${key}' is already bound; '${entry.name}' will not be reachable by keyboard.`);
    continue;
  }
  SHORTCUTS[key] = entry.name;
}

export interface ShortcutsHandle {
  destroy(): void;
}

export function attachShortcuts(scene: Scene, appStore?: AppStore): ShortcutsHandle {
  const onKey = (e: KeyboardEvent) => {
    /**
    Skip form-control input and modified keys, matches the panZoom guard
    so the two listeners don't fight over the same event.
    **/
    const t = e.target as HTMLElement | null;
    if (t?.tagName === 'INPUT' || t?.tagName === 'TEXTAREA') return;

    /**
    Ctrl/Cmd+Z undoes the last canvas action, rewinding both the scene and the
    active tool's in-progress slots. Shift+Ctrl+Z (redo) and the proof view are
    left untouched.
    **/
    if ((e.ctrlKey || e.metaKey) && !e.altKey && !e.shiftKey && e.key.toLowerCase() === 'z') {
      if (appStore?.proofMode) return;
      scene.undo();
      scene.setSlotError(null);
      // Sync the slot hint to wherever the tool landed after rewinding.
      const activeTool = getTool(scene.tool);
      scene.setSlotHint(activeTool?.currentSlotLabel?.() ?? null);
      e.preventDefault();
      return;
    }

    // ESC cancels any in-progress construction and removes points placed so far.
    if (e.key === 'Escape') {
      if (appStore?.proofMode) return;
      const escapeTool = getTool(scene.tool);
      const slotsFilledSoFar = escapeTool?.captureState?.()?.currentSlotIndex ?? 0;
      for (let i = 0; i < slotsFilledSoFar; i++) {
        scene.undo();
      }
      scene.setSlotError(null);
      scene.setSlotHint(null);
      e.preventDefault();
      return;
    }

    if (e.metaKey || e.ctrlKey || e.altKey) return;
    if (appStore?.proofMode || appStore?.theoremManagerMode || appStore?.panelTab !== 'toolbar') return;
    const tool = SHORTCUTS[e.key.toLowerCase()];
    if (!tool) return;
    getTool(scene.tool)?.onDeactivate?.({ scene });
    scene.setTool(tool);
    e.preventDefault();
  };
  window.addEventListener('keydown', onKey);
  return {
    destroy() {
      window.removeEventListener('keydown', onKey);
    },
  };
}
