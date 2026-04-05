# @relevance/workflow-editor

A lightweight, framework-agnostic diagram editor built on JointJS.

**[Live Demo](https://demo.relevance.io)**

---

## Features

- **Framework agnostic** — works with vanilla JS/TS; first-class wrappers for Angular, React, and Vue
- **Event-driven API** — subscribe to node, edge, and selection lifecycle events
- **Built-in node shapes** — Rectangle, Square, Ellipse, Circle, Diamond, Triangle, Hexagon, Pentagon, Octagon
- **Custom node types** — define shapes with typed schemas, default options, and change handlers via `DiagramNode.define()`
- **Edge styling** — configurable line color, width, style (solid/dashed/dotted), arrow markers, and connector routing (elbow/straight/curved)
- **Auto port switching** — edges automatically connect to the nearest port as nodes are moved
- **Auto arrange** — one-call Dagre-powered layout with `autoArrange()`
- **Zoom and pan** — mouse wheel zoom, click-and-drag pan, zoom to fit, and keyboard shortcuts
- **Keyboard shortcuts** — arrow keys to nudge, Delete/Backspace to remove, Ctrl+C/V to copy/paste, Tab to cycle selection, +/- to zoom, 0 to reset zoom, Enter/F2 to edit
- **Duplicate** — duplicate nodes via the properties panel, context menu, or Ctrl+V after Ctrl+C
- **Touch support** — single-finger pan and two-finger pinch-to-zoom on mobile
- **Properties panel** — built-in sidebar for editing node and edge properties, including image upload
- **Headless mode** — build diagrams programmatically without a DOM, then render later
- **Serialize / deserialize** — save and restore full diagram state as JSON, including node type definitions
- **Import / export** — download and re-upload diagrams as JSON files

### Roadmap

- Additional validators (min, max, choices, etc.)
- Node trees — programmatically traverse the workflow graph in any language
  - Circular tree support
- More keyboard shortcuts
- Path finding improvements
- UX improvements — mobile/tablet UX, improved context menu

---

## SDK Documentation

| SDK | README |
| --- | --- |
| Angular | [sdk/angular/README.md](sdk/angular/README.md) |

---

## Installation

### npm

```bash
npm install @relevance/workflow-editor
```

### CDN

```html
<link rel="stylesheet" href="https://unpkg.com/@relevance/workflow-editor/index.css" />
<div id="editor" style="width: 100%; height: 600px;"></div>
<script type="module">
  import { DiagramEditor, RectangleNode } from "https://unpkg.com/@relevance/workflow-editor/index.es.js";

  const editor = new DiagramEditor(document.getElementById("editor"));
  const node = new RectangleNode({ label: "Hello World" });
  await editor.addNode(node);
</script>
```

---

## Usage

### Vanilla JS / TypeScript

```typescript
import { DiagramEditor, RectangleNode, DiamondNode } from "@relevance/workflow-editor";
import "@relevance/workflow-editor/index.css";

const editor = new DiagramEditor(document.getElementById("editor")!);

const start    = new RectangleNode({ label: "Start",     backgroundColor: "#d4edda" });
const decision = new DiamondNode({   label: "Decision?" });
const end      = new RectangleNode({ label: "End",       backgroundColor: "#f8d7da" });

await editor.addNode(start);
await editor.addNode(decision);
await editor.addNode(end);

start.connectTo(decision);
decision.connectTo(end);

await editor.autoArrange();

// Save
editor.on("change", () => {
  localStorage.setItem("diagram", editor.serialize());
});

// Restore
const saved = localStorage.getItem("diagram");
if (saved) await editor.deserialize(saved);
```

### Headless mode

Create and manipulate a diagram without a DOM container, then render it later:

```typescript
import { DiagramEditor, RectangleNode, EllipseNode } from "@relevance/workflow-editor";

const editor = new DiagramEditor(); // no container → headless
editor.registerBuiltInNodes();

const start   = await editor.addNode(new EllipseNode({    label: "Start" }));
const process = await editor.addNode(new RectangleNode({ label: "Process" }));
start.connectTo(process);

// Render into the DOM when ready
await editor.render(document.getElementById("editor")!);
```

---

## API Reference

### `DiagramEditor`

| Method / Property | Returns | Description |
| --- | --- | --- |
| `new DiagramEditor(container?)` | `DiagramEditor` | Create an editor. Omit `container` for headless mode |
| `render(container)` | `Promise<DiagramEditor>` | Mount a headless editor into a DOM element |
| `addNode(node, x?, y?)` | `Promise<DiagramNode>` | Add a node. `x`/`y` are canvas-area pixel coordinates |
| `removeNode(node)` | `void` | Remove a node and its connected edges |
| `clear()` | `DiagramEditor` | Remove all nodes and edges |
| `getNodes()` | `DiagramNode[]` | All nodes on the canvas |
| `getEdges()` | `Edge[]` | All edges on the canvas |
| `serialize(includeTypes?)` | `string` | Serialize to JSON string (includes type definitions by default) |
| `serializeNodes()` | `{ nodes, edges }` | Serialize only nodes and edges |
| `serializeTypes()` | `SerializedNodeType[]` | Serialize only registered node type definitions |
| `deserialize(json)` | `Promise<DiagramEditor>` | Restore from JSON. Re-registers node types if present |
| `registerNodeType(label, NodeClass, name?)` | `void` | Register a custom node type |
| `registerBuiltInNodes()` | `void` | Register all nine built-in shapes |
| `clearRegisteredNodes()` | `DiagramEditor` | Unregister all node types |
| `autoArrange()` | `Promise<DiagramEditor>` | Dagre auto-layout |
| `zoomToFit()` | `DiagramEditor` | Zoom to fit all content |
| `zoomIn(factor?)` | `DiagramEditor` | Zoom in |
| `zoomOut(factor?)` | `DiagramEditor` | Zoom out |
| `zoomReset()` | `DiagramEditor` | Reset zoom to 1:1 |
| `getZoomLevel()` | `number` | Current zoom scale |
| `centerContent()` | `DiagramEditor` | Center the canvas |
| `panTo(x, y)` | `DiagramEditor` | Pan to a position |
| `clearSelection()` | `DiagramEditor` | Clear current selection |
| `getSelectedItem()` | `DiagramNode \| Edge \| null` | Currently selected item |
| `setAutoPortSwitching(enabled)` | `DiagramEditor` | Toggle automatic port switching |

### `DiagramNode`

| Property / Method | Type | Description |
| --- | --- | --- |
| `id` | `string \| null` | Unique identifier |
| `x`, `y` | `number \| undefined` | Canvas position (undefined in headless mode if unset) |
| `width`, `height` | `number` | Read-only dimensions |
| `label` | `string` | Display label |
| `labelColor` | `string` | Label text color |
| `labelFontSize` | `number` | Label font size (%) |
| `description` | `string` | Secondary text below label |
| `descriptionColor` | `string` | Description text color |
| `backgroundColor` | `string` | Fill color |
| `borderColor` | `string` | Border color |
| `borderWidth` | `number` | Border width in pixels |
| `imageUrl` | `string` | Icon/image URL or data URI |
| `imageWidth`, `imageHeight` | `number` | Image dimensions in pixels |
| `moveTo(x, y)` | `DiagramNode` | Move to absolute position |
| `moveBy(dx, dy)` | `DiagramNode` | Move by relative offset |
| `toFront()` | `DiagramNode` | Bring to front |
| `toBack()` | `DiagramNode` | Send to back |
| `select()` | `DiagramNode` | Select this node |
| `deselect()` | `DiagramNode` | Deselect this node |
| `remove()` | `void` | Remove from canvas |
| `connectTo(target, sourcePort?, targetPort?)` | `Edge \| null` | Connect to another node |
| `getEdges()` | `Edge[]` | All connected edges |
| `getIncomingEdges()` | `Edge[]` | Edges where this node is the target |
| `getOutgoingEdges()` | `Edge[]` | Edges where this node is the source |
| `getCustomProperty(key)` | `any` | Get a custom property value |
| `setCustomProperty(key, value)` | `void` | Set a custom property value |
| `getSchema()` | `Schema` | Get the custom properties schema |

### `Edge`

| Property / Method | Type | Description |
| --- | --- | --- |
| `id` | `string` | Unique identifier |
| `source`, `target` | `DiagramNode` | Connected nodes |
| `label` | `string` | Edge label |
| `labelColor` | `string` | Label text color |
| `labelFontSize` | `number` | Label font size (%) |
| `lineColor` | `string` | Line color |
| `lineWidth` | `number` | Line width in pixels |
| `lineStyle` | `'solid' \| 'dashed' \| 'dotted'` | Line style |
| `sourceArrow` | `'none' \| 'classic' \| 'block'` | Arrow at source end |
| `targetArrow` | `'none' \| 'classic' \| 'block'` | Arrow at target end |
| `connectorType` | `'elbow' \| 'straight' \| 'curved'` | Routing style |
| `description` | `string` | Edge description |
| `sourcePort`, `targetPort` | `number \| null` | Pinned port index |
| `select()` | `Edge` | Select this edge |
| `deselect()` | `Edge` | Deselect this edge |
| `remove()` | `void` | Remove from canvas |
| `addPathPoint(x, y)` | `PathPoint` | Add a bend point to the edge path |
| `getPathPoints()` | `PathPoint[]` | Get all bend points |

### Events

```typescript
editor.on("change",           ()     => {});
editor.on("node:add",         (node) => {});
editor.on("node:remove",      (node) => {});
editor.on("node:change",      (node) => {});
editor.on("node:move",        (node) => {});
editor.on("edge:add",         (edge) => {});
editor.on("edge:remove",      (edge) => {});
editor.on("edge:change",      (edge) => {});
editor.on("selection:change", (item) => {});
```

### Built-in node types

| Class | Shape |
| --- | --- |
| `RectangleNode` | Rectangle |
| `SquareNode` | Square |
| `EllipseNode` | Ellipse |
| `CircleNode` | Circle |
| `DiamondNode` | Diamond |
| `TriangleNode` | Triangle |
| `HexagonNode` | Hexagon |
| `PentagonNode` | Pentagon |
| `OctagonNode` | Octagon |

### Custom node types

Use `DiagramNode.define()` to create custom node types with a schema and change handlers:

```typescript
import { DiagramNode, RectangleNode } from "@relevance/workflow-editor";

const TaskNode = (DiagramNode as any).define(RectangleNode, {
  defaults: { label: "New Task", backgroundColor: "#f0f8ff" },
  schema: {
    assignee: { label: "Assignee", type: "text", default: "" },
    effort: { label: "Effort", type: "number", default: 1, min: 1, max: 10 },
    done: {
      label: "Done",
      type: "boolean",
      default: false,
      // onChange is called whenever this property changes.
      // Not serialized — re-register the type with the same schema after import.
      onChange: (node, value) => {
        node.backgroundColor = value ? "#d4edda" : "#f0f8ff";
        node.borderColor     = value ? "#28a745" : "#adb5bd";
      },
    },
    priority: {
      label: "Priority",
      type: "choice",
      default: "medium",
      choices: { low: "Low", medium: "Medium", high: "High" },
    },
  },
  // Optional: restrict which built-in props appear in the properties panel.
  // Omit entirely to show all. Pass [] to hide all.
  visibleProps: ["label", "backgroundColor", "borderColor"],
  // Optional: which prop Enter/F2 focuses in the properties panel.
  editProp: "label",
});

editor.registerNodeType("TaskNode", TaskNode, "Task");
const task = await editor.addNode(new TaskNode({ label: "Review PR" }));
task.setCustomProperty("assignee", "alice");
```

### Serialization types

```typescript
// Built-in types serialize as a plain string (their nodeClass name).
// Custom types include their full definition.
// serialize/deserialize/onChange fields are stripped — re-register the type
// with the same handlers after import to restore them.
type SerializedNodeType =
  | string
  | {
      nodeClass: string;
      name?: string;
      baseClass: string;
      defaultOptions: NodeOptions;
      schema: Schema;
      visibleProps?: BuiltInNodeProp[];
      editProp?: string;
    };

interface SerializedDiagram {
  nodes: SerializedNode[];
  edges: SerializedEdge[];
  nodeTypes?: SerializedNodeType[]; // omitted when serialize(false) is called
}
```

### `FieldDefinition` reference

| Field | Type | Description |
| --- | --- | --- |
| `label` | `string` | Display name in the properties panel |
| `type` | `'text' \| 'number' \| 'textarea' \| 'boolean' \| 'choice' \| 'color' \| 'object'` | Input type. `object` fields are not shown in the panel |
| `default` | `any` | Initial value |
| `choices` | `Record<string, string>` | Options map for `choice` type (`{ value: label }`) |
| `min`, `max` | `number` | Bounds for `number` type |
| `visible` | `boolean` | `false` hides the field from the properties panel |
| `readonly` | `boolean` | Renders the field as disabled |
| `serialize` | `(value: any, node: DiagramNode) => any` | Transform value before serialization. Not written to JSON |
| `deserialize` | `(raw: any, node: DiagramNode) => any` | Transform value after deserialization. Not written to JSON |
| `onChange` | `(node: DiagramNode, newValue: any, oldValue: any) => void` | Called after the value changes. Not written to JSON |

### `BuiltInNodeProp`

The `visibleProps` array accepts any combination of:

```typescript
type BuiltInNodeProp =
  | "label" | "labelColor" | "labelFontSize"
  | "description" | "descriptionColor"
  | "backgroundColor" | "borderColor"
  | "imageUrl" | "imageWidth" | "imageHeight";
```

---

## Contributing

### Prerequisites

- Node.js 24+
- npm

### Setup

```bash
git clone https://github.com/relevance-io/workflow-editor.git
cd workflow-editor
npm run install:all  # for development
npm run ci:all       # for CI
```

### Build

```bash
# Build everything (lib, demo app, Angular component)
npm run build

# Build individually
npm run build:lib      # core library → dist/
npm run build:app      # demo app → dist/
npm run build:angular  # Angular component → dist/angular/
```

### Development server

```bash
npm start
# Opens http://localhost:5173 with hot reload
```

### Pull requests

1. Fork the repository
2. Create a feature branch
3. Push to your branch and open a pull request

---

## License

[MIT](LICENSE)
