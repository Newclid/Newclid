/**
 * History of every proof run this session, shown in the Proofs tab.
 * It's a thin view over appStore.jobs: re-render on every store change and
 * let the existing proof panel handle the actual detail view.
 */
import { el } from './dom';
import { AppStore } from '../store/appStore';
import { statusLabel } from './proofPanel';

export interface ProofsListHandle {
  root: HTMLElement;
  destroy(): void;
}

export function createProofsList(appStore: AppStore): ProofsListHandle {
  const root = el('div', { class: 'proofs-list' });

  const update = () => {
    // Cheap to rebuild the whole list since runs are few; revisit if that changes.
    root.innerHTML = '';
    // Newest first, so the run you just started shows up at the top.
    const jobs = [...appStore.jobs.values()].sort(
      (a, b) => b.submittedAt - a.submittedAt,
    );

    if (jobs.length === 0) {
      root.appendChild(el('p', { class: 'proofs-list-empty' }, ['No proofs yet.']));
      return;
    }

    for (const job of jobs) {
      const row = el('button', {
        type: 'button',
        class: 'proofs-list-item',
      }) as HTMLButtonElement;
      row.appendChild(el('span', { class: 'proofs-list-problem' }, [job.problem]));
      row.appendChild(
        el('span', { class: 'proof-status-badge', 'data-status': job.status }, [
          statusLabel(job.status),
        ]),
      );
      /**
       * Reuse the full-screen proof panel by making this job active and
       * flipping into proof mode, same as a fresh submission does.
       */
      row.addEventListener('click', () => {
        appStore.setActiveJob(job.jobId);
        appStore.enterProofMode();
      });
      root.appendChild(row);
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
