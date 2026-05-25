import { Viewport } from './geometry/viewport';
import { Renderer } from './render/renderer';
import { Scene } from './scene/scene';
import { attachPanZoom } from './input/panZoom';
import { attachToolDispatcher } from './input/toolDispatcher';
import { attachShortcuts } from './input/shortcuts';
import { createToolbar } from './ui/toolbar';
import { AppStore } from './store/appStore';
import { BackendClient } from './api/backendClient';
import { JobPoller } from './api/jobPoller';
import { createJobStatusBanner } from './ui/jobStatusBanner';
import './style.css';

const root = document.getElementById('app');
if (!root) {
  throw new Error('No #app element found in HTML');
}

const scene = new Scene();
export const appStore = new AppStore();
export const backendClient = new BackendClient('/api');
export const jobPoller = new JobPoller(backendClient, appStore);

const onJgexSubmit = async (jgex: string) => {
  appStore.setProblem(jgex);
  const resp = await backendClient.submitJob(jgex);
  appStore.addJob(resp.job_id);
  jobPoller.start(resp.job_id);
};
const toolbar = createToolbar(scene, onJgexSubmit);

const banner = createJobStatusBanner();
document.body.appendChild(banner.root);

// Track the last notified job result so we fire at most once per result.
let lastNotifiedKey = '';
appStore.subscribe(() => {
  const { activeJobId } = appStore;
  if (!activeJobId) return;
  const job = appStore.jobs.get(activeJobId);
  if (!job) return;

  const key = `${activeJobId}:${job.result?.status ?? ''}:${job.error ?? ''}`;
  if (key === lastNotifiedKey) return;

  if (job.result) {
    lastNotifiedKey = key;
    if (job.result.status === 'succeeded') {
      console.log('[Newclid] Job succeeded', job.result);
      console.log('[Newclid] Proof steps:', job.result.proof_sections?.proof_steps);
      banner.showSuccess('Proof complete — see console for details');
    } else {
      console.log('[Newclid] Job failed', job.result);
      banner.showError(job.result.message);
    }
  } else if (job.error) {
    lastNotifiedKey = key;
    console.log('[Newclid] Job error', job.error);
    banner.showError(job.error);
  }
});
root.appendChild(toolbar.root);

/**
Canvas host fills the second grid column; viewport tracks its size so
the SVG fills the cell rather than overlapping the toolbar.
**/
const canvasHost = document.createElement('div');
canvasHost.className = 'canvas-host';
root.appendChild(canvasHost);

const viewport = new Viewport();
viewport.width = canvasHost.clientWidth;
viewport.height = canvasHost.clientHeight;

const renderer = new Renderer(canvasHost, viewport, scene);

let frameQueued = false;
const requestRedraw = () => {
  if (frameQueued) return;
  frameQueued = true;
  requestAnimationFrame(() => {
    frameQueued = false;
    renderer.draw();
  });
};
renderer.draw();

attachPanZoom(renderer.svg, viewport, requestRedraw);
attachToolDispatcher(renderer.svg, viewport, scene, requestRedraw);
attachShortcuts(scene);

scene.subscribe(requestRedraw);

window.addEventListener('resize', () => {
  viewport.width = canvasHost.clientWidth;
  viewport.height = canvasHost.clientHeight;
  renderer.resize();
  requestRedraw();
});
