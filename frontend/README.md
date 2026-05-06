# Newclid frontend

Web frontend for the Newclid geometry theorem prover. This is an
incremental from-scratch rebuild — each commit adds one well-understood
piece, so this is *mid-build*, not abandoned. See **Roadmap** below for
what is intentionally not here yet.

## Status

A blank geometry plane (grid + axes) with pan and zoom. Nothing else.

## Running

Requires Node 18+.

```sh
npm install
npm run dev        # vite dev server, opens http://localhost:5173
npm run build      # tsc -b && vite build
npm run typecheck
```

## Layout

```
src/
  main.ts              entry point — boots viewport, renderer, input
  style.css            base layout (full-window canvas)
  vite-env.d.ts        Vite ambient types (e.g. CSS side-effect imports)
  geometry/
    coords.ts          WorldPoint / ScreenPoint branded types + factories
    viewport.ts        camera state + world<->screen transforms + pan/zoom math
  render/
    renderer.ts        SVG drawing of grid, axes, tick labels
  input/
    panZoom.ts         spacebar+drag = pan, wheel = zoom; rAF-coalesced
```

The split is deliberate: `geometry/` is pure math (no DOM), `render/` is
DOM output (no input handling), `input/` is DOM events (no drawing).
Each layer talks to the next through `Viewport`, which is the only
shared mutable state.

## Coordinate system

- **World**: Y points up, origin at math (0, 0), units are abstract.
- **Screen**: Y points down (SVG convention), origin at the top-left of
  the SVG element.
- The viewport is parameterized as `{ center: WorldPoint, scale, width,
  height }`, where `scale` is pixels per world unit. Pan moves `center`
  in world units (pixel delta divided by scale). Zoom changes `scale`
  while keeping the world point under the cursor pinned to the same
  screen position.

`WorldPoint` and `ScreenPoint` are branded types — the compiler stops
you from passing a screen pixel where a world coord is expected. Use
the `world(x, y)` and `screen(x, y)` factories.

## Input bindings

| Action | Binding |
| --- | --- |
| Pan  | hold `Space`, then left-drag |
| Zoom | scroll wheel (zooms toward cursor) |

Bare left-click is intentionally unbound; future tools (point, line,
circle, ...) will claim it.

## Roadmap

Things that are *not* built yet, in rough order:

- Geometric object model (points, lines, circles) and persistence
- Construction tools (place point, draw line/segment/circle)
- Selection, hover, hit-testing
- Problem input (a textual statement -> initial figure)
- Proof viewer (step-through of solver output)
- Backend wiring (Newclid solver via WebSocket or HTTP)

If you've landed here expecting any of the above, you're early — the
solver and prior frontend live elsewhere in this repo and this
directory will catch up to them piece by piece.
