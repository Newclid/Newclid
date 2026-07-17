import { Viewport } from './geometry/viewport';
import { Renderer } from './render/renderer';
import { Scene } from './scene/scene';
import { attachPanZoom } from './input/panZoom';
import { attachToolDispatcher, type ToolDispatcherHandle } from './input/toolDispatcher';
import { attachShortcuts } from './input/shortcuts';
import { createToolbar } from './ui/toolbar';
import { AppStore } from './store/appStore';
import { BackendClient } from './api/backendClient';
import { JobPoller } from './api/jobPoller';
import { initNotifications, notify } from './ui/notifications';
import { attachToolbarResizer } from './ui/toolbarResizer';
import { createPointContextMenu } from './ui/pointContextMenu';
import { expandJgexPredicates, geomFromSignatures, parseConstructionSignature, parseJgexGeometry } from './emit/jgexParser';
import type { ConstructionMarker } from './emit/jgexParser';
import { buildNameTable } from './emit/names';
import { TERMINAL_STATUSES } from './api/types';
import type { JobResultPayload, SketchPoint } from './api/types';
import { theoremStore } from './store/theoremStore';
import { predicateToJgex } from './types/theorem';
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

function buildCustomTheoremPayloads() {
  return theoremStore.getAll().map((t) => ({
    name: t.name,
    description: t.description,
    premises: t.premises.map(predicateToJgex),
    conclusions: t.conclusions.map(predicateToJgex),
  }));
}

const onCanvasProofSubmit = async (jgex: string) => {
  const expanded = expandJgexPredicates(jgex);
  // Capture user's point positions now, before the scene is cleared on proof-mode entry.
  const nameTable = buildNameTable(scene);
  const userSketchPoints: SketchPoint[] = [];
  for (const obj of scene.objects.values()) {
    if (obj.kind !== 'point') continue;
    const name = nameTable.get(obj.id);
    if (name) userSketchPoints.push({ name, x: obj.x, y: obj.y });
  }

  appStore.setProblem(expanded);
  const resp = await backendClient.submitJob(expanded, buildCustomTheoremPayloads());
  appStore.addJob(resp.job_id, expanded);
  if (userSketchPoints.length > 0) {
    appStore.updateJob(resp.job_id, { userSketchPoints });
  }
  jobPoller.start(resp.job_id);
};

// For the raw JGEX text dialog: don't capture canvas coords — the JGEX may
// describe a completely different construction, so the proof visualization
// always uses the backend's returned coordinates.  The canvas is preserved
// while queued/running (same as the visual flow) and restored on exit.
const onJgexTextSubmit = async (jgex: string) => {
  const expanded = expandJgexPredicates(jgex);
  appStore.setProblem(expanded);
  const resp = await backendClient.submitJob(expanded, buildCustomTheoremPayloads());
  appStore.addJob(resp.job_id, expanded);
  jobPoller.start(resp.job_id);
};

const toolbar = createToolbar(scene, onCanvasProofSubmit, appStore, onJgexTextSubmit);
root.appendChild(toolbar.root);
attachToolbarResizer({ app: root, toolbar: toolbar.root });

