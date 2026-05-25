import { el } from './dom';

export interface JgexInputHandle {
  root: HTMLElement; // the backdrop, mounted on document.body
  open(): void;
  close(): void;
  destroy(): void;
}

export function createJgexInput(
  onSubmit?: (jgex: string) => Promise<void>,
): JgexInputHandle {
  const input = el('input', {
    type: 'text',
    class: 'jgex-input',
    placeholder: 'a b = segment a b; c = midpoint c a b ? rconst c a a b 1/2',
    autocomplete: 'off',
    spellcheck: 'false',
  }) as HTMLInputElement;

  const errorMsg = el('p', { class: 'jgex-error' }) as HTMLParagraphElement;

  const cancelBtn = el('button', {
    type: 'button',
    class: 'jgex-btn jgex-btn-quiet',
  }, ['Cancel']) as HTMLButtonElement;

  const submitBtn = el('button', {
    type: 'button',
    class: 'jgex-btn jgex-btn-accent',
  }, ['Submit']) as HTMLButtonElement;

  const dialog = el('div', {
    class: 'jgex-dialog',
    role: 'dialog',
    'aria-modal': 'true',
    'aria-labelledby': 'jgex-dialog-title',
  }, [
    el('div', { class: 'jgex-title', id: 'jgex-dialog-title' }, ['Enter a JGEX line']),
    input,
    errorMsg,
    el('div', { class: 'jgex-actions' }, [cancelBtn, submitBtn]),
  ]);
  const backdrop = el('div', { class: 'jgex-backdrop' }, [dialog]);

  const close = () => backdrop.classList.remove('is-open');
  const open = () => {
    backdrop.classList.add('is-open');
    input.value = '';
    errorMsg.textContent = '';
    input.focus();
  };

  const submit = async () => {
    const value = input.value.trim();
    if (!value) return;

    if (!onSubmit) {
      close();
      return;
    }

    submitBtn.disabled = true;
    errorMsg.textContent = '';
    try {
      await onSubmit(value);
      close();
    } catch (err) {
      console.log('[JGEX submit error]', err);
      errorMsg.textContent = 'Server Error';
    } finally {
      submitBtn.disabled = false;
    }
  };

  // Enter submits, Esc closes; clicking the dim area (but not the dialog) closes.
  input.addEventListener('keydown', (e) => {
    if (e.key === 'Enter') void submit();
    else if (e.key === 'Escape') close();
  });
  backdrop.addEventListener('mousedown', (e) => {
    if (e.target === backdrop) close();
  });
  cancelBtn.addEventListener('click', close);
  submitBtn.addEventListener('click', () => void submit());

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
