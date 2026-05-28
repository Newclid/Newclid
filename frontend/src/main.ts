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
import { attachToolbarResizer } from './ui/toolbarResizer';
import { parseJgexGeometry } from './emit/jgexParser';
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
const toolbar = createToolbar(scene, onJgexSubmit, appStore);
root.appendChild(toolbar.root);
attachToolbarResizer({ app: root, toolbar: toolbar.root });

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
      banner.showSuccess('Proof complete');
    } else {
      banner.showError(job.result.message);
    }
  } else if (job.error) {
    lastNotifiedKey = key;
    banner.showError(job.error);
  }
});

/**
Canvas host fills the whole app and the toolbar overlays it; the viewport
tracks the host size so the SVG matches the window.
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
attachToolDispatcher(renderer.svg, viewport, scene, requestRedraw, appStore);
attachShortcuts(scene, appStore);

scene.subscribe(requestRedraw);

appStore.subscribe(() => {
  const { proofMode, activeJobId } = appStore;
  if (proofMode && activeJobId) {
    const job = appStore.jobs.get(activeJobId);
    const sketchPoints = job?.result?.sketch_points ?? [];
    const problem = appStore.problem ?? '';
    renderer.proofSketch = sketchPoints.length > 0
      ? { points: sketchPoints, geometry: parseJgexGeometry(problem) }
      : null;
    if (renderer.proofSketch) {
      viewport.fitPoints(renderer.proofSketch.points);
    }
  } else {
    renderer.proofSketch = null;
  }
  requestRedraw();
});

// Keep the viewport in step with the canvas, which fills the window. A
// ResizeObserver catches window resizes; the toolbar overlays the canvas so
// dragging it doesn't change the canvas size.
const syncCanvasSize = () => {
  viewport.width = canvasHost.clientWidth;
  viewport.height = canvasHost.clientHeight;
  renderer.resize();
  requestRedraw();
};

const canvasResizeObserver = new ResizeObserver(() => syncCanvasSize());
canvasResizeObserver.observe(canvasHost);