initNotifications();

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
      notify('success', 'Proof complete');
    } else {
      notify('error', job.result.message);
    }
  } else if (job.error) {
    lastNotifiedKey = key;
    notify('error', job.error);
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

// dispatcherHandle is assigned below; the closure only runs once pan/zoom
// actually fires, by which point it's set.
let dispatcherHandle: ToolDispatcherHandle | undefined;
attachPanZoom(renderer.svg, viewport, () => {
  requestRedraw();
  dispatcherHandle?.refreshPreview();
});

const pointMenu = createPointContextMenu(scene, canvasHost, requestRedraw);
dispatcherHandle = attachToolDispatcher(renderer.svg, viewport, scene, requestRedraw, appStore, {
  selectMenuCallback: (pointId, x, y) => pointMenu.show(pointId, x, y),
});
scene.subscribe(() => { if (scene.tool !== 'select') pointMenu.dismiss(); });
attachShortcuts(scene, appStore);

scene.subscribe(requestRedraw);

// Floating hint pill that shows the current construction slot instruction.
const hintEl = document.createElement('div');
hintEl.className = 'slot-hint';
hintEl.hidden = true;
canvasHost.appendChild(hintEl);

// Error pill shown above the hint when a click is rejected by validation.
const errorEl = document.createElement('div');
errorEl.className = 'slot-error';
errorEl.hidden = true;
canvasHost.appendChild(errorEl);

// Track what the error pill is currently showing so unrelated scene emits
// don't restart the fade timer.
let shownError: string | null = null;
let errorFadeTimer: number | null = null;
let errorHideTimer: number | null = null;

function clearErrorDisplay() {
  if (errorFadeTimer !== null) { clearTimeout(errorFadeTimer); errorFadeTimer = null; }
  if (errorHideTimer !== null) { clearTimeout(errorHideTimer); errorHideTimer = null; }
  errorEl.style.transition = 'none';
  errorEl.style.opacity = '0';
  errorEl.hidden = true;
  shownError = null;
}

scene.subscribe(() => {
  hintEl.textContent = scene.slotHint ?? '';
  hintEl.hidden = !scene.slotHint;

  const err = scene.slotError;

  if (!err) {
    if (shownError !== null) clearErrorDisplay();
    return;
  }

  // Same error already showing — don't restart the countdown.
  if (err === shownError) return;

  // New error: reset and start fresh.
  clearErrorDisplay();
  shownError = err;
  errorEl.textContent = err;
  errorEl.style.transition = 'none';
  errorEl.style.opacity = '1';
  errorEl.hidden = false;
  void errorEl.offsetWidth; // flush so the reset applies before the transition starts

  // Start fading at 3.5 s.
  errorFadeTimer = window.setTimeout(() => {
    errorEl.style.transition = 'opacity 1.5s ease';
    errorEl.style.opacity = '0';
  }, 3500);

  // Fully hide at 5 s and clean up scene state.
  errorHideTimer = window.setTimeout(() => {
    errorEl.hidden = true;
    shownError = null;
    errorFadeTimer = null;
    errorHideTimer = null;
    scene.setSlotError(null);
  }, 5000);
});

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

// Parse premises in text order and resolve each one's canvas geometry signature (if any).
// Each premise ends with a bracket ref: [Cn] = construction, [Nn] = numerical (no canvas), [\d+] = step ref.
function buildTextPremiseSigs(
  rawStep: string,
  stepSigs: string[],
  constructionSigs: string[],
  proofSteps: string[],
): Array<string | null> {
  const premiseSection = rawStep.match(/^\d+\.\s*\|\s*(.+?)\s*=\(/)?.[1] ?? '';

  // Build step-number (as printed, e.g. 36 from "036.") → step_signatures index.
  const stepNumToSigIdx = new Map<number, number>();
  for (let i = 0; i < proofSteps.length; i++) {
    const nm = proofSteps[i].match(/^0*(\d+)\./);
    if (nm) stepNumToSigIdx.set(parseInt(nm[1], 10), i);
  }

  const result: Array<string | null> = [];
  const premRegex = /.*?\[\w*\d+\]/g;
  let m;
  while ((m = premRegex.exec(premiseSection)) !== null) {
    const prem = m[0].replace(/^[,\s]+/, '').trim();
    const cMatch = prem.match(/\[C(\d+)\]$/);
    const nMatch = prem.match(/\[N\d+\]$/);
    const stepMatch = prem.match(/\[(\d+)\]$/);

    if (cMatch) {
      const cIdx = parseInt(cMatch[1], 10);
      result.push((cIdx >= 0 && cIdx < constructionSigs.length && constructionSigs[cIdx])
        ? constructionSigs[cIdx] : null);
    } else if (nMatch) {
      result.push(null); // numerical check — no canvas geometry
    } else if (stepMatch) {
      const stepNum = parseInt(stepMatch[1], 10);
      const sigIdx = stepNumToSigIdx.get(stepNum);
      result.push((sigIdx !== undefined && stepSigs[sigIdx]) ? stepSigs[sigIdx] : null);
    } else {
      result.push(null);
    }
  }
  return result;
}

let savedSceneSnapshot: SceneSnapshot | null = null;
let wasInProofMode = false;
let sceneCleared = false; // true once we clear the canvas for the current proof session
let lastJobResult: JobResultPayload | null | undefined;
// Use sentinels so the first run always builds the sketch.
let lastStepIndex: number | null = -1 as unknown as null;
let lastSubStepIndex: number | null = -1 as unknown as null;

appStore.subscribe(() => {
  const { proofMode, activeJobId } = appStore;

  if (proofMode && !wasInProofMode) {
    savedSceneSnapshot = scene.snapshot();
    sceneCleared = false;
    // Don't clear the canvas yet — keep the user's constructions visible
    // while the proof is queued or running.
  } else if (!proofMode && wasInProofMode) {
    if (savedSceneSnapshot) {
      scene.restore(savedSceneSnapshot);
      savedSceneSnapshot = null;
    }
    sceneCleared = false;
  }
  wasInProofMode = proofMode;

  if (proofMode && activeJobId) {
    const job = appStore.jobs.get(activeJobId);
    const result = job?.result;
    const stepIndex = appStore.activeProofStepIndex;
    const subStepIndex = appStore.activeProofSubStepIndex;

    // Clear the user's construction only when the proof result first arrives
    // so their drawing stays visible while the proof is queued or running.
    if (result && !sceneCleared) {
      scene.clear();
      sceneCleared = true;
    }

    // Auto-initialise to step 0 when result first arrives.
    if (result && result !== lastJobResult && (result.proof_sections?.proof_steps.length ?? 0) > 0 && stepIndex === null) {
      appStore.setActiveProofStep(0);
      return; // setActiveProofStep will trigger another subscription call
    }

    if (result === lastJobResult && stepIndex === lastStepIndex && subStepIndex === lastSubStepIndex) { requestRedraw(); return; }
    lastJobResult = result;
    lastStepIndex = stepIndex;
    lastSubStepIndex = subStepIndex;

    const problem = job?.problem ?? '';
    // Use the user's drawing coordinates stored at submission time.
    // Fall back to backend coords (with normalisation + viewport fit) only
    // for jobs submitted via raw JGEX text input (no canvas drawing).
    const userPoints = job?.userSketchPoints ?? [];
    const points: SketchPoint[] = userPoints.length > 0
      ? userPoints
      : normalizeSketchPoints(result?.sketch_points ?? []);
    const sections = result?.proof_sections;
    const stepSigs = sections?.step_signatures ?? [];

    const baseGeometry = [
      ...parseJgexGeometry(problem),
      ...geomFromSignatures([...new Set(sections?.construction_signatures ?? [])]),
    ];

    let geometry = baseGeometry;
    let extraGeometry = geomFromSignatures([
      ...new Set([
        ...(sections?.step_signatures ?? []),
        ...(sections?.goal_signatures ?? []),
      ]),
    ]);
    let highlightGeometry: ReturnType<typeof geomFromSignatures> | undefined;
    let highlightPoints: string[] | undefined;
    let premiseGeometry: ReturnType<typeof geomFromSignatures> | undefined;
    let premisePoints: string[] | undefined;
    let premiseMarkers: ConstructionMarker[] | undefined;
    let markers: ConstructionMarker[];

    if (stepIndex !== null && stepSigs[stepIndex] !== undefined) {
      // Past steps merged into solid base geometry (no markers).
      const pastSigs = [...new Set(stepSigs.slice(0, stepIndex))];
      geometry = [...baseGeometry, ...geomFromSignatures(pastSigs)];
      extraGeometry = [];

      const constructionSigs = sections?.construction_signatures ?? [];
      const rawStepText = sections?.proof_steps?.[stepIndex] ?? '';

      // Premises in text order; each entry is a canvas signature or null (no geometry).
      const textPremiseSigs = buildTextPremiseSigs(
        rawStepText, stepSigs, constructionSigs, sections?.proof_steps ?? [],
      );

      // Sub-steps: one per text premise + the conclusion.
      const conclusionSubStep = textPremiseSigs.length;
      const rawSubStep = appStore.activeProofSubStepIndex ?? 0;
      const subStep = Math.max(0, Math.min(rawSubStep, conclusionSubStep));

      const geomPoints = (geoms: ReturnType<typeof geomFromSignatures>): string[] =>
        geoms.flatMap((g) => {
          if (g.kind === 'segment' || g.kind === 'line') return [g.p1, g.p2];
          if (g.kind === 'circle') return [g.center, g.through];
          if (g.kind === 'circumcircle') return [g.p1, g.p2, g.p3];
          return [];
        });

      if (subStep === conclusionSubStep) {
        // Conclusion: highlight the deduction in green.
        highlightGeometry = geomFromSignatures([stepSigs[stepIndex]]);
        highlightPoints = geomPoints(highlightGeometry);
        const m = parseConstructionSignature(stepSigs[stepIndex]);
        markers = m ? [m] : [];
      } else {
        // Premise sub-step: highlight in amber if this premise has canvas geometry.
        const pSig = textPremiseSigs[subStep];
        if (pSig) {
          premiseGeometry = geomFromSignatures([pSig]);
          premisePoints = geomPoints(premiseGeometry);
          const pm = parseConstructionSignature(pSig);
          premiseMarkers = pm ? [pm] : [];
        }
        // If pSig is null (e.g. [N-type] premise): canvas shows no highlight — correct.
        markers = [];
      }
    } else {
      // Fallback: no step selected — show everything at once (original behaviour).
      markers = [
        ...new Set([
          ...(sections?.construction_signatures ?? []),
          ...(sections?.step_signatures ?? []),
          ...(sections?.goal_signatures ?? []),
        ]),
      ]
        .map(parseConstructionSignature)
        .filter((m): m is ConstructionMarker => m !== null);
    }

    renderer.proofSketch = points.length > 0
      ? { points, geometry, extraGeometry, highlightGeometry, highlightPoints,
          premiseGeometry, premisePoints, premiseMarkers, markers }
      : null;
    if (renderer.proofSketch && userPoints.length === 0) {
      viewport.fitPoints(renderer.proofSketch.points);
    }
  } else {
    lastJobResult = null;
    lastStepIndex = -1 as unknown as null;
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

// --- Zoom controls ---
const zoomControls = document.createElement('div');
zoomControls.className = 'zoom-controls';

const zoomInBtn = document.createElement('button');
zoomInBtn.className = 'zoom-btn';
zoomInBtn.textContent = '+';
zoomInBtn.title = 'Zoom in';
zoomInBtn.addEventListener('click', () => {
  const cx = viewport.width / 2;
  const cy = viewport.height / 2;
  viewport.zoomAt({ x: cx, y: cy, _kind: 'screen' } as any, 1.25);
  requestRedraw();
});

const zoomOutBtn = document.createElement('button');
zoomOutBtn.className = 'zoom-btn';
zoomOutBtn.textContent = '−';
zoomOutBtn.title = 'Zoom out';
zoomOutBtn.addEventListener('click', () => {
  const cx = viewport.width / 2;
  const cy = viewport.height / 2;
  viewport.zoomAt({ x: cx, y: cy, _kind: 'screen' } as any, 1 / 1.25);
  requestRedraw();
});

zoomControls.appendChild(zoomInBtn);
zoomControls.appendChild(zoomOutBtn);
canvasHost.appendChild(zoomControls);

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
  const hasSketchPoints = (job?.result?.sketch_points?.length ?? 0) > 0;
  // Redraw randomises coordinates — only meaningful for JGEX submissions where
  // coordinates are generated by the solver. For visual submissions the user's
  // own drawing is the source of truth, so redrawing makes no sense.
  const wasVisualSubmission = job?.userSketchPoints !== undefined;
  redrawBtn.hidden = !hasSketchPoints || wasVisualSubmission;
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