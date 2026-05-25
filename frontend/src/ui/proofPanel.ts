import { AppStore } from '../store/appStore';
import { el } from './dom';

export interface ProofPanelHandle {
  root: HTMLElement;
  destroy(): void;
}

function statusLabel(status: string): string {
  switch (status) {
    case 'queued': return 'Queued…';
    case 'running': return 'Running…';
    case 'succeeded': return 'Proved';
    case 'failed': return 'Failed';
    case 'timed_out': return 'Timed out';
    case 'cancelled': return 'Cancelled';
    default: return status;
  }
}

function buildSection(title: string, items: string[]): HTMLElement {
  const section = el('div', { class: 'proof-section' });
  section.appendChild(el('div', { class: 'proof-section-title' }, [title]));
  const list = el('ol', { class: 'proof-steps-list' });
  for (const item of items) {
    list.appendChild(el('li', { class: 'proof-step-item' }, [item]));
  }
  section.appendChild(list);
  return section;
}

export function createProofPanel(appStore: AppStore): ProofPanelHandle {
  const root = el('div', { class: 'proof-panel' });

  const update = () => {
    root.innerHTML = '';

    const { activeJobId } = appStore;
    if (!activeJobId) return;

    const job = appStore.jobs.get(activeJobId);
    if (!job) return;

    const isInProgress = job.status === 'queued' || job.status === 'running';

    const statusRow = el('div', { class: 'proof-status-row' });
    if (isInProgress) {
      statusRow.appendChild(el('span', { class: 'proof-spinner' }));
    }
    statusRow.appendChild(
      el('span', { class: 'proof-status-badge', 'data-status': job.status }, [
        statusLabel(job.status),
      ]),
    );
    root.appendChild(statusRow);

    if (job.result) {
      if (job.result.status === 'succeeded' && job.result.proof_sections) {
        const { assumptions, proven_goals, unproven_goals, proof_steps } =
          job.result.proof_sections;
        if (assumptions.length > 0) {
          root.appendChild(buildSection('Assumptions', assumptions));
        }
        if (proven_goals.length > 0) {
          root.appendChild(buildSection('Proven Goals', proven_goals));
        }
        if (unproven_goals.length > 0) {
          root.appendChild(buildSection('Unproven Goals', unproven_goals));
        }
        if (proof_steps.length > 0) {
          root.appendChild(buildSection('Proof Steps', proof_steps));
        }
      } else if (job.result.message) {
        root.appendChild(el('p', { class: 'proof-error-msg' }, [job.result.message]));
      }
    } else if (job.error) {
      root.appendChild(el('p', { class: 'proof-error-msg' }, [job.error]));
    }
  };

  update();
  const unsubscribe = appStore.subscribe(update);

  return {
    root,
    destroy() {
      unsubscribe();
    },
  };
}
