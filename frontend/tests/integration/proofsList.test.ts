import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest';
import { createProofsList } from '../../src/ui/proofsList';
import { AppStore } from '../../src/store/appStore';
import { makeSucceededResult } from '../fixtures/proofResult';

describe('createProofsList + AppStore', () => {
  let appStore: AppStore;
  let destroyList: (() => void) | null = null;

  beforeEach(() => {
    // Increment by 1000ms per call so jobs always get distinct submittedAt values.
    let mockNow = 0;
    vi.spyOn(Date, 'now').mockImplementation(() => (mockNow += 1000));

    appStore = new AppStore();

    vi.stubGlobal('ResizeObserver', class {
      observe() {}
      unobserve() {}
      disconnect() {}
    });
  });

  afterEach(() => {
    destroyList?.();
    destroyList = null;
    document.body.innerHTML = '';
    vi.restoreAllMocks();
    vi.unstubAllGlobals();
  });

  // ─────────────────────────────────────────────────────────────
  // Empty state
  // ─────────────────────────────────────────────────────────────

  describe('empty state', () => {
    // no jobs yet → show a clear empty-state message
    it('renders "No solutions yet." when the jobs map is empty', () => {
      const { root, destroy } = createProofsList(appStore);
      destroyList = destroy;
      expect(root.querySelector('.proofs-list-empty')?.textContent).toBe('No solutions yet.');
    });
  });

  // ─────────────────────────────────────────────────────────────
  // Job list rendering
  // ─────────────────────────────────────────────────────────────

  describe('job list rendering', () => {
    // each job gets exactly one row
    it('shows one row per job in appStore.jobs', () => {
      appStore.addJob('j1', 'problem1');
      appStore.addJob('j2', 'problem2');
      const { root, destroy } = createProofsList(appStore);
      destroyList = destroy;
      expect(root.querySelectorAll('.proofs-list-item').length).toBe(2);
    });

    // newest job should appear at the top of the list
    it('newest job appears first (sorted by submittedAt descending)', () => {
      appStore.addJob('j1', 'problem1'); // submittedAt = 1000
      appStore.addJob('j2', 'problem2'); // submittedAt = 2000
      const { root, destroy } = createProofsList(appStore);
      destroyList = destroy;
      const names = Array.from(root.querySelectorAll('.proofs-list-name')).map(n => n.textContent);
      expect(names[0]).toBe('Solution 2'); // j2 is newest → displayed first
      expect(names[1]).toBe('Solution 1');
    });

    // auto-label numbering: oldest = 1, second oldest = 2, …
    it('auto-labels oldest job "Solution 1" and second-oldest "Solution 2"', () => {
      appStore.addJob('j1', 'problem1');
      appStore.addJob('j2', 'problem2');
      const { root, destroy } = createProofsList(appStore);
      destroyList = destroy;
      const names = new Set(
        Array.from(root.querySelectorAll('.proofs-list-name')).map(n => n.textContent),
      );
      expect(names).toContain('Solution 1');
      expect(names).toContain('Solution 2');
    });

    // user-assigned name overrides the auto-label
    it('shows the user-assigned name instead of the auto-label when job.name is set', () => {
      appStore.addJob('j1', 'problem');
      appStore.renameJob('j1', 'My Proof');
      const { root, destroy } = createProofsList(appStore);
      destroyList = destroy;
      const name = root.querySelector('.proofs-list-name')?.textContent;
      expect(name).toBe('My Proof');
    });

    // status badge reflects current job lifecycle state
    it('status badge reflects job.status ("Proved" for succeeded)', () => {
      appStore.addJob('j1', 'problem');
      appStore.updateJob('j1', { result: makeSucceededResult(), status: 'succeeded' });
      const { root, destroy } = createProofsList(appStore);
      destroyList = destroy;
      const badge = root.querySelector('.proof-status-badge');
      expect(badge?.textContent).toBe('Proved');
      expect(badge?.getAttribute('data-status')).toBe('succeeded');
    });

    // list reacts to new jobs added after it was created
    it('adds a new row reactively when a second job is added', () => {
      appStore.addJob('j1', 'problem1');
      const { root, destroy } = createProofsList(appStore);
      destroyList = destroy;
      expect(root.querySelectorAll('.proofs-list-item').length).toBe(1);

      appStore.addJob('j2', 'problem2');
      expect(root.querySelectorAll('.proofs-list-item').length).toBe(2);
    });
  });

  // ─────────────────────────────────────────────────────────────
  // Selecting a proof from history
  // ─────────────────────────────────────────────────────────────

  describe('selecting a proof from history', () => {
    // clicking the main area makes the job active and shows the proof panel
    it('clicking a row main area calls appStore.setActiveJob and enterProofMode', () => {
      appStore.addJob('j1', 'problem');
      const { root, destroy } = createProofsList(appStore);
      destroyList = destroy;
      const setActiveJobSpy = vi.spyOn(appStore, 'setActiveJob');
      const enterProofModeSpy = vi.spyOn(appStore, 'enterProofMode');

      root.querySelector<HTMLElement>('.proofs-list-item-main')!.click();

      expect(setActiveJobSpy).toHaveBeenCalledWith('j1');
      expect(enterProofModeSpy).toHaveBeenCalled();
    });

    // Enter key on the row is keyboard-equivalent to a click
    it('pressing Enter on a focused row also activates it', () => {
      appStore.addJob('j1', 'problem');
      const { root, destroy } = createProofsList(appStore);
      destroyList = destroy;
      const spy = vi.spyOn(appStore, 'setActiveJob');

      const main = root.querySelector<HTMLElement>('.proofs-list-item-main')!;
      main.dispatchEvent(new KeyboardEvent('keydown', { key: 'Enter', bubbles: true }));

      expect(spy).toHaveBeenCalledWith('j1');
    });
  });

  // ─────────────────────────────────────────────────────────────
  // Rename flow
  // ─────────────────────────────────────────────────────────────

  describe('rename flow', () => {
    function openRename(root: Element) {
      root.querySelector<HTMLButtonElement>('.proofs-list-menu-btn')!.click();
      // Rename is the first dropdown item
      root.querySelectorAll<HTMLButtonElement>('.proofs-list-dropdown-item')[0].click();
    }

    // opening the rename flow swaps the name span for an input
    it('clicking ⋮ → Rename replaces the name span with an inline text input', () => {
      appStore.addJob('j1', 'problem');
      const { root, destroy } = createProofsList(appStore);
      destroyList = destroy;
      openRename(root);
      expect(root.querySelector('.proofs-list-rename-input')).toBeTruthy();
    });

    // Enter commits the new name via appStore
    it('pressing Enter saves the new name via appStore.renameJob', () => {
      appStore.addJob('j1', 'problem');
      const { root, destroy } = createProofsList(appStore);
      destroyList = destroy;
      const spy = vi.spyOn(appStore, 'renameJob');
      openRename(root);

      const input = root.querySelector<HTMLInputElement>('.proofs-list-rename-input')!;
      input.value = 'My Proof';
      input.dispatchEvent(new KeyboardEvent('keydown', { key: 'Enter', bubbles: true }));

      expect(spy).toHaveBeenCalledWith('j1', 'My Proof');
    });

    // Escape discards the edit and restores the original name span
    it('pressing Escape cancels without saving', () => {
      appStore.addJob('j1', 'problem');
      const { root, destroy } = createProofsList(appStore);
      destroyList = destroy;
      const spy = vi.spyOn(appStore, 'renameJob');
      openRename(root);

      const input = root.querySelector<HTMLInputElement>('.proofs-list-rename-input')!;
      input.value = 'Discarded Name';
      input.dispatchEvent(new KeyboardEvent('keydown', { key: 'Escape', bubbles: true }));

      expect(spy).not.toHaveBeenCalled();
      expect(root.querySelector('.proofs-list-name')?.textContent).toBe('Solution 1');
    });

    // blur (e.g. clicking elsewhere) also commits the name
    it('blurring the input saves the trimmed value', () => {
      appStore.addJob('j1', 'problem');
      const { root, destroy } = createProofsList(appStore);
      destroyList = destroy;
      const spy = vi.spyOn(appStore, 'renameJob');
      openRename(root);

      const input = root.querySelector<HTMLInputElement>('.proofs-list-rename-input')!;
      input.value = '  Trimmed  ';
      input.dispatchEvent(new Event('blur'));

      expect(spy).toHaveBeenCalledWith('j1', 'Trimmed');
    });
  });

  // ─────────────────────────────────────────────────────────────
  // Remove flow
  // ─────────────────────────────────────────────────────────────

  describe('remove flow', () => {
    function openRemoveDialog(root: Element) {
      root.querySelector<HTMLButtonElement>('.proofs-list-menu-btn')!.click();
      // Remove is the second dropdown item (danger style)
      root.querySelectorAll<HTMLButtonElement>('.proofs-list-dropdown-item')[1].click();
    }

    // the dialog title should name the job so the user knows what they're removing
    it('clicking ⋮ → Remove opens the confirm dialog with the job display name', () => {
      appStore.addJob('j1', 'problem');
      const { root, destroy } = createProofsList(appStore);
      destroyList = destroy;
      openRemoveDialog(root);

      const dialog = document.querySelector('.remove-confirm-dialog');
      expect(dialog).toBeTruthy();
      expect(dialog?.querySelector('.jgex-title')?.textContent).toContain('Solution 1');
    });

    // Cancel is a safe exit — nothing should be removed
    it('clicking Cancel closes the dialog without calling removeJob', () => {
      appStore.addJob('j1', 'problem');
      const { root, destroy } = createProofsList(appStore);
      destroyList = destroy;
      const spy = vi.spyOn(appStore, 'removeJob');
      openRemoveDialog(root);

      document.querySelector<HTMLButtonElement>('.jgex-btn-quiet')!.click();

      expect(spy).not.toHaveBeenCalled();
      expect(document.querySelector('.remove-confirm-dialog')).toBeNull();
    });

    // the danger Remove button confirms the deletion
    it('clicking Remove in the dialog calls appStore.removeJob', () => {
      appStore.addJob('j1', 'problem');
      const { root, destroy } = createProofsList(appStore);
      destroyList = destroy;
      const spy = vi.spyOn(appStore, 'removeJob');
      openRemoveDialog(root);

      document.querySelector<HTMLButtonElement>('.jgex-btn-danger')!.click();

      expect(spy).toHaveBeenCalledWith('j1');
    });

    // after removal the list re-renders and the row disappears
    it('removed job row disappears from the list', () => {
      appStore.addJob('j1', 'problem');
      appStore.addJob('j2', 'problem2');
      const { root, destroy } = createProofsList(appStore);
      destroyList = destroy;
      expect(root.querySelectorAll('.proofs-list-item').length).toBe(2);

      openRemoveDialog(root);
      document.querySelector<HTMLButtonElement>('.jgex-btn-danger')!.click();

      expect(root.querySelectorAll('.proofs-list-item').length).toBe(1);
    });
  });

  // ─────────────────────────────────────────────────────────────
  // Dropdown close behaviour
  // ─────────────────────────────────────────────────────────────

  describe('dropdown close behaviour', () => {
    // opening a second dropdown should close the first one
    it('clicking ⋮ on a second job closes the first job\'s open dropdown', () => {
      appStore.addJob('j1', 'problem1'); // submittedAt = 1000
      appStore.addJob('j2', 'problem2'); // submittedAt = 2000 → rendered first (newest)
      const { root, destroy } = createProofsList(appStore);
      destroyList = destroy;

      const menuBtns = root.querySelectorAll<HTMLButtonElement>('.proofs-list-menu-btn');
      const dropdowns = root.querySelectorAll<HTMLElement>('.proofs-list-dropdown');
      // Row 0 = j2 (newest), Row 1 = j1

      menuBtns[1].click(); // open j1's dropdown
      expect(dropdowns[1].classList.contains('is-open')).toBe(true);

      menuBtns[0].click(); // open j2's dropdown → should close j1's
      expect(dropdowns[1].classList.contains('is-open')).toBe(false);
      expect(dropdowns[0].classList.contains('is-open')).toBe(true);
    });
  });

  // ─────────────────────────────────────────────────────────────
  // destroy()
  // ─────────────────────────────────────────────────────────────

  describe('destroy()', () => {
    // after destroy the list stops reacting to appStore changes
    it('after destroy(), further appStore mutations no longer update the list DOM', () => {
      appStore.addJob('j1', 'problem');
      const { root, destroy } = createProofsList(appStore);
      destroyList = null; // managed manually in this test

      const rowsBefore = root.querySelectorAll('.proofs-list-item').length;
      destroy();

      appStore.addJob('j2', 'problem2');
      expect(root.querySelectorAll('.proofs-list-item').length).toBe(rowsBefore);
    });
  });
});
