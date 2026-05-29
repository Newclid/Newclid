import { AppStore } from '../store/appStore';
import { Scene } from '../scene/scene';
import { el } from './dom';

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

  function resetState(): void {
    selectedPredicate = null;
    appStore.setGoalPickCallback(null);
    render();
  }

  // Placeholder — filled out in commit 4 when slot logic is added.
  function onCanvasPick(_worldX: number, _worldY: number, _scale: number): void { /* next commit */ }

  function render(): void {
    content.innerHTML = '';
    if (!scene) {
      content.appendChild(el('p', { class: 'proof-error-msg' }, ['Scene not available.']));
      return;
    }
    // Predicate grid goes here in commit 3.
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
