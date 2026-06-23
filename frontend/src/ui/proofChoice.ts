/**
 * The "Solve a new problem" dialog. It's the single entry point for starting a
 * proof, branching to one of two ways to define a problem.
 */
import { el } from './dom';

export interface ProofChoiceHandle {
  root: HTMLElement;
  open(): void;
  close(): void;
  destroy(): void;
}

export function createProofChoice(opts: {
  onJgex: () => void;
  onPoints: () => void;
}): ProofChoiceHandle {
  const visualOpt = el('button', {
    type: 'button',
    class: 'proof-choice-btn proof-choice-btn-primary',
  }, [
    el('span', { class: 'proof-choice-btn-header' }, [
      el('span', { class: 'proof-choice-btn-title' }, ['Define Goal Visually']),
      el('span', { class: 'proof-choice-badge proof-choice-badge-recommended' }, ['Recommended']),
    ]),
    el('span', { class: 'proof-choice-btn-subtitle' }, [
      'Define the goal interactively using the constructed figure.',
    ]),
  ]) as HTMLButtonElement;

  const syntaxOpt = el('button', {
    type: 'button',
    class: 'proof-choice-btn proof-choice-btn-secondary',
  }, [
    el('span', { class: 'proof-choice-btn-header' }, [
      el('span', { class: 'proof-choice-btn-title' }, ['Write in JGEX Syntax']),
      el('span', { class: 'proof-choice-badge' }, ['Advanced']),
    ]),
    el('span', { class: 'proof-choice-btn-subtitle' }, [
      'Define the full problem using JGEX commands.',
    ]),
  ]) as HTMLButtonElement;

  const cancelBtn = el('button', {
    type: 'button',
    class: 'jgex-btn jgex-btn-quiet proof-choice-cancel',
  }, ['Cancel']) as HTMLButtonElement;

  const dialog = el('div', {
    class: 'jgex-dialog proof-choice-dialog',
    role: 'dialog',
    'aria-modal': 'true',
    'aria-labelledby': 'proof-choice-title',
  }, [
    el('div', { class: 'jgex-title', id: 'proof-choice-title' }, ['Solve New Problem']),
    el('div', { class: 'proof-choice-options' }, [visualOpt, syntaxOpt]),
    el('div', { class: 'proof-choice-footer' }, [cancelBtn]),
  ]);
  const backdrop = el('div', { class: 'jgex-backdrop' }, [dialog]);

  const close = () => backdrop.classList.remove('is-open');
  const open = () => backdrop.classList.add('is-open');

  // "Build Visually" → interactive points/drawing route (onPoints)
  visualOpt.addEventListener('click', () => {
    close();
    opts.onPoints();
  });
  // "Write in JGEX Syntax" → JGEX text input route (onJgex)
  syntaxOpt.addEventListener('click', () => {
    close();
    opts.onJgex();
  });
  cancelBtn.addEventListener('click', () => close());
  backdrop.addEventListener('mousedown', (e) => {
    if (e.target === backdrop) close();
  });

  document.body.appendChild(backdrop);

  return {
    root: backdrop,
    open,
    close,
    destroy() {
      backdrop.remove();
    },
  };
}
