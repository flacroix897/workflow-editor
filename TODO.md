# Workflow Editor Technical Audit & Roadmap

## Code Smells

- **`builtIns` array declared three times verbatim** — the list of built-in prop keys (`label`, `labelColor`, ... `imageHeight`) is copy-pasted identically in `define()`'s `CustomNode` constructor, `addNode()`, and `deserialize()`. Extract it as a module-level `const BUILT_IN_NODE_PROPS`.

- **Two-pass `onChange` firing is duplicated across four sites** — the pattern of silently setting all custom props then firing `onChange` for each exists independently in the `CustomNode` constructor, `addNode()`'s ready block, the non-headless loop in `deserialize()`, and the drop handler. The `applyCustomProps` helper already exists inside `deserialize()` but is never reused. Extract it to a shared module-level function and call it from all four sites.

- **Async render-wait-resize sequence duplicated in `addNode()` and both drop handlers** — the triple `_waitForRender` / `_resizeNodeAsync` / `_waitForRender` / attach-listeners pattern is copy-pasted across `addNode()`, the custom-node drop path, and the built-in drop path. The built-in drop path is also missing one `_waitForRender` call that the others have — a divergence bug caused by the duplication. Extract to a private `_finalizeAddedNode(node, cell)` helper.

- **Drop handlers in `_attachButtonListeners` reimplement `addNode()` inline** — both drop paths manually build the cell, set attrs, add to graph, and run the async loop, bypassing `addNode()` entirely. This means they also miss the `_findOpenPosition` centering logic. They should call `addNode()` with the computed drop coordinates.

- **`_toggleSidebar` duplicates the DOM operations from `_setSidebarCollapsed`** — icon rotation and collapsed-label visibility are set manually in `_toggleSidebar` instead of delegating to `_setSidebarCollapsed`. Consolidate so `_toggleSidebar` calls `_setSidebarCollapsed`.

- **`serializeNodes()` has two near-identical node serialization blocks** — the headless and non-headless paths produce the same `SerializedNode` shape with only the `id` and `nodeClass` source differing. Extract a `_serializeNodeProps(node)` helper and call it from both paths.

- **`_attachButtonListeners` is a ~250-line god method** — it wires export/import, sidebar collapse, zoom buttons, wheel zoom, context menu, drag-and-drop (two full drop paths), and image upload in a single method. Split into `_attachToolbarListeners`, `_attachCanvasListeners`, and `_attachDropListeners`.

- **`parseInt` applied to already-numeric cell values** — `parseInt(cell.get('imageWidth') || 32)` and `parseInt(cell.get('imageHeight') || 32)` in `_fitNodeToContent` coerce a number through string parsing unnecessarily. `cell.get('imageWidth')` is always stored and retrieved as a number. Remove `parseInt`.

- **`_isMobile()` calls `window.matchMedia(...)` on every invocation** — there is no caching; the media query is evaluated on every pointer event, render step, and sidebar toggle. Cache the `MediaQueryList` as a private field and read `.matches` from it.

- **Dead conditional `portRadius = this._isMobile() ? 6 : 6`** — both branches of this ternary are identical (`6`). This appears in both `addNode()` and `deserialize()` with a `// FIXME` comment. Remove the conditional and use the literal directly, or promote `portRadius` to a configurable field.

- **Inconsistent lambda parameter names for node/edge callbacks** — `addNode()` uses `changedNode`/`movedNode` in its listener lambdas, while `deserialize()` and the drop handlers use the opaque `n`. Standardise on descriptive names throughout.

- **`fd` vs `fieldDef` abbreviation inconsistency** — `fieldDef` is used as the variable name everywhere except inside `applyCustomProps` and the `define()` constructor where it is shortened to `fd`. Use `fieldDef` consistently.

- **`l` and `e` as loop variable names in `_updateConnectionPorts`** — `l` (used as a connected link inside `getUsedSourcePortIds` / `getUsedTargetPortIds`) and `e` (used as a headless edge entry in `_getEdgesForNode`) are opaque and conflict with common event/error conventions. Rename to `connectedLink` and `headlessEdge` respectively.

- **`(this as unknown as DiagramNode)` cast repeated throughout `define()`** — a structural consequence of the dynamic factory pattern, but it fully bypasses strict typing inside the most complex part of the codebase. Introducing a typed `ICustomNode` interface that `CustomNode` can satisfy would eliminate most of these casts.

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
