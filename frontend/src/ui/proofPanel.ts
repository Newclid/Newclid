import { AppStore } from '../store/appStore';
import type { NewclidProofSections } from '../api/types';
import { el } from './dom';

// Count text premise refs in a raw proof step string (each ends with a bracket ref like [C0], [N1], [36]).
function countTextPremises(rawStep: string): number {
  const premiseSection = rawStep.match(/^\d+\.\s*\|\s*(.+?)\s*=\(/)?.[1] ?? '';
  const premRegex = /.*?\[\w*\d+\]/g;
  let count = 0;
  while (premRegex.exec(premiseSection) !== null) count++;
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

// Strip the backend bracket-ref prefix "[C0] : " (or "[N0] : " etc.) from an assumption string.
function extractPredicate(raw: string): string {
  return raw.replace(/^\[\w+\d*\]\s*:\s*/, '').trim();
}

// Remap backend bracket refs to user-friendly 1-based labels for display only.
// [C0] → [A1]  (exercise premises, 1-based)
// [N0] → [N1]  (numerical checks, 1-based)
// [36] → [F37] (derived proof facts, 1-based)
// Raw strings passed to buildTextPremiseSigs in main.ts are never transformed here.
function remapRef(s: string): string {
  return s
    .replace(/\[C(\d+)\]/g, (_, n) => `[A${+n + 1}]`)
    .replace(/\[N(\d+)\]/g, (_, n) => `[N${+n + 1}]`)
    .replace(/\[(\d+)\]/g, (_, n) => `[F${+n + 1}]`);
}

function buildLegend(): HTMLElement {
  const legend = el('div', { class: 'proof-legend' });
  const entries: [string, string, string][] = [
    ['proof-ref-label proof-ref-premise', 'A1, A2…', 'Premises given in the exercise'],
    ['proof-ref-label proof-ref-numerical', 'N1, N2…', 'Numerical checks (computed values)'],
    ['proof-ref-label proof-ref-derived', 'F1, F2…', 'Facts derived during the proof'],
  ];
  for (const [cls, key, desc] of entries) {
    const row = el('div', { class: 'proof-legend-row' });
    row.appendChild(el('span', { class: cls }, [key]));
    row.appendChild(el('span', { class: 'proof-legend-desc' }, [desc]));
    legend.appendChild(row);
  }
  return legend;
}

function buildPremisesSection(assumptions: string[]): HTMLElement {
  const section = el('div', { class: 'proof-section' });
  section.appendChild(el('div', { class: 'proof-section-title' }, ['Premises']));
  const list = el('ol', { class: 'proof-steps-list' });
  for (let i = 0; i < assumptions.length; i++) {
    const predicate = extractPredicate(assumptions[i]);
    const item = el('li', { class: 'proof-step-item proof-labeled-item' });
    item.appendChild(el('span', { class: 'proof-ref-label proof-ref-premise' }, [`A${i + 1}`]));
    item.appendChild(document.createTextNode(predicate));
    list.appendChild(item);
  }
  section.appendChild(list);
  return section;
}

function buildNumericalChecksSection(checks: string[]): HTMLElement {
  const section = el('div', { class: 'proof-section' });
  section.appendChild(el('div', { class: 'proof-section-title' }, ['Numerical Checks']));
  const list = el('ol', { class: 'proof-steps-list' });
  for (let i = 0; i < checks.length; i++) {
    const predicate = extractPredicate(checks[i]);
    const item = el('li', { class: 'proof-step-item proof-labeled-item' });
    item.appendChild(el('span', { class: 'proof-ref-label proof-ref-numerical' }, [`N${i + 1}`]));
    item.appendChild(document.createTextNode(predicate));
    list.appendChild(item);
  }
  section.appendChild(list);
  return section;
}

// Live-updating list of fact conclusions accumulated up to the current step (inclusive).
function buildDerivedFactsSection(steps: string[], upToIdx: number): HTMLElement {
  const section = el('div', { class: 'proof-section' });
  section.appendChild(el('div', { class: 'proof-section-title' }, ['Derived Facts']));
  const list = el('ol', { class: 'proof-steps-list' });
  let count = 0;
  for (let i = 0; i <= upToIdx && i < steps.length; i++) {
    const parsed = parseProofStep(steps[i]);
    if (!parsed) continue;
    count++;
    const item = el('li', { class: 'proof-step-item proof-labeled-item' });
    item.appendChild(el('span', { class: 'proof-ref-label proof-ref-derived' }, [`F${count}`]));
    item.appendChild(document.createTextNode(remapRef(parsed.conclusion)));
    list.appendChild(item);
  }
  if (count === 0) {
    list.appendChild(el('li', { class: 'proof-step-item proof-empty-hint' }, ['Step through the proof to see derived facts.']));
  }
  section.appendChild(list);
  return section;
}

function buildSimpleSection(title: string, items: string[]): HTMLElement {
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
  const topMatch = raw.match(/^(\d+)\.\s*\|\s*(.+?)\s*=\((.+?)\)>\s*(.+)$/);
  if (!topMatch) return null;

  const premiseSection = topMatch[2];
  // Each premise ends with a bracket ref like [C0], [N1], [36].
  const premises: string[] = [];
  const premRegex = /.*?\[\w*\d+\]/g;
  let m;
  while ((m = premRegex.exec(premiseSection)) !== null) {
    const trimmed = m[0].replace(/^[,\s]+/, '').trim();
    if (trimmed) premises.push(trimmed);
  }
  // Fallback for malformed steps without bracket refs.
  if (premises.length === 0 && premiseSection.trim()) {
    premises.push(...premiseSection.split(',').map(p => p.trim()).filter(Boolean));
  }

  return {
    num: topMatch[1],
    premises,
    rule: topMatch[3].trim(),
    conclusion: topMatch[4].trim(),
  };
}

function buildProofStepItem(raw: string, activeSubStep?: number): HTMLElement {
  const parsed = parseProofStep(raw);
  if (!parsed) {
    return el('li', { class: 'proof-step-item' }, [raw]);
  }

  // 1-based step number for display (backend uses 0-indexed "000", "001", …).
  const displayNum = String(parseInt(parsed.num, 10) + 1);
  const conclusionSubStep = parsed.premises.length;
  const card = el('li', { class: 'proof-step-card' });
  card.appendChild(el('span', { class: 'proof-step-num' }, [displayNum]));

  for (let i = 0; i < parsed.premises.length; i++) {
    const cls = (activeSubStep === i)
      ? 'proof-step-premise is-active-substep'
      : 'proof-step-premise';
    card.appendChild(el('span', { class: cls }, [remapRef(parsed.premises[i])]));
  }

  card.appendChild(el('span', { class: 'proof-step-rule' }, [parsed.rule]));

  const conclusionCls = (activeSubStep === conclusionSubStep)
    ? 'proof-step-conclusion is-active-substep'
    : 'proof-step-conclusion';
  card.appendChild(el('span', { class: conclusionCls }, [remapRef(parsed.conclusion)]));
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

  // Sub-step count = one per text premise + one for the conclusion.
  const rawStepText = steps[index] ?? '';
  const premiseSubStepCount = countTextPremises(rawStepText);
  const conclusionSubStep = premiseSubStepCount;
  const rawSubStep = appStore.activeProofSubStepIndex ?? 0;
  const subStep = Math.max(0, Math.min(rawSubStep, conclusionSubStep));

  // Build the step card, highlighting the active premise/conclusion line.
  const card = buildProofStepItem(steps[index], subStep);
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
        const {
          assumptions, numerical_checks, proven_goals, unproven_goals, proof_steps,
        } = job.result.proof_sections;

        content.appendChild(buildLegend());

        if (assumptions.length > 0) {
          content.appendChild(buildPremisesSection(assumptions));
        }
        if (numerical_checks && numerical_checks.length > 0) {
          content.appendChild(buildNumericalChecksSection(numerical_checks));
        }

        const stepIndex = appStore.activeProofStepIndex;
        const atLastStep = proof_steps.length === 0
          || (stepIndex !== null && stepIndex === proof_steps.length - 1);

        if (proof_steps.length > 0) {
          content.appendChild(buildStepNavigator(job.result.proof_sections, appStore));
          if (stepIndex !== null) {
            content.appendChild(buildDerivedFactsSection(proof_steps, stepIndex));
          }
        }

        if (proven_goals.length > 0 && atLastStep) {
          content.appendChild(buildSimpleSection('Proven Goals', proven_goals.map(remapRef)));
        }
        if (unproven_goals.length > 0) {
          content.appendChild(buildSimpleSection('Unproven Goals', unproven_goals));
        }
      } else {
        if (job.result.message) {
          content.appendChild(el('p', { class: 'proof-error-msg' }, [job.result.message]));
        }
        if (job.result.proof_sections) {
          const {
            assumptions, numerical_checks, proven_goals, unproven_goals, proof_steps,
          } = job.result.proof_sections;

          content.appendChild(buildLegend());

          if (unproven_goals.length > 0) {
            content.appendChild(buildSimpleSection('Unproven Goals', unproven_goals));
          }
          if (assumptions.length > 0) {
            content.appendChild(buildPremisesSection(assumptions));
          }
          if (numerical_checks && numerical_checks.length > 0) {
            content.appendChild(buildNumericalChecksSection(numerical_checks));
          }
          const stepIndex = appStore.activeProofStepIndex;
          const atLastStep = proof_steps.length === 0
            || (stepIndex !== null && stepIndex === proof_steps.length - 1);

          if (proven_goals.length > 0 && atLastStep) {
            content.appendChild(buildSimpleSection('Proved So Far', proven_goals.map(remapRef)));
          }
          if (proof_steps.length > 0) {
            const nav = buildStepNavigator(job.result.proof_sections, appStore);
            content.appendChild(nav);
            if (stepIndex !== null) {
              content.appendChild(buildDerivedFactsSection(proof_steps, stepIndex));
            }
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
