import { el } from './dom';

export interface JobStatusBanner {
  root: HTMLElement;
  showSuccess(message: string): void;
  showError(message: string): void;
  clear(): void;
}

export function createJobStatusBanner(): JobStatusBanner {
  const text = el('span', { class: 'job-banner-text' });

  const closeBtn = el('button', {
    type: 'button',
    class: 'job-banner-close',
    'aria-label': 'Dismiss',
  }, ['×']) as HTMLButtonElement;

  const root = el('div', { class: 'job-status-banner' }, [text, closeBtn]);

  const clear = () => {
    root.classList.remove('is-visible');
    root.removeAttribute('data-variant');
    text.textContent = '';
  };

  const show = (variant: 'success' | 'error', message: string) => {
    text.textContent = message;
    root.setAttribute('data-variant', variant);
    root.classList.add('is-visible');
  };

  closeBtn.addEventListener('click', clear);

  return {
    root,
    showSuccess: (msg) => show('success', msg),
    showError: (msg) => show('error', msg),
    clear,
  };
}
