import { AppStore } from '../store/appStore';
import { Scene } from '../scene/scene';
import { el } from './dom';
import { pickNearestPoint } from '../geometry/hitTest';
import { world } from '../geometry/coords';
import { buildNameTable } from '../emit/names';
import { emitScene } from '../emit/jgex';
import type { ObjectId } from '../geometry/types-object';

interface SlotGroup {
  label: string;
  count: number;
}

interface GoalPredicate {
  id: string;
  label: string;
  shorthand: string;
  icon: string;
  slotLabels: string[];          // base labels (also the minimum set)
  slotGroups?: SlotGroup[];      // if present, renders labeled sub-sections
  variableSlots?: boolean;       // if true, user can add/remove slots beyond the base set
  hidden?: boolean;
  description?: string;
  buildJgex(jgexNames: string[]): string;
}

const GOAL_PREDICATES: GoalPredicate[] = [
  {
    id: 'perp', label: 'Perpendicular', shorthand: 'AB ⊥ CD', icon: '⊥',
    slotLabels: ['A', 'B', 'C', 'D'],
    slotGroups: [{ label: 'Line 1', count: 2 }, { label: 'Line 2', count: 2 }],
    buildJgex: (ns) => `perp ${ns.join(' ')}`,
  },
  {
    id: 'para', label: 'Parallel', shorthand: 'AB || CD', icon: '||',
    slotLabels: ['A', 'B', 'C', 'D'],
    slotGroups: [{ label: 'Line 1', count: 2 }, { label: 'Line 2', count: 2 }],
    buildJgex: (ns) => `para ${ns.join(' ')}`,
  },
  {
    id: 'cong', label: 'Equal Length', shorthand: '|AB| = |CD|', icon: '=',
    slotLabels: ['A', 'B', 'C', 'D'],
    slotGroups: [{ label: 'Segment 1', count: 2 }, { label: 'Segment 2', count: 2 }],
    buildJgex: (ns) => `cong ${ns.join(' ')}`,
  },
  {
    id: 'coll', label: 'Collinear', shorthand: 'A, B, C, … on line', icon: '—',
    slotLabels: ['A', 'B', 'C'],
    variableSlots: true,  // user can add more points beyond the minimum 3
    buildJgex: (ns) => `coll ${ns.join(' ')}`,
  },
  {
    id: 'cyclic', label: 'Concyclic', shorthand: 'A,B,C,D on circle', icon: '○',
    slotLabels: ['A', 'B', 'C', 'D'],
    buildJgex: (ns) => `cyclic ${ns.join(' ')}`,
  },
  {
    id: 'midpoint', label: 'Midpoint', shorthand: 'M midpoint of AB', icon: '–·–',
    slotLabels: ['M', 'A', 'B'],
    slotGroups: [{ label: 'Midpoint', count: 1 }, { label: 'Segment', count: 2 }],
    buildJgex: (ns) => `midp ${ns.join(' ')}`,
  },
  {
    id: 'eqangle', label: 'Equal Angles', shorthand: '∠(AB,CD) = ∠(EF,GH)', icon: '∠',
    slotLabels: ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H'],
    slotGroups: [{ label: 'Angle 1', count: 4 }, { label: 'Angle 2', count: 4 }],
    buildJgex: (ns) => `eqangle ${ns.join(' ')}`,
  },
  {
    id: 'eqratio', label: 'Equal Ratios', shorthand: 'AB/CD = EF/GH', icon: '∝',
    slotLabels: ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H'],
    slotGroups: [{ label: 'Ratio 1', count: 4 }, { label: 'Ratio 2', count: 4 }],
    buildJgex: (ns) => `eqratio ${ns.join(' ')}`,
  },
  {
    id: 'simtri', label: 'Similar Triangles', shorthand: '△ABC ~ △DEF', icon: '~△',
    slotLabels: ['A', 'B', 'C', 'D', 'E', 'F'],
    slotGroups: [{ label: 'Triangle 1', count: 3 }, { label: 'Triangle 2', count: 3 }],
    buildJgex: (ns) => `simtri ${ns.join(' ')}`,
  },
  {
    id: 'contri', label: 'Congruent Triangles', shorthand: '△ABC ≅ △DEF', icon: '≅△',
    slotLabels: ['A', 'B', 'C', 'D', 'E', 'F'],
    slotGroups: [{ label: 'Triangle 1', count: 3 }, { label: 'Triangle 2', count: 3 }],
    description: 'Vertex order matters: A↔D, B↔E, C↔F. Use when both triangles share the same cyclic orientation (both clockwise or both counter-clockwise). Valid orderings: ABC↔BCA↔CAB.',
    buildJgex: (ns) => `contri ${ns.join(' ')}`,
  },
  {
    id: 'contrir', label: 'Congruent Triangles (reflected)', shorthand: '△ABC ≅ᵣ △DEF', icon: '≅△ᵣ',
    slotLabels: ['A', 'B', 'C', 'D', 'E', 'F'],
    slotGroups: [{ label: 'Triangle 1', count: 3 }, { label: 'Triangle 2', count: 3 }],
    description: 'Vertex order matters: A↔D, B↔E, C↔F. Use when the triangles have opposite cyclic orientation — one is a mirror image of the other. Valid orderings: ABC↔ACB↔BAC↔CBA.',
    buildJgex: (ns) => `contrir ${ns.join(' ')}`,
  },
  {
    id: 'obtuse_angle', label: 'Obtuse Angle', shorthand: '∠ABC obtuse', icon: '↖↗',
    slotLabels: ['A', 'B', 'C'],
    hidden: true,
    buildJgex: (ns) => `obtuse_angle ${ns.join(' ')}`,
  },
];

