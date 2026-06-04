import { AppStore } from '../store/appStore';
import type { NewclidProofSections } from '../api/types';
import { el } from './dom';

// Count the number of canvas-visible construction premise sub-steps in a raw proof step string.
function countConstructionSubSteps(rawStep: string, constructionSigs: string[]): number {
  const premiseSection = rawStep.match(/^\d+\.\s*\|\s*(.+?)\s*=\(/)?.[1] ?? '';
  const regex = /\[C(\d+)\]/g;
  let m;
  let count = 0;
  while ((m = regex.exec(premiseSection)) !== null) {
    const cIdx = parseInt(m[1], 10);
    if (cIdx >= 0 && cIdx < constructionSigs.length && constructionSigs[cIdx]) count++;
  }
  return count;
}

export interface ProofPanelHandle {
  root: HTMLElement;
  destroy(): void;
}

export function statusLabel(status: string): string {
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

interface ParsedProofStep {
  num: string;
  premises: string[];
  rule: string;
  conclusion: string;
}

function parseProofStep(raw: string): ParsedProofStep | null {
  const match = raw.match(/^(\d+)\.\s*\|\s*(.+?)\s*=\((.+?)\)>\s*(.+)$/);
  if (!match) return null;
  return {
    num: match[1],
    premises: match[2].split(',').map((p) => p.trim()),
    rule: match[3].trim(),
    conclusion: match[4].trim(),
  };
}

function buildProofStepItem(raw: string): HTMLElement {
  const parsed = parseProofStep(raw);
  if (!parsed) {
    return el('li', { class: 'proof-step-item' }, [raw]);
  }

  const card = el('li', { class: 'proof-step-card' });
  card.appendChild(el('span', { class: 'proof-step-num' }, [parsed.num]));
  for (const premise of parsed.premises) {
    card.appendChild(el('span', { class: 'proof-step-premise' }, [premise]));
  }
  card.appendChild(el('span', { class: 'proof-step-rule' }, [parsed.rule]));
  card.appendChild(el('span', { class: 'proof-step-conclusion' }, [parsed.conclusion]));
  return card;
}

function buildStepNavigator(sections: NewclidProofSections, appStore: AppStore): HTMLElement {
  const steps = sections.proof_steps;
  const total = steps.length;
  const rawIndex = appStore.activeProofStepIndex ?? 0;
  const index = Math.max(0, Math.min(rawIndex, total - 1));

  const section = el('div', { class: 'proof-section' });
  section.appendChild(el('div', { class: 'proof-section-title' }, ['Proof Steps']));

  // Outer step navigation.
  const nav = el('div', { class: 'proof-step-nav' });
  const prevBtn = el('button', { class: 'proof-step-nav-btn', type: 'button' }, ['← Prev']) as HTMLButtonElement;
  prevBtn.disabled = index === 0;
  prevBtn.addEventListener('click', () => appStore.setActiveProofStep(index - 1));
  const counter = el('span', { class: 'proof-step-counter' }, [`Step ${index + 1} of ${total}`]);
  const nextBtn = el('button', { class: 'proof-step-nav-btn', type: 'button' }, ['Next →']) as HTMLButtonElement;
  nextBtn.disabled = index === total - 1;
  nextBtn.addEventListener('click', () => appStore.setActiveProofStep(index + 1));
  nav.appendChild(prevBtn);
  nav.appendChild(counter);
  nav.appendChild(nextBtn);
  section.appendChild(nav);

  // Compute sub-steps for the current step.
  const constructionSigs = sections.construction_signatures ?? [];
  const rawStepText = steps[index] ?? '';
  const premiseIndices = sections.step_premise_indices?.[index] ?? [];
  const constructionSubStepCount = countConstructionSubSteps(rawStepText, constructionSigs);
  const premiseSubStepCount = constructionSubStepCount + premiseIndices.length;
  const conclusionSubStep = premiseSubStepCount;
  const rawSubStep = appStore.activeProofSubStepIndex ?? 0;
  const subStep = Math.max(0, Math.min(rawSubStep, conclusionSubStep));

  // Build the step card and color its left border based on sub-step type.
  const card = buildProofStepItem(steps[index]);
  card.classList.add('is-active');
  card.classList.add(subStep < premiseSubStepCount ? 'is-substep-premise' : 'is-substep-conclusion');

  // Sub-step navigation row (only shown when there are premise sub-steps to navigate).
  if (premiseSubStepCount > 0) {
    const subNav = el('div', { class: 'proof-substep-nav' });

    const prevSubBtn = el('button', { class: 'proof-substep-nav-btn', type: 'button' }, ['← Prev']) as HTMLButtonElement;
    prevSubBtn.disabled = subStep === 0;
    prevSubBtn.addEventListener('click', () => appStore.setActiveProofSubStep(subStep - 1));

    const subLabel = subStep < premiseSubStepCount
      ? `Premise ${subStep + 1} of ${premiseSubStepCount}`
      : 'Conclusion';
    const subCounter = el('span', { class: 'proof-substep-counter' }, [subLabel]);

    const nextSubBtn = el('button', { class: 'proof-substep-nav-btn', type: 'button' }, ['Next →']) as HTMLButtonElement;
    nextSubBtn.disabled = subStep === conclusionSubStep;
    nextSubBtn.addEventListener('click', () => appStore.setActiveProofSubStep(subStep + 1));

    subNav.appendChild(prevSubBtn);
    subNav.appendChild(subCounter);
    subNav.appendChild(nextSubBtn);
    card.appendChild(subNav);
  }

  section.appendChild(card);
  return section;
}

function buildStepNavigatorFromSections(sections: NewclidProofSections, appStore: AppStore): HTMLElement | null {
  if (sections.proof_steps.length === 0) return null;
  return buildStepNavigator(sections, appStore);
}

export function createProofPanel(appStore: AppStore): ProofPanelHandle {
  const root = el('div', { class: 'proof-panel' });

  const backBtn = el('button', { class: 'proof-back-btn', type: 'button' }, ['← Back to edit']);
  backBtn.addEventListener('click', () => appStore.exitProofMode());
  root.appendChild(backBtn);

  const content = el('div', { class: 'proof-panel-content' });
  root.appendChild(content);

  const update = () => {
    content.innerHTML = '';

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
    content.appendChild(statusRow);

    if (job.result) {
      if (job.result.status === 'succeeded' && job.result.proof_sections) {
        const { assumptions, proven_goals, unproven_goals, proof_steps } =
          job.result.proof_sections;
        if (assumptions.length > 0) {
          content.appendChild(buildSection('Assumptions', assumptions));
        }
        if (proven_goals.length > 0) {
          content.appendChild(buildSection('Proven Goals', proven_goals));
        }
        if (unproven_goals.length > 0) {
          content.appendChild(buildSection('Unproven Goals', unproven_goals));
        }
        if (proof_steps.length > 0) {
          const nav = buildStepNavigatorFromSections(job.result.proof_sections, appStore);
          if (nav) content.appendChild(nav);
        }
      } else {
        if (job.result.message) {
          content.appendChild(el('p', { class: 'proof-error-msg' }, [job.result.message]));
        }
        if (job.result.proof_sections) {
          const { assumptions, proven_goals, unproven_goals, proof_steps } =
            job.result.proof_sections;
          if (unproven_goals.length > 0) {
            content.appendChild(buildSection('Unproven Goals', unproven_goals));
          }
          if (assumptions.length > 0) {
            content.appendChild(buildSection('Assumptions', assumptions));
          }
          if (proven_goals.length > 0) {
            content.appendChild(buildSection('Proved So Far', proven_goals));
          }
          if (proof_steps.length > 0) {
            const nav = buildStepNavigatorFromSections(job.result.proof_sections, appStore);
            if (nav) content.appendChild(nav);
          }
        }
        if (job.result.stderr) {
          const pre = el('pre', { class: 'proof-stderr' });
          pre.textContent = job.result.stderr;
          content.appendChild(pre);
        }
      }
    } else if (job.error) {
      content.appendChild(el('p', { class: 'proof-error-msg' }, [job.error]));
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
