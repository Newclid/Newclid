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
import './style.css';

const root = document.getElementById('app');
if (!root) {
  throw new Error('No #app element found in HTML');
}

const scene = new Scene();
export const appStore = new AppStore();
export const backendClient = new BackendClient('/api');
export const jobPoller = new JobPoller(backendClient, appStore);

const toolbar = createToolbar(scene);
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
