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

// Tracks the currently-open dropdown so we can close it when another opens.
let openDropdown: { close(): void } | null = null;

function openRemoveDialog(name: string, onConfirm: () => void): void {
  const backdrop = el('div', { class: 'jgex-backdrop' });
  const dialog = el('div', {
    class: 'jgex-dialog remove-confirm-dialog',
    role: 'dialog',
    'aria-modal': 'true',
  });

  const close = () => backdrop.remove();

  const footer = el('div', { class: 'jgex-actions' });
  const cancelBtn = el('button', { type: 'button', class: 'jgex-btn jgex-btn-quiet' }, ['Cancel']) as HTMLButtonElement;
  const confirmBtn = el('button', { type: 'button', class: 'jgex-btn jgex-btn-danger' }, ['Remove']) as HTMLButtonElement;

  cancelBtn.addEventListener('click', close);
  confirmBtn.addEventListener('click', () => { close(); onConfirm(); });
  backdrop.addEventListener('mousedown', (e) => { if (e.target === backdrop) close(); });

  footer.appendChild(cancelBtn);
  footer.appendChild(confirmBtn);

  dialog.appendChild(el('div', { class: 'jgex-title' }, [`Remove "${name}"?`]));
  dialog.appendChild(el('p', { class: 'remove-confirm-body' }, ['This cannot be undone.']));
  dialog.appendChild(footer);
  backdrop.appendChild(dialog);
  document.body.appendChild(backdrop);

  requestAnimationFrame(() => backdrop.classList.add('is-open'));
  confirmBtn.focus();
}

function closeOpenDropdown(): void {
  if (openDropdown) {
    openDropdown.close();
    openDropdown = null;
  }
}

export function createProofsList(appStore: AppStore): ProofsListHandle {
  const root = el('div', { class: 'proofs-list' });

  // Collapse status badge text to a coloured circle when the list is narrow.
  const resizeObserver = new ResizeObserver(([entry]) => {
    root.classList.toggle('is-narrow', entry.contentRect.width < 175);
  });
  resizeObserver.observe(root);

  const update = () => {
    root.innerHTML = '';
    // Newest first for display; oldest-first index used for auto-label numbers.
    const jobsNewestFirst = [...appStore.jobs.values()].sort(
      (a, b) => b.submittedAt - a.submittedAt,
    );

    if (jobsNewestFirst.length === 0) {
      root.appendChild(el('p', { class: 'proofs-list-empty' }, ['No proofs yet.']));
      return;
    }

    // Stable "Solution N" numbering: oldest job = 1, next = 2, …
    const labelIndex = new Map(
      [...appStore.jobs.values()]
        .sort((a, b) => a.submittedAt - b.submittedAt)
        .map((job, i) => [job.jobId, i + 1]),
    );

    for (const job of jobsNewestFirst) {
      const displayName = job.name || `Solution ${labelIndex.get(job.jobId)}`;

      // ── outer row (position:relative for the dropdown) ──────────────────
      const row = el('div', { class: 'proofs-list-item' });

      // ── main clickable area ──────────────────────────────────────────────
      const main = el('div', {
        class: 'proofs-list-item-main',
        role: 'button',
        tabindex: '0',
      });

      const badge = el(
        'span',
        { class: 'proof-status-badge', 'data-status': job.status },
        [statusLabel(job.status)],
      );

      const nameSpan = el('span', { class: 'proofs-list-name' }, [displayName]);

      main.appendChild(badge);
      main.appendChild(nameSpan);

      const activateRow = () => {
        appStore.setActiveJob(job.jobId);
        appStore.enterProofMode();
      };
      main.addEventListener('click', activateRow);
      main.addEventListener('keydown', (e: KeyboardEvent) => {
        if (e.key === 'Enter' || e.key === ' ') {
          e.preventDefault();
          activateRow();
        }
      });

      // ── 3-dot menu button ────────────────────────────────────────────────
      const menuBtn = el('button', {
        type: 'button',
        class: 'proofs-list-menu-btn',
        'aria-label': 'Solution options',
        title: 'Options',
      }, ['⋮']) as HTMLButtonElement;

      // ── dropdown ─────────────────────────────────────────────────────────
      const dropdown = el('div', { class: 'proofs-list-dropdown' });

      const renameBtn = el('button', { type: 'button', class: 'proofs-list-dropdown-item' }, ['Rename']);
      const removeBtn = el('button', { type: 'button', class: 'proofs-list-dropdown-item proofs-list-dropdown-item-danger' }, ['Remove']);
      dropdown.appendChild(renameBtn);
      dropdown.appendChild(removeBtn);

      let dropdownOpen = false;

      const openMenu = () => {
        closeOpenDropdown();
        dropdownOpen = true;
        dropdown.classList.add('is-open');
        openDropdown = { close: closeMenu };
      };

      const closeMenu = () => {
        dropdownOpen = false;
        dropdown.classList.remove('is-open');
        if (openDropdown?.close === closeMenu) openDropdown = null;
      };

      menuBtn.addEventListener('click', (e) => {
        e.stopPropagation();
        if (dropdownOpen) closeMenu();
        else openMenu();
      });

      // ── rename ────────────────────────────────────────────────────────────
      renameBtn.addEventListener('click', (e) => {
        e.stopPropagation();
        closeMenu();

        const input = el('input', {
          type: 'text',
          class: 'proofs-list-rename-input',
          value: displayName,
        }) as HTMLInputElement;

        main.replaceChild(input, nameSpan);
        input.focus();
        input.select();

        let saved = false;

        const save = () => {
          if (saved) return;
          saved = true;
          const trimmed = input.value.trim();
          appStore.renameJob(job.jobId, trimmed);
        };

        const cancel = () => {
          if (saved) return;
          saved = true;
          main.replaceChild(nameSpan, input);
        };

        input.addEventListener('keydown', (ke: KeyboardEvent) => {
          // Stop bubbling so the parent role="button" keydown doesn't fire activateRow.
          ke.stopPropagation();
          if (ke.key === 'Enter') { ke.preventDefault(); save(); }
          if (ke.key === 'Escape') { ke.preventDefault(); cancel(); }
        });
        input.addEventListener('blur', save);
      });

      // ── remove ────────────────────────────────────────────────────────────
      removeBtn.addEventListener('click', (e) => {
        e.stopPropagation();
        closeMenu();
        openRemoveDialog(displayName, () => appStore.removeJob(job.jobId));
      });

      row.appendChild(main);
      row.appendChild(menuBtn);
      row.appendChild(dropdown);
      root.appendChild(row);
    }
  };

  // Close open dropdown on any outside click.
  const onDocMouseDown = (e: MouseEvent) => {
    if (openDropdown && !root.contains(e.target as Node)) {
      closeOpenDropdown();
    }
  };
  document.addEventListener('mousedown', onDocMouseDown);

  update();
  const unsubscribe = appStore.subscribe(update);

  return {
    root,
    destroy() {
      unsubscribe();
      resizeObserver.disconnect();
      document.removeEventListener('mousedown', onDocMouseDown);
    },
  };
}
