import { createJobStatusBanner, JobStatusBanner } from './jobStatusBanner';

let _banner: JobStatusBanner | null = null;

export function initNotifications(): JobStatusBanner {
  const banner = createJobStatusBanner();
  document.body.appendChild(banner.root);
  _banner = banner;
  return banner;
}

export function notify(type: 'success' | 'error' | 'info', message: string): void {
  if (!_banner) return;
  if (type === 'success') _banner.showSuccess(message);
  else if (type === 'error') _banner.showError(message);
  else _banner.showInfo(message);
}