export interface ProofByPointsPanelHandle {
  root: HTMLElement;
  destroy(): void;
}

export function createProofByPointsPanel(
  appStore: AppStore,
  scene?: Scene,
  onSubmit?: (jgex: string) => Promise<void>,
): ProofByPointsPanelHandle {
  const root = el('div', { class: 'proof-panel' });

  const backBtn = el('button', { class: 'proof-back-btn', type: 'button' }, ['← Back to edit']);
  backBtn.addEventListener('click', () => { resetState(); appStore.exitProofByPoints(); });
  root.appendChild(backBtn);

  const content = el('div', { class: 'proof-panel-content' });
  root.appendChild(content);

  // ---- Mutable state ----
  let selectedPredicate: GoalPredicate | null = null;
  let slotAssignments: (ObjectId | null)[] = [];
  let activeSlot = 0;
  // Extra slots added by the user for variable-length predicates (e.g. coll).
  let extraSlots = 0;
  const originalColors = new Map<ObjectId, string | undefined>();

  // Returns the full label array for the current predicate + any extra slots added.
  // For coll with 1 extra: ['A','B','C','D']; with 2 extra: ['A','B','C','D','E'].
  function getEffectiveSlotLabels(): string[] {
    if (!selectedPredicate) return [];
    const base = selectedPredicate.slotLabels;
    if (!selectedPredicate.variableSlots || extraSlots === 0) return base;
    const extra = Array.from({ length: extraSlots }, (_, i) =>
      String.fromCharCode(65 + base.length + i),  // D, E, F…
    );
    return [...base, ...extra];
  }

  // ---- Group helpers ----

  // One distinct color per slot-group so the user sees which points belong to which structure.
  const GROUP_COLORS = ['#2A4A7F', '#8B3A2A', '#2A7A3A', '#7A5A1A'];

  function getGroupForSlot(slotIndex: number): number {
    if (!selectedPredicate?.slotGroups) return 0;
    let offset = 0;
    for (let g = 0; g < selectedPredicate.slotGroups.length; g++) {
      offset += selectedPredicate.slotGroups[g].count;
      if (slotIndex < offset) return g;
    }
    return selectedPredicate.slotGroups.length - 1;
  }

  function getSlotsInSameGroup(slotIndex: number): number[] {
    if (!selectedPredicate?.slotGroups) {
      // No groups defined → treat all slots as one group (no duplicates anywhere).
      return slotAssignments.map((_, i) => i);
    }
    let offset = 0;
    for (const group of selectedPredicate.slotGroups) {
      const start = offset;
      offset += group.count;
      if (slotIndex < offset) {
        return Array.from({ length: group.count }, (_, i) => start + i);
      }
    }
    return [slotIndex];
  }

  // ---- Highlight helpers ----

  function highlightPoint(id: ObjectId, color: string): void {
    if (!scene) return;
    const obj = scene.objects.get(id);
    if (!obj || obj.kind !== 'point') return;
    if (!originalColors.has(id)) originalColors.set(id, obj.color);
    scene.setPointColor(id, color);
  }

  // After a slot change, re-evaluate a point's color: restore original if it's
  // no longer in any slot, or re-highlight with its remaining group's color.
  function updatePointHighlight(id: ObjectId): void {
    const remainingSlot = slotAssignments.findIndex((sid) => sid === id);
    if (remainingSlot === -1) {
      if (originalColors.has(id)) {
        scene?.setPointColor(id, originalColors.get(id));
        originalColors.delete(id);
      }
    } else {
      const groupIdx = getGroupForSlot(remainingSlot);
      scene?.setPointColor(id, GROUP_COLORS[groupIdx % GROUP_COLORS.length]);
    }
  }

  function clearHighlights(): void {
    if (!scene) return;
    for (const [id, color] of originalColors) scene.setPointColor(id, color);
    originalColors.clear();
  }

  function resetState(): void {
    clearHighlights();
    selectedPredicate = null;
    slotAssignments = [];
    activeSlot = 0;
    extraSlots = 0;
    appStore.setGoalPickCallback(null);
    render();
  }

  // ---- Canvas pick callback ----

  function onCanvasPick(worldX: number, worldY: number, scale: number): void {
    if (!selectedPredicate || !scene) return;
    if (activeSlot >= slotAssignments.length) return;

    const nearest = pickNearestPoint(scene.objects, world(worldX, worldY), { tolerancePx: 12, scale });
    if (!nearest) return;

    const groupIdx = getGroupForSlot(activeSlot);

    // Vacate only slots in the SAME group that already hold this point —
    // the same point is allowed across different groups (e.g. AB ∥ AC).
    for (const groupSlot of getSlotsInSameGroup(activeSlot)) {
      if (groupSlot !== activeSlot && slotAssignments[groupSlot] === nearest.id) {
        slotAssignments[groupSlot] = null;
      }
    }

    // Clear the point previously in this slot.
    const prevId = slotAssignments[activeSlot];
    if (prevId !== null && prevId !== nearest.id) {
      slotAssignments[activeSlot] = null;
      updatePointHighlight(prevId);
    }

    highlightPoint(nearest.id, GROUP_COLORS[groupIdx % GROUP_COLORS.length]);
    slotAssignments[activeSlot] = nearest.id;

    // Advance to the next unfilled slot.
    let next = activeSlot + 1;
    while (next < slotAssignments.length && slotAssignments[next] !== null) next++;
    activeSlot = next;

    render();
  }

  // ---- Slot row builder ----

  function buildSlotRow(i: number, labels: string[], nameTable: Map<ObjectId, string>): HTMLElement {
    const assignedId = slotAssignments[i];
    const isActive = i === activeSlot;
    const isFilled = assignedId !== null;

    const row = el('div', {
      class: ['goal-slot-row', isActive ? 'is-next' : '', isFilled ? 'is-filled' : ''].filter(Boolean).join(' '),
      title: isActive ? '' : 'Click to edit this point',
    });

    row.addEventListener('click', (e) => {
      if ((e.target as HTMLElement).closest('.goal-slot-clear')) return;
      activeSlot = i;
      render();
    });

    row.appendChild(el('span', { class: 'goal-slot-label' }, [labels[i]]));

    if (isFilled) {
      const obj = scene?.objects.get(assignedId);
      const displayLabel = obj?.kind === 'point' ? obj.label : assignedId;
      row.appendChild(
        el('span', { class: 'goal-slot-value' }, [`${displayLabel} (${nameTable.get(assignedId) ?? '?'})`]),
      );
      const clearBtn = el('button', { type: 'button', class: 'goal-slot-clear', title: 'Remove' }, ['×']) as HTMLButtonElement;
      clearBtn.addEventListener('click', (e) => {
        e.stopPropagation();
        slotAssignments[i] = null;
        updatePointHighlight(assignedId);
        activeSlot = i;
        render();
      });
      row.appendChild(clearBtn);
    } else {
      row.appendChild(
        el('span', { class: `goal-slot-placeholder${isActive ? ' is-next' : ''}` },
          [isActive ? '← click on canvas' : '—']),
      );
    }
    return row;
  }

  // ---- Render ----

  function render(): void {
    content.innerHTML = '';
    if (!scene) {
      content.appendChild(el('p', { class: 'proof-error-msg' }, ['Scene not available.']));
      return;
    }

    // ---- Predicate chooser grid ----
    const chooserSection = el('div', { class: 'goal-chooser-section' });
    chooserSection.appendChild(el('div', { class: 'proof-section-title' }, ['Choose what to prove:']));
    const grid = el('div', { class: 'goal-pred-grid' });
    for (const pred of GOAL_PREDICATES.filter(p => !p.hidden)) {
      const isActive = selectedPredicate?.id === pred.id;
      const btn = el('button', {
        type: 'button',
        class: `goal-pred-btn${isActive ? ' is-active' : ''}`,
        title: pred.shorthand,
      }) as HTMLButtonElement;
      btn.appendChild(el('span', { class: 'goal-pred-icon' }, [pred.icon]));
      btn.appendChild(el('span', { class: 'goal-pred-label' }, [pred.label]));
      btn.addEventListener('click', () => {
        clearHighlights();
        selectedPredicate = pred;
        slotAssignments = pred.slotLabels.map(() => null);
        activeSlot = 0;
        extraSlots = 0;
        appStore.setGoalPickCallback(onCanvasPick);
        render();
      });
      grid.appendChild(btn);
    }
    chooserSection.appendChild(grid);
    content.appendChild(chooserSection);

    if (!selectedPredicate) return;

    if ([...scene.points()].length === 0) {
      content.appendChild(el('p', { class: 'goal-hint goal-hint-warn' }, ['Go back and add points to the canvas first.']));
      return;
    }

    // ---- Slot list ----
    const labels = getEffectiveSlotLabels();
    const nameTable = buildNameTable(scene);
    const slotSection = el('div', { class: 'goal-slot-section' });
    slotSection.appendChild(el('div', { class: 'proof-section-title' }, [`Points — ${selectedPredicate.shorthand}`]));

    const slotList = el('div', { class: 'goal-slot-list' });

    if (selectedPredicate.slotGroups) {
      let offset = 0;
      for (const group of selectedPredicate.slotGroups) {
        slotList.appendChild(el('div', { class: 'goal-slot-group-label' }, [group.label]));
        const groupEl = el('div', { class: 'goal-slot-group' });
        for (let j = 0; j < group.count; j++) {
          groupEl.appendChild(buildSlotRow(offset + j, labels, nameTable));
        }
        slotList.appendChild(groupEl);
        offset += group.count;
      }
    } else {
      for (let i = 0; i < labels.length; i++) {
        slotList.appendChild(buildSlotRow(i, labels, nameTable));
      }
    }

    // +/− controls for variable-length predicates (e.g. collinear).
    if (selectedPredicate.variableSlots) {
      const varControls = el('div', { class: 'goal-var-controls' });

      const addBtn = el('button', { type: 'button', class: 'goal-var-btn' }, ['+ Add point']) as HTMLButtonElement;
      addBtn.addEventListener('click', () => {
        extraSlots++;
        slotAssignments.push(null);
        activeSlot = slotAssignments.length - 1;  // focus the new slot
        render();
      });
      varControls.appendChild(addBtn);

      // Only show "Remove" when there are extra slots (can't go below the minimum).
      if (extraSlots > 0) {
        const removeBtn = el('button', { type: 'button', class: 'goal-var-btn goal-var-btn-remove' }, ['− Remove last']) as HTMLButtonElement;
        removeBtn.addEventListener('click', () => {
          const lastIdx = slotAssignments.length - 1;
          const lastId = slotAssignments[lastIdx];
          slotAssignments.pop();
          extraSlots--;
          if (lastId !== null) updatePointHighlight(lastId);
          if (activeSlot >= slotAssignments.length) activeSlot = slotAssignments.length - 1;
          render();
        });
        varControls.appendChild(removeBtn);
      }

      slotList.appendChild(varControls);
    }

    slotSection.appendChild(slotList);

    if (selectedPredicate.description) {
      slotSection.appendChild(
        el('p', { class: 'goal-pred-description' }, [selectedPredicate.description]),
      );
    }

    if (activeSlot < labels.length) {
      slotSection.appendChild(
        el('p', { class: 'goal-hint' }, [`Click point "${labels[activeSlot]}" on the canvas`]),
      );
    }
    content.appendChild(slotSection);

    // ---- JGEX preview ----
    const goalJgex = buildGoalJgex();
    const setupJgex = emitScene(scene);
    const partialNames = slotAssignments.map((id, i) =>
      id ? (nameTable.get(id) ?? '?') : `[${labels[i]}]`,
    );
    const previewText = (setupJgex ? setupJgex + ' ' : '') +
      `? ${goalJgex ?? selectedPredicate.buildJgex(partialNames)}`;

    const previewSection = el('div', { class: 'goal-preview-section' });
    previewSection.appendChild(el('div', { class: 'proof-section-title' }, ['JGEX Preview:']));
    const previewCode = el('pre', { class: 'goal-preview-code' });
    previewCode.textContent = previewText;
    previewSection.appendChild(previewCode);
    content.appendChild(previewSection);

    // ---- Submit ----
    const errorEl = el('p', { class: 'jgex-error' });
    const submitBtn = el('button', {
      type: 'button',
      class: 'jgex-btn jgex-btn-accent goal-submit-btn',
    }, ['Submit →']) as HTMLButtonElement;
    submitBtn.disabled = goalJgex === null;

    submitBtn.addEventListener('click', async () => {
      const jgex = buildGoalJgex();
      if (!jgex || !onSubmit) return;
      const setup = emitScene(scene);
      const full = (setup ? setup + ' ' : '') + `? ${jgex}`;
      submitBtn.disabled = true;
      errorEl.textContent = '';
      clearHighlights();
      appStore.setGoalPickCallback(null);
      try {
        await onSubmit(full);
      } catch {
        errorEl.textContent = 'Server error — check connection.';
        submitBtn.disabled = false;
      }
    });

    content.appendChild(errorEl);
    content.appendChild(submitBtn);
  }

  function buildGoalJgex(): string | null {
    if (!selectedPredicate || !scene) return null;
    const nameTable = buildNameTable(scene);
    const names: string[] = [];
    for (const id of slotAssignments) {
      if (id === null) return null;
      const name = nameTable.get(id);
      if (!name) return null;
      names.push(name);
    }
    return selectedPredicate.buildJgex(names);
  }

  let wasPBPMode = false;
  const unsubscribe = appStore.subscribe(() => {
    const now = appStore.proofByPointsMode;
    if (now && !wasPBPMode) resetState();
    if (!now && wasPBPMode) clearHighlights();
    wasPBPMode = now;
  });

  render();
  return {
    root,
    destroy() { resetState(); unsubscribe(); },
  };
}
