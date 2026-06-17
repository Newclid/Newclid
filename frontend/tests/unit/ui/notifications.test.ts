import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest';

describe('notifications', () => {
  type Mod = typeof import('../../../src/ui/notifications');

  let mod: Mod;
  let fakeBanner: {
    root: HTMLElement;
    showSuccess: ReturnType<typeof vi.fn>;
    showError: ReturnType<typeof vi.fn>;
    showInfo: ReturnType<typeof vi.fn>;
    clear: ReturnType<typeof vi.fn>;
  };

  beforeEach(async () => {
    vi.resetModules();
    fakeBanner = {
      root: document.createElement('div'),
      showSuccess: vi.fn(),
      showError: vi.fn(),
      showInfo: vi.fn(),
      clear: vi.fn(),
    };
    vi.doMock('../../../src/ui/jobStatusBanner', () => ({
      createJobStatusBanner: vi.fn(() => fakeBanner),
    }));
    mod = await import('../../../src/ui/notifications');
  });

  afterEach(() => {
    document.body.innerHTML = '';
    vi.restoreAllMocks();
  });

  // notify must silently return early before the banner exists to avoid unhandled errors
  it('notify before initNotifications does not throw', () => {
    expect(() => mod.notify('success', 'hello')).not.toThrow();
  });

  // the banner root must be in the DOM so CSS can position and animate it
  it('initNotifications appends the banner root to document.body', () => {
    mod.initNotifications();
    expect(document.body.contains(fakeBanner.root)).toBe(true);
  });

  // notify must dispatch to showSuccess so the correct CSS variant is applied
  it('notify success calls showSuccess with the message', () => {
    mod.initNotifications();
    mod.notify('success', 'Done');
    expect(fakeBanner.showSuccess).toHaveBeenCalledWith('Done');
  });

  // notify must dispatch to showError so the error color variant is applied
  it('notify error calls showError with the message', () => {
    mod.initNotifications();
    mod.notify('error', 'Oops');
    expect(fakeBanner.showError).toHaveBeenCalledWith('Oops');
  });

  // notify must dispatch to showInfo for neutral messages
  it('notify info calls showInfo with the message', () => {
    mod.initNotifications();
    mod.notify('info', 'FYI');
    expect(fakeBanner.showInfo).toHaveBeenCalledWith('FYI');
  });
});
