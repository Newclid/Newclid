import { describe, it, expect, beforeEach } from 'vitest';
import { createJobStatusBanner } from '../../../src/ui/jobStatusBanner';

describe('createJobStatusBanner', () => {
  let banner: ReturnType<typeof createJobStatusBanner>;

  beforeEach(() => {
    banner = createJobStatusBanner();
  });

  // the returned root must be the element we mount into the page layout
  it('returns a root div with class job-status-banner', () => {
    expect(banner.root.tagName).toBe('DIV');
    expect(banner.root.classList.contains('job-status-banner')).toBe(true);
  });

  // showSuccess writes the message into the text span so the user reads it
  it('showSuccess sets the text span content to the message', () => {
    banner.showSuccess('Problem solved');
    expect(banner.root.querySelector('.job-banner-text')?.textContent).toBe('Problem solved');
  });

  // the data-variant attribute is the CSS hook that picks the right color
  it('showSuccess sets data-variant to success', () => {
    banner.showSuccess('ok');
    expect(banner.root.getAttribute('data-variant')).toBe('success');
  });

  // is-visible is what CSS uses to slide the banner into view
  it('showSuccess adds is-visible class to the root', () => {
    banner.showSuccess('ok');
    expect(banner.root.classList.contains('is-visible')).toBe(true);
  });

  // showError must route to the error variant for the red styling
  it('showError sets data-variant to error', () => {
    banner.showError('Bad thing happened');
    expect(banner.root.getAttribute('data-variant')).toBe('error');
  });

  // showInfo must route to the info variant for the neutral styling
  it('showInfo sets data-variant to info', () => {
    banner.showInfo('FYI');
    expect(banner.root.getAttribute('data-variant')).toBe('info');
  });

  // clear must hide the banner and wipe the message so nothing lingers on screen
  it('clear removes is-visible and data-variant and empties the text span', () => {
    banner.showSuccess('something');
    banner.clear();
    expect(banner.root.classList.contains('is-visible')).toBe(false);
    expect(banner.root.hasAttribute('data-variant')).toBe(false);
    expect(banner.root.querySelector('.job-banner-text')?.textContent).toBe('');
  });

  // the close button is the primary gesture for dismissing the banner
  it('clicking the close button triggers clear behavior', () => {
    banner.showError('oops');
    const closeBtn = banner.root.querySelector('.job-banner-close') as HTMLButtonElement;
    closeBtn.click();
    expect(banner.root.classList.contains('is-visible')).toBe(false);
    expect(banner.root.querySelector('.job-banner-text')?.textContent).toBe('');
  });
});
