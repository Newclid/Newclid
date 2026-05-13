// Global tool-switching shortcuts.

import { Scene } from '../scene/scene';
import type { ToolName } from '../geometry/types-object';

const SHORTCUTS: Record<string, ToolName> = {
  v: 'select',
  p: 'point',
  c: 'circle',
};

export interface ShortcutsHandle {
  destroy(): void;
}

export function attachShortcuts(scene: Scene): ShortcutsHandle {
  const onKey = (e: KeyboardEvent) => {
    /**
    Skip form-control input and modified keys, matches the panZoom guard
    so the two listeners don't fight over the same event.
    **/
    const t = e.target as HTMLElement | null;
    if (t?.tagName === 'INPUT' || t?.tagName === 'TEXTAREA') return;
    if (e.metaKey || e.ctrlKey || e.altKey) return;
    const tool = SHORTCUTS[e.key.toLowerCase()];
    if (!tool) return;
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
