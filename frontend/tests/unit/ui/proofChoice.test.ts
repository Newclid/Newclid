import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest';
import { createProofChoice } from '../../../src/ui/proofChoice';

describe('createProofChoice', () => {
  let onJgex: () => void;
  let onPoints: () => void;
  let handle: ReturnType<typeof createProofChoice>;

  beforeEach(() => {
    onJgex = vi.fn();
    onPoints = vi.fn();
    handle = createProofChoice({ onJgex, onPoints });
  });

  afterEach(() => {
    handle.destroy();
    document.body.innerHTML = '';
  });

  // open must add is-open to trigger the CSS backdrop transition
  it('open adds is-open class to the backdrop', () => {
    handle.open();
    expect(handle.root.classList.contains('is-open')).toBe(true);
  });

  // close must remove is-open to dismiss the dialog
  it('close removes is-open class from the backdrop', () => {
    handle.open();
    handle.close();
    expect(handle.root.classList.contains('is-open')).toBe(false);
  });

  // the constructor appends to body so absolute CSS positioning works from the start
  it('appends backdrop to document.body on construction', () => {
    expect(document.body.contains(handle.root)).toBe(true);
  });

  // the visual route calls onPoints so the canvas goal picker activates
  it('clicking the visual option button calls opts.onPoints', () => {
    const visualBtn = handle.root.querySelector('.proof-choice-btn-primary') as HTMLButtonElement;
    visualBtn.click();
    expect(onPoints).toHaveBeenCalledOnce();
  });

  // the dialog must close after forwarding the callback so the canvas is visible
  it('clicking the visual option button also closes the dialog', () => {
    handle.open();
    const visualBtn = handle.root.querySelector('.proof-choice-btn-primary') as HTMLButtonElement;
    visualBtn.click();
    expect(handle.root.classList.contains('is-open')).toBe(false);
  });

  // the syntax route calls onJgex so the JGEX text input opens
  it('clicking the syntax option button calls opts.onJgex', () => {
    const syntaxBtn = handle.root.querySelector('.proof-choice-btn-secondary') as HTMLButtonElement;
    syntaxBtn.click();
    expect(onJgex).toHaveBeenCalledOnce();
  });

  // cancel must close without firing either route callback
  it('clicking cancel closes without calling onJgex or onPoints', () => {
    handle.open();
    const cancelBtn = handle.root.querySelector('.proof-choice-cancel') as HTMLButtonElement;
    cancelBtn.click();
    expect(handle.root.classList.contains('is-open')).toBe(false);
    expect(onJgex).not.toHaveBeenCalled();
    expect(onPoints).not.toHaveBeenCalled();
  });

  // clicking the dim area outside the dialog is a standard dismiss gesture
  it('mousedown directly on the backdrop removes is-open', () => {
    handle.open();
    handle.root.dispatchEvent(new MouseEvent('mousedown', { bubbles: true }));
    expect(handle.root.classList.contains('is-open')).toBe(false);
  });

  // mousedown on a child element inside the dialog should not close it
  it('mousedown on a child element (inside the dialog) does NOT close', () => {
    handle.open();
    const dialog = handle.root.querySelector('.jgex-dialog') as HTMLElement;
    dialog.dispatchEvent(new MouseEvent('mousedown', { bubbles: true }));
    expect(handle.root.classList.contains('is-open')).toBe(true);
  });
});
