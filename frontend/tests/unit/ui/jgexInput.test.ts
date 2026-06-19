import { describe, it, expect, vi, afterEach } from 'vitest';
import { createJgexInput } from '../../../src/ui/jgexInput';

describe('createJgexInput', () => {
  let handle: ReturnType<typeof createJgexInput>;

  afterEach(() => {
    handle.destroy();
    document.body.innerHTML = '';
  });

  // the backdrop needs is-open to trigger the CSS reveal animation
  it('open adds is-open class to the backdrop', () => {
    handle = createJgexInput();
    handle.open();
    expect(handle.root.classList.contains('is-open')).toBe(true);
  });

  // close must remove is-open so the backdrop fades out
  it('close removes is-open class from the backdrop', () => {
    handle = createJgexInput();
    handle.open();
    handle.close();
    expect(handle.root.classList.contains('is-open')).toBe(false);
  });

  // the constructor mounts immediately so open/close work on first call
  it('appends the backdrop to document.body on construction', () => {
    handle = createJgexInput();
    expect(document.body.contains(handle.root)).toBe(true);
  });

  // destroy removes the node so orphan elements do not accumulate
  it('destroy removes the backdrop from document.body', () => {
    handle = createJgexInput();
    handle.destroy();
    expect(document.body.contains(handle.root)).toBe(false);
  });

  // Cancel is the standard non-destructive dismiss gesture
  it('clicking the cancel button removes is-open', () => {
    handle = createJgexInput();
    handle.open();
    const cancelBtn = handle.root.querySelector('.jgex-btn-quiet') as HTMLButtonElement;
    cancelBtn.click();
    expect(handle.root.classList.contains('is-open')).toBe(false);
  });

  // clicking the dark backdrop area outside the dialog is another dismiss gesture
  it('mousedown directly on the backdrop removes is-open', () => {
    handle = createJgexInput();
    handle.open();
    handle.root.dispatchEvent(new MouseEvent('mousedown', { bubbles: true }));
    expect(handle.root.classList.contains('is-open')).toBe(false);
  });

  // Escape is the universal keyboard shortcut for dismissing dialogs
  it('pressing Escape in the input removes is-open', () => {
    handle = createJgexInput();
    handle.open();
    const input = handle.root.querySelector('input') as HTMLInputElement;
    input.dispatchEvent(new KeyboardEvent('keydown', { key: 'Escape', bubbles: true }));
    expect(handle.root.classList.contains('is-open')).toBe(false);
  });

  // Enter submits the trimmed input value to the onSubmit callback
  it('pressing Enter calls onSubmit with the trimmed input value', async () => {
    const onSubmit = vi.fn().mockResolvedValue(undefined);
    handle = createJgexInput(onSubmit);
    const input = handle.root.querySelector('input') as HTMLInputElement;
    input.value = '  coll A B C  ';
    input.dispatchEvent(new KeyboardEvent('keydown', { key: 'Enter', bubbles: true }));
    await vi.waitFor(() => expect(onSubmit).toHaveBeenCalledWith('coll A B C'));
  });

  // clicking submit is the mouse equivalent of pressing Enter
  it('clicking the submit button calls onSubmit with the input value', async () => {
    const onSubmit = vi.fn().mockResolvedValue(undefined);
    handle = createJgexInput(onSubmit);
    const input = handle.root.querySelector('input') as HTMLInputElement;
    input.value = 'perp A B C D';
    const submitBtn = handle.root.querySelector('.jgex-btn-accent') as HTMLButtonElement;
    submitBtn.click();
    await vi.waitFor(() => expect(onSubmit).toHaveBeenCalledWith('perp A B C D'));
  });

  // a rejected onSubmit must surface an error so the user knows the submit failed
  it('shows "Server Error" in the error paragraph when onSubmit rejects', async () => {
    const onSubmit = vi.fn().mockRejectedValue(new Error('network error'));
    handle = createJgexInput(onSubmit);
    handle.open();
    const input = handle.root.querySelector('input') as HTMLInputElement;
    input.value = 'something';
    const submitBtn = handle.root.querySelector('.jgex-btn-accent') as HTMLButtonElement;
    submitBtn.click();
    await vi.waitFor(() => {
      const errorEl = handle.root.querySelector('.jgex-error') as HTMLElement;
      expect(errorEl.textContent).toBe('Server Error');
    });
  });
});
