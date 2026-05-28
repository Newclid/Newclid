/**
 * The "Create proof" dialog. It's the single entry point for starting a proof,
 * branching to one of two ways to define a problem. We reuse the JGEX modal's
 * backdrop/dialog classes so it reads as the same kind of popup.
 */
import { el } from './dom';

export interface ProofChoiceHandle {
  root: HTMLElement;
  open(): void;
  close(): void;
  destroy(): void;
}

/**
 * onJgex is called when the user picks the JGEX route; the caller decides what
 * that opens (today it's the JGEX text input). onPoints is called for the
 * "by points" route (today it opens the placeholder proof-by-points plane).
 */
export function createProofChoice(opts: {
  onJgex: () => void;
  onPoints: () => void;
}): ProofChoiceHandle {
  const jgexOpt = el('button', {
    type: 'button',
    class: 'jgex-btn jgex-btn-accent proof-choice-btn',
  }, ['Proof with JGEX']) as HTMLButtonElement;

  const pointsOpt = el('button', {
    type: 'button',
    class: 'jgex-btn jgex-btn-quiet proof-choice-btn',
  }, ['Proof by points']) as HTMLButtonElement;

  const dialog = el('div', {
    class: 'jgex-dialog',
    role: 'dialog',
    'aria-modal': 'true',
    'aria-labelledby': 'proof-choice-title',
  }, [
    el('div', { class: 'jgex-title', id: 'proof-choice-title' }, ['Create a proof']),
    el('div', { class: 'proof-choice-options' }, [jgexOpt, pointsOpt]),
  ]);
  const backdrop = el('div', { class: 'jgex-backdrop' }, [dialog]);

  const close = () => backdrop.classList.remove('is-open');
  const open = () => backdrop.classList.add('is-open');

  jgexOpt.addEventListener('click', () => {
    close();
    opts.onJgex();
  });
  // Dismiss the dialog first, then hand off to the caller's "by points" route.
  pointsOpt.addEventListener('click', () => {
    close();
    opts.onPoints();
  });
  // Click outside the dialog to dismiss.
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
