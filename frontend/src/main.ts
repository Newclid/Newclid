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
import { geomFromSignatures, parseConstructionSignature, parseJgexGeometry } from './emit/jgexParser';
import type { ConstructionMarker } from './emit/jgexParser';
import { TERMINAL_STATUSES } from './api/types';
import type { SceneSnapshot } from './scene/scene';
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
  appStore.addJob(resp.job_id, jgex);
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

function normalizeSketchPoints(
  pts: { name: string; x: number; y: number }[],
): { name: string; x: number; y: number }[] {
  if (pts.length === 0) return pts;
  const xs = pts.map(p => p.x), ys = pts.map(p => p.y);
  const minX = Math.min(...xs), maxX = Math.max(...xs);
  const minY = Math.min(...ys), maxY = Math.max(...ys);
  const cx = (minX + maxX) / 2, cy = (minY + maxY) / 2;
  const span = Math.max(maxX - minX, maxY - minY);
  const scale = span > 1e-9 ? 4 / span : 1;
  return pts.map(p => ({
    name: p.name,
    x: (p.x - cx) * scale + 3,
    y: (p.y - cy) * scale + 3,
  }));
}

let savedSceneSnapshot: SceneSnapshot | null = null;
let wasInProofMode = false;

appStore.subscribe(() => {
  const { proofMode, activeJobId } = appStore;

  if (proofMode && !wasInProofMode) {
    savedSceneSnapshot = scene.snapshot();
    scene.clear();
  } else if (!proofMode && wasInProofMode) {
    if (savedSceneSnapshot) {
      scene.restore(savedSceneSnapshot);
      savedSceneSnapshot = null;
    }
  }
  wasInProofMode = proofMode;

  if (proofMode && activeJobId) {
    const job = appStore.jobs.get(activeJobId);
    const raw = job?.result?.sketch_points ?? [];
    const sketchPoints = normalizeSketchPoints(raw);
    const problem = job?.problem ?? '';
    const sections = job?.result?.proof_sections;
    const markerSigs = sections?.construction_signatures ?? [];
    const markers = markerSigs
      .map(parseConstructionSignature)
      .filter((m): m is ConstructionMarker => m !== null);
    const allSigs = [
      ...(sections?.construction_signatures ?? []),
      ...(sections?.step_signatures ?? []),
    ];
    const predicateGeom = geomFromSignatures(allSigs);
    renderer.proofSketch = sketchPoints.length > 0
      ? {
          points: sketchPoints,
          geometry: [...parseJgexGeometry(problem), ...predicateGeom],
          markers,
        }
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

// --- Redraw button ---
const redrawBtn = document.createElement('button');
redrawBtn.className = 'redraw-btn';
redrawBtn.textContent = 'Redraw';
redrawBtn.hidden = true;
canvasHost.appendChild(redrawBtn);

appStore.subscribe(() => {
  const { proofMode, activeJobId } = appStore;
  if (!proofMode || !activeJobId) { redrawBtn.hidden = true; return; }
  const job = appStore.jobs.get(activeJobId);
  redrawBtn.hidden = !((job?.result?.sketch_points?.length ?? 0) > 0);
});

let redrawing = false;
redrawBtn.addEventListener('click', async () => {
  if (redrawing) return;
  const targetJobId = appStore.activeJobId;
  const targetJob = targetJobId ? appStore.jobs.get(targetJobId) : null;
  if (!targetJobId || !targetJob?.problem) return;

  redrawing = true;
  redrawBtn.disabled = true;
  redrawBtn.textContent = 'Redrawing…';
  try {
    const { job_id } = await backendClient.submitJob(targetJob.problem);
    await new Promise<void>((resolve) => {
      const iv = setInterval(async () => {
        try {
          const statusResp = await backendClient.getJobStatus(job_id);
          if (!TERMINAL_STATUSES.has(statusResp.status)) return;
          clearInterval(iv);
          const resultResp = await backendClient.getJobResult(job_id);
          const raw = resultResp.result?.sketch_points ?? [];
          const currentJob = appStore.jobs.get(targetJobId);
          if (raw.length > 0 && currentJob?.result) {
            appStore.updateJob(targetJobId, {
              result: { ...currentJob.result, sketch_points: raw },
            });
          }
          resolve();
        } catch {
          clearInterval(iv);
          resolve();
        }
      }, 2000);
    });
  } catch { /* network error: fail silently */ } finally {
    redrawing = false;
    redrawBtn.disabled = false;
    redrawBtn.textContent = 'Redraw';
  }
});
