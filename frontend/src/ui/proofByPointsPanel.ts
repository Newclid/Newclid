import { AppStore } from '../store/appStore';
import { Scene } from '../scene/scene';
import { el } from './dom';
import { pickNearestPoint } from '../geometry/hitTest';
import { world } from '../geometry/coords';
import type { ObjectId } from '../geometry/types-object';

// Describes one provable geometric relationship.
// slotLabels names the points the user must select (e.g. ['A','B','C','D'] for perp).
// buildJgex converts resolved JGEX identifiers into a goal clause.
interface GoalPredicate {
  id: string;
  label: string;
  shorthand: string;  // tooltip / preview label
  icon: string;
  slotLabels: string[];
  buildJgex(jgexNames: string[]): string;
}

const GOAL_PREDICATES: GoalPredicate[] = [
  { id: 'perp',     label: 'Perpendicular', shorthand: 'AB ⊥ CD',         icon: '⊥', slotLabels: ['A','B','C','D'],             buildJgex: (ns) => `perp ${ns.join(' ')}` },
  { id: 'para',     label: 'Parallel',      shorthand: 'AB ∥ CD',          icon: '∥', slotLabels: ['A','B','C','D'],             buildJgex: (ns) => `para ${ns.join(' ')}` },
  { id: 'cong',     label: 'Equal Length',  shorthand: '|AB| = |CD|',      icon: '≅', slotLabels: ['A','B','C','D'],             buildJgex: (ns) => `cong ${ns.join(' ')}` },
  { id: 'coll',     label: 'Collinear',     shorthand: 'A, B, C on line',  icon: '—', slotLabels: ['A','B','C'],                 buildJgex: (ns) => `coll ${ns.join(' ')}` },
  { id: 'cyclic',   label: 'Concyclic',     shorthand: 'A,B,C,D on circle',icon: '○', slotLabels: ['A','B','C','D'],             buildJgex: (ns) => `cyclic ${ns.join(' ')}` },
  { id: 'midp',     label: 'Midpoint',      shorthand: 'M midpoint of AB', icon: '·', slotLabels: ['M','A','B'],                 buildJgex: (ns) => `midp ${ns.join(' ')}` },
  { id: 'eqangle',  label: 'Equal Angles',  shorthand: '∠(AB,CD)=∠(EF,GH)',icon:'∠', slotLabels: ['A','B','C','D','E','F','G','H'], buildJgex: (ns) => `eqangle ${ns.join(' ')}` },
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
  backBtn.addEventListener('click', () => {
    resetState();
    appStore.exitProofByPoints();
  });
  root.appendChild(backBtn);

  const content = el('div', { class: 'proof-panel-content' });
  root.appendChild(content);

  // ---- Mutable state ----
  let selectedPredicate: GoalPredicate | null = null;
  // One entry per slot; null = not yet filled.
  let slotAssignments: (ObjectId | null)[] = [];
  // Index of the slot we are currently waiting the user to click for.
  let nextSlotIndex = 0;
  // Saved colors so we can restore them when the user exits or changes predicate.
  const originalColors = new Map<ObjectId, string | undefined>();

  // ---- Highlight helpers ----

  function highlightPoint(id: ObjectId): void {
    if (!scene) return;
    const obj = scene.objects.get(id);
    if (!obj || obj.kind !== 'point') return;
    if (!originalColors.has(id)) originalColors.set(id, obj.color);
    scene.setPointColor(id, '#2A4A7F');  // accent blue
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
    nextSlotIndex = 0;
    appStore.setGoalPickCallback(null);
    render();
  }

  // ---- Canvas pick callback ----
  // Called by toolDispatcher whenever the user clicks in proofByPointsMode.

  function onCanvasPick(worldX: number, worldY: number, scale: number): void {
    if (!selectedPredicate || !scene) return;
    if (nextSlotIndex >= selectedPredicate.slotLabels.length) return;

    const nearest = pickNearestPoint(scene.objects, world(worldX, worldY), { tolerancePx: 12, scale });
    if (!nearest) return;

    // If the point already occupies another slot, vacate that slot first.
    const existing = slotAssignments.indexOf(nearest.id);
    if (existing !== -1 && existing !== nextSlotIndex) slotAssignments[existing] = null;

    highlightPoint(nearest.id);
    slotAssignments[nextSlotIndex] = nearest.id;

    // Advance nextSlotIndex past any already-filled slots.
    do { nextSlotIndex++; }
    while (nextSlotIndex < slotAssignments.length && slotAssignments[nextSlotIndex] !== null);

    render();
  }

  function render(): void {
    content.innerHTML = '';
    if (!scene) {
      content.appendChild(el('p', { class: 'proof-error-msg' }, ['Scene not available.']));
      return;
    }

    // ---- Predicate chooser grid ----
    // Always visible so the user can switch their choice at any time.
    const chooserSection = el('div', { class: 'goal-chooser-section' });
    chooserSection.appendChild(
      el('div', { class: 'proof-section-title' }, ['Choose what to prove:']),
    );

    const grid = el('div', { class: 'goal-pred-grid' });
    for (const pred of GOAL_PREDICATES) {
      const isActive = selectedPredicate?.id === pred.id;
      const btn = el('button', {
        type: 'button',
        class: `goal-pred-btn${isActive ? ' is-active' : ''}`,
        title: pred.shorthand,
      }) as HTMLButtonElement;
      btn.appendChild(el('span', { class: 'goal-pred-icon' }, [pred.icon]));
      btn.appendChild(el('span', { class: 'goal-pred-label' }, [pred.label]));
      btn.addEventListener('click', () => {
        // Switching predicate resets any prior slot selections and highlights.
        clearHighlights();
        selectedPredicate = pred;
        slotAssignments = pred.slotLabels.map(() => null);
        nextSlotIndex = 0;
        appStore.setGoalPickCallback(onCanvasPick);
        render();
      });
      grid.appendChild(btn);
    }
    chooserSection.appendChild(grid);
    content.appendChild(chooserSection);

    // Slot list goes here in commit 5.
  }

  // Re-enter the mode fresh whenever the user opens this panel again.
  let wasPBPMode = false;
  const unsubscribe = appStore.subscribe(() => {
    const now = appStore.proofByPointsMode;
    if (now && !wasPBPMode) resetState();
    wasPBPMode = now;
  });

  render();
  return {
    root,
    destroy() { resetState(); unsubscribe(); },
  };
}
