# Workflow Editor Technical Audit & Roadmap

## Bugs

- **`removeNode` Map deletion silently fails for rendered nodes** — `node.id` is a getter that reads from `cell?.id`, so after `node.remove()` removes the cell, `node.id` returns `null` and `_nodeMap.delete(null)` is a no-op. Cache the id before removal.

- **Pinch-to-zoom origin jump** — in the `touchmove` pinch branch, `originX/Y` is computed by dividing by `state.initialScale` rather than the renderer's *current* scale at the time of the move event. If the gesture begins while the canvas is already mid-zoom, the origin point is wrong and the content jumps on the first move.

- **`window` listeners leak on teardown** — `_attachButtonListeners` adds a `window.addEventListener('click', ...)` for context menu dismissal, and `blank:pointerdown` dynamically attaches `mousemove`/`mouseup` listeners to `document`. Neither is ever removed. Angular's `ngOnDestroy` only clears `innerHTML`, leaving these listeners attached to the global scope.

## Missing API

- **`DiagramEditor.destroy()`** — needed to properly tear down the editor. Should: remove all `window`/`document` event listeners, call `graph.clear()` and `paper.remove()` to release JointJS resources, and clear `_nodeMap` and `_edgeMap`. The Angular component's `ngOnDestroy` should delegate to this method instead of only clearing `innerHTML`.

- **`DiagramEditor.batchUpdate(fn: () => void)`** — a public wrapper around `graph.startBatch` / `graph.stopBatch` to let callers apply multiple node/edge mutations without triggering a DOM update per change. Useful for programmatic bulk operations.

## Performance

- **`_findOpenPosition` is O(N) per candidate** — the spiral search calls `graph.getElements()` on every candidate position check. At large node counts this becomes quadratic. A simple bounding-box spatial index (or just snapshotting the element bboxes once before the loop) would fix the hotspot.

- **Multiple sequential `.attr()` calls in `_fitNodeToContent`** — `label`, `descriptionLabel`, and `image` attrs are set in separate calls, each triggering a JointJS change event and a view update. Consolidating them into a single `.attr({})` call would reduce unnecessary reflows during load and resize.

- **Pan `translate` called on every `mousemove`** — the `blank:pointerdown` pan handler calls `renderer.translate()` directly on every mouse event. Wrapping the translate call in `requestAnimationFrame` (with a dirty flag) would sync it to the display refresh rate and reduce frame drops on large diagrams.

## Code Quality & Type Safety

- **Pervasive `any` in JointJS event callbacks** — all renderer event handlers (`view: any`, `event: any`, `cell: any`, `link: any`) use `any`. These should use internal interfaces (e.g. `JointCellView`, `JointLink`) to satisfy the strict typing rules in `agents.md` and catch misuse at compile time.

- **Static metadata stored as ad-hoc properties on constructor functions** — `define()` stamps `__schema`, `__defaultOptions`, `__baseClass`, `__visibleProps`, `__nodeLabel`, and `__nodeName` directly onto constructor functions. This bypasses TypeScript's type system entirely — all reads of these properties require `(cls as any).__x` casts throughout the codebase. A `TypeRegistry` map keyed by constructor or by `nodeClass` string would make this fully typed and more discoverable.

- **`deserialize` swallows invalid JSON silently** — a malformed JSON string throws a native `SyntaxError` from `JSON.parse` that propagates uncaught to the caller with no context. Wrapping the parse in a try/catch and re-throwing as a descriptive `Error` would align with the existing `UnknownNodeTypeError` pattern.
