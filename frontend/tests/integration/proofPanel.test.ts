import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest';
import { createProofPanel } from '../../src/ui/proofPanel';
import { AppStore } from '../../src/store/appStore';
import {
  makeSucceededResult,
  makeFailedResult,
  makeMultiStepResult,
} from '../fixtures/proofResult';

// createProofPanel depends only on AppStore and the DOM — no heavy collaborators to mock.

describe('createProofPanel + AppStore', () => {
  let appStore: AppStore;

  beforeEach(() => {
    appStore = new AppStore();
  });

  afterEach(() => {
    vi.restoreAllMocks();
  });

  // ─────────────────────────────────────────────────────────────
  // Status display
  // ─────────────────────────────────────────────────────────────

  describe('status display', () => {
    // spinner visible only while the backend is still working
    it('shows spinner + "Queued…" badge for a queued job', () => {
      const { root } = createProofPanel(appStore);
      appStore.addJob('j1', 'problem');

      expect(root.querySelector('.proof-spinner')).toBeTruthy();
      const badge = root.querySelector('.proof-status-badge');
      expect(badge?.textContent).toBe('Queued…');
      expect(badge?.getAttribute('data-status')).toBe('queued');
    });

    // running is also in-progress, same visual treatment as queued
    it('shows spinner + "Running…" badge for a running job', () => {
      const { root } = createProofPanel(appStore);
      appStore.addJob('j1', 'problem');
      appStore.updateJob('j1', { status: 'running' });

      expect(root.querySelector('.proof-spinner')).toBeTruthy();
      const badge = root.querySelector('.proof-status-badge');
      expect(badge?.textContent).toBe('Running…');
      expect(badge?.getAttribute('data-status')).toBe('running');
    });

    // success: no spinner, badge switches to "Proved"
    it('shows "Proved" badge without spinner for a succeeded job', () => {
      const { root } = createProofPanel(appStore);
      appStore.addJob('j1', 'problem');
      appStore.updateJob('j1', { result: makeSucceededResult(), status: 'succeeded' });

      expect(root.querySelector('.proof-spinner')).toBeNull();
      const badge = root.querySelector('.proof-status-badge');
      expect(badge?.textContent).toBe('Proved');
      expect(badge?.getAttribute('data-status')).toBe('succeeded');
    });

    // failure: badge reflects "Failed"
    it('shows "Failed" badge for a failed job', () => {
      const { root } = createProofPanel(appStore);
      appStore.addJob('j1', 'problem');
      appStore.updateJob('j1', { result: makeFailedResult(), status: 'failed' });

      const badge = root.querySelector('.proof-status-badge');
      expect(badge?.textContent).toBe('Failed');
    });

    // transport error (no result, just job.error) shows the raw error string
    it('shows job.error in proof-error-msg when job has error and no result', () => {
      const { root } = createProofPanel(appStore);
      appStore.addJob('j1', 'problem');
      appStore.updateJob('j1', { error: 'network timeout' });

      const msg = root.querySelector('.proof-error-msg');
      expect(msg?.textContent).toBe('network timeout');
    });

    // solver returned a failed result with a human-readable message
    it('shows result.message in proof-error-msg when result.status is failed', () => {
      const { root } = createProofPanel(appStore);
      appStore.addJob('j1', 'problem');
      appStore.updateJob('j1', { result: makeFailedResult('no proof found'), status: 'failed' });

      const msg = root.querySelector('.proof-error-msg');
      expect(msg?.textContent).toBe('no proof found');
    });
  });

  // ─────────────────────────────────────────────────────────────
  // Assumptions and numerical checks
  // ─────────────────────────────────────────────────────────────

  describe('assumptions and numerical checks', () => {
    // premise labels use 1-based P prefix derived from proof_sections.assumptions
    it('renders assumptions list with P1… labels', () => {
      const { root } = createProofPanel(appStore);
      appStore.addJob('j1', 'problem');
      appStore.updateJob('j1', { result: makeSucceededResult(), status: 'succeeded' });

      const labels = Array.from(root.querySelectorAll('.proof-labeled-item .proof-ref-premise'));
      expect(labels.length).toBe(1);
      expect(labels[0].textContent).toBe('P1');
    });

    // numerical check labels use 1-based N prefix
    it('renders numerical checks with N1… labels', () => {
      const { root } = createProofPanel(appStore);
      appStore.addJob('j1', 'problem');
      appStore.updateJob('j1', { result: makeSucceededResult(), status: 'succeeded' });

      const labels = Array.from(root.querySelectorAll('.proof-labeled-item .proof-ref-numerical'));
      expect(labels.length).toBe(1);
      expect(labels[0].textContent).toBe('N1');
    });
  });

  // ─────────────────────────────────────────────────────────────
  // Step navigation
  // ─────────────────────────────────────────────────────────────

  describe('step navigation', () => {
    function setupMultiStep() {
      const handle = createProofPanel(appStore);
      appStore.addJob('j1', 'problem');
      appStore.updateJob('j1', { result: makeMultiStepResult(2), status: 'succeeded' });
      return handle;
    }

    function getStepBtns(root: Element) {
      return root.querySelectorAll<HTMLButtonElement>('.proof-step-nav-btn');
    }

    // counter is 1-indexed with the total for orientation
    it('shows "Step 1 of 2" counter initially', () => {
      const { root } = setupMultiStep();
      expect(root.querySelector('.proof-step-counter')?.textContent).toBe('Step 1 of 2');
    });

    // prev always disabled at step 0, next always disabled at last step
    it('"← Prev" is disabled on step 0 and "Next →" is disabled on last step', () => {
      const { root } = setupMultiStep();
      const [prevBtn, nextBtn] = getStepBtns(root);
      expect(prevBtn.disabled).toBe(true);
      expect(nextBtn.disabled).toBe(false);

      appStore.setActiveProofStep(1); // advance to last step
      const [prevBtn2, nextBtn2] = getStepBtns(root);
      expect(prevBtn2.disabled).toBe(false);
      expect(nextBtn2.disabled).toBe(true);
    });

    // clicking Next delegates to appStore, not directly to the DOM
    it('clicking Next → calls appStore.setActiveProofStep(1)', () => {
      const { root } = setupMultiStep();
      const spy = vi.spyOn(appStore, 'setActiveProofStep');
      getStepBtns(root)[1].click();
      expect(spy).toHaveBeenCalledWith(1);
    });

    // clicking Prev at step 1 calls setActiveProofStep(0)
    it('clicking ← Prev calls appStore.setActiveProofStep with previous index', () => {
      const { root } = setupMultiStep();
      appStore.setActiveProofStep(1);
      const spy = vi.spyOn(appStore, 'setActiveProofStep');
      getStepBtns(root)[0].click();
      expect(spy).toHaveBeenCalledWith(0);
    });

    // counter text updates reactively on navigation
    it('navigating to step 2 updates the counter to "Step 2 of 2"', () => {
      const { root } = setupMultiStep();
      appStore.setActiveProofStep(1);
      expect(root.querySelector('.proof-step-counter')?.textContent).toBe('Step 2 of 2');
    });
  });

  // ─────────────────────────────────────────────────────────────
  // Substep navigation and premise/conclusion highlighting
  // ─────────────────────────────────────────────────────────────

  describe('substep navigation (premise/conclusion highlighting)', () => {
    // SAMPLE_PROOF_STEP has 2 text premises → 3 substeps: 0, 1, 2 (conclusion)

    function setupWithStep() {
      const handle = createProofPanel(appStore);
      appStore.addJob('j1', 'problem');
      appStore.updateJob('j1', { result: makeSucceededResult(), status: 'succeeded' });
      // activeProofSubStepIndex defaults to 0
      return handle;
    }

    function subPrev(root: Element): HTMLButtonElement {
      return root.querySelectorAll<HTMLButtonElement>('.proof-substep-nav-btn')[0];
    }

    function subNext(root: Element): HTMLButtonElement {
      return root.querySelectorAll<HTMLButtonElement>('.proof-substep-nav-btn')[1];
    }

    // substep 0 highlights the first premise span
    it('first substep marks premise 0 with is-active-substep', () => {
      const { root } = setupWithStep();
      const premises = root.querySelectorAll('.proof-step-premise');
      expect(premises[0].classList.contains('is-active-substep')).toBe(true);
      expect(premises[1].classList.contains('is-active-substep')).toBe(false);
    });

    // clicking Next substep advances the highlight to premise 1
    it('clicking Next substep advances to premise 1', () => {
      const { root } = setupWithStep();
      subNext(root).click();
      const premises = root.querySelectorAll('.proof-step-premise');
      expect(premises[0].classList.contains('is-active-substep')).toBe(false);
      expect(premises[1].classList.contains('is-active-substep')).toBe(true);
    });

    // two Next substep clicks land on the conclusion
    it('two Next substep clicks reach the conclusion substep', () => {
      const { root } = setupWithStep();
      subNext(root).click();
      subNext(root).click();
      expect(root.querySelector('.proof-step-conclusion')?.classList.contains('is-active-substep')).toBe(true);
    });

    // counter says "Conclusion" instead of "Premise N of M" on the last substep
    it('substep counter shows "Conclusion" at last substep', () => {
      const { root } = setupWithStep();
      subNext(root).click();
      subNext(root).click();
      expect(root.querySelector('.proof-substep-counter')?.textContent).toBe('Conclusion');
    });

    // can't go past the conclusion substep
    it('Next substep button is disabled at the conclusion substep', () => {
      const { root } = setupWithStep();
      subNext(root).click();
      subNext(root).click();
      expect(subNext(root).disabled).toBe(true);
    });

    // going back from premise 1 returns to premise 0
    it('clicking ← Prev substep goes back one position', () => {
      const { root } = setupWithStep();
      subNext(root).click();
      subPrev(root).click();
      const premises = root.querySelectorAll('.proof-step-premise');
      expect(premises[0].classList.contains('is-active-substep')).toBe(true);
    });
  });

  // ─────────────────────────────────────────────────────────────
  // Derived facts
  // ─────────────────────────────────────────────────────────────

  describe('derived facts', () => {
    // derived facts section is only appended when stepIndex is non-null
    it('derived facts section is absent when activeProofStepIndex is null', () => {
      const { root } = createProofPanel(appStore);
      appStore.addJob('j1', 'problem');
      appStore.updateJob('j1', { result: makeSucceededResult(), status: 'succeeded' });

      const titles = Array.from(root.querySelectorAll('.proof-section-title')).map(s => s.textContent);
      expect(titles).not.toContain('Derived Facts');
    });

    // setActiveProofStep(0) makes stepIndex non-null, derived facts section appears
    it('shows F1 derived fact label after setActiveProofStep(0)', () => {
      const { root } = createProofPanel(appStore);
      appStore.addJob('j1', 'problem');
      appStore.updateJob('j1', { result: makeSucceededResult(), status: 'succeeded' });
      appStore.setActiveProofStep(0);

      // scope to .proof-labeled-item to exclude the legend's .proof-ref-derived entry
      const derivedLabels = root.querySelectorAll('.proof-labeled-item .proof-ref-derived');
      expect(derivedLabels.length).toBe(1);
      expect(derivedLabels[0].textContent).toBe('F1');
    });
  });

  // ─────────────────────────────────────────────────────────────
  // Proven goals
  // ─────────────────────────────────────────────────────────────

  describe('proven goals', () => {
    // proven goals section only appears when at the last step
    it('proven goals section is shown when at the last step of a succeeded result', () => {
      const { root } = createProofPanel(appStore);
      appStore.addJob('j1', 'problem');
      appStore.updateJob('j1', { result: makeSucceededResult(), status: 'succeeded' });
      appStore.setActiveProofStep(0); // 1-step result → step 0 is last step

      const titles = Array.from(root.querySelectorAll('.proof-section-title')).map(s => s.textContent);
      expect(titles).toContain('Proven Goals');
    });

    // not at last step → proven goals are withheld
    it('proven goals section is hidden when not at the last step', () => {
      const { root } = createProofPanel(appStore);
      appStore.addJob('j1', 'problem');
      appStore.updateJob('j1', { result: makeMultiStepResult(2), status: 'succeeded' });
      appStore.setActiveProofStep(0); // 2-step result → step 0 is not last

      const titles = Array.from(root.querySelectorAll('.proof-section-title')).map(s => s.textContent);
      expect(titles).not.toContain('Proven Goals');
    });
  });

  // ─────────────────────────────────────────────────────────────
  // "← Back to edit" button
  // ─────────────────────────────────────────────────────────────

  describe('"← Back to edit" button', () => {
    // the back button is always in the root, not inside the reactive content area
    it('clicking it calls appStore.exitProofMode()', () => {
      const { root } = createProofPanel(appStore);
      const spy = vi.spyOn(appStore, 'exitProofMode');
      root.querySelector<HTMLButtonElement>('.proof-back-btn')!.click();
      expect(spy).toHaveBeenCalled();
    });
  });

  // ─────────────────────────────────────────────────────────────
  // destroy()
  // ─────────────────────────────────────────────────────────────

  describe('destroy()', () => {
    // unsubscribing means the DOM no longer reflects subsequent state changes
    it('after destroy(), further appStore mutations no longer re-render the panel', () => {
      const { root, destroy } = createProofPanel(appStore);
      appStore.addJob('j1', 'problem');
      const textBefore = root.querySelector('.proof-status-badge')?.textContent;

      destroy();

      appStore.updateJob('j1', { result: makeSucceededResult(), status: 'succeeded' });
      expect(root.querySelector('.proof-status-badge')?.textContent).toBe(textBefore);
    });
  });
});
