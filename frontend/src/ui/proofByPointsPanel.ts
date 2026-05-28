import { AppStore } from '../store/appStore';
import { el } from './dom';

export interface ProofByPointsPanelHandle {
  root: HTMLElement;
  destroy(): void;
}

/**
 * Placeholder plane reached from "Create proof" > "Proof by points".
 * Blank for now; the point-picking / proving-methods UI lands here later.
 */
export function createProofByPointsPanel(appStore: AppStore): ProofByPointsPanelHandle {
  const root = el('div', { class: 'proof-panel' });

  const backBtn = el('button', { class: 'proof-back-btn', type: 'button' }, ['← Back to edit']);
  backBtn.addEventListener('click', () => appStore.exitProofByPoints());
  root.appendChild(backBtn);

  // No subscription yet: the panel is static. Keep destroy() for a consistent handle shape.
  return { root, destroy() {} };
}
