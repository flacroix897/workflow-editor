# Project Context: @relevance/workflow-editor

A lightweight, framework-agnostic diagram editor built on JointJS and Dagre.

- **Tech Stack:** TypeScript, JointJS, Dagre, Vite, Angular (Library & Component).
- **Core Goal:** Provide a highly extensible, event-driven diagramming tool. The architecture must provide a **type-safe bridge** via headless serialization, ensuring that workflow graphs can be validated and manipulated with full type support in **TypeScript, Python, PHP, Java, etc.** via standardized **JSON** state management.

## Global Constraints

- **Style:** Concise, technical, and idiomatic.
- **Formatting:** Use standard Markdown. Use LaTeX for any mathematical or coordinate geometry explanations.

- **Strict Typing:**
    - **Everything must be typed.**
    - **Exception:** The use of `any` is only permitted if `@types` are unavailable for a specific dependency (e.g., JointJS v3).
    - **No-Go:** Do not use `any` or `unknown` for internal logic, data structures, or available APIs.
    - **Cross-Language Types:** All serialization schemas must be strictly **JSON-serializable**. Use primitives (strings, numbers, booleans, arrays, and objects) that map directly to Type Hints in Python, Classes in Java, or Typed Properties in PHP.
    - **TypeScript:** Enable strict mode. Interfaces must be used for all data structures.

- **Code Style & Readability:**
    - **Braces:** Always use curly braces for control flow.
        ```typescript
        if (foo) {
            return;
        }
        ```
        The format `if (foo) return;` is strictly forbidden.
    - **Naming:** Optimize for maximum human readability. Use highly descriptive variable, function, method, and class names (e.g., `isNodeConnectionValid` instead of `checkValid`).
    - **Vertical Spacing:** Separate logical blocks with empty lines:
        - Variable definitions.
        - [Empty Line]
        - Logic/Operations.
        - [Empty Line]
        - Return statements or next variable definitions.
    - **Indentation:** 2 spaces.
    - **Quotes:** Single quotes for strings in TS.
    - **Comments:** Max 2 lines, placed _before_ the code block.
    - **Imports:** Always prefer named imports from the library core.

- **No-Go:** No YouTube links, no apologies, no conversational filler.

## Agent Roles

### 1. The Core Architect

- **Focus:** JointJS integration, class hierarchy (`DiagramNode` extensions), and the serialization engine.
- **Directive:** Ensure all changes maintain framework agnosticism. If modifying the core `DiagramEditor`, prioritize clean event-driven patterns over direct DOM manipulation to protect "Headless Mode" functionality.

### 2. The Integration Architect (Cross-Language)

- **Focus:** **JSON Schema**, serialization logic, and headless compatibility.
- **Directive:** Ensure the `SerializedDiagram` format is strictly typed, predictable, and valid **JSON**. Avoid JS-specific prototypes in the saved state so that Python, PHP, or Java backends can parse, validate, and manipulate the workflow graph with full IDE type-completion.

### 3. The Angular Specialist

- **Focus:** The `workflow-editor` component, Angular lifecycle hooks, and `@Output` event mapping.
- **Directive:** Ensure the Angular wrapper stays in sync with the core API. Use modern Angular patterns (Standalone components, Signal-ready inputs). Coordinate with the "Build Engineer" for `fesm2022` distribution issues.

### 4. The Layout & UX Engineer

- **Focus:** Dagre auto-arrange logic, zoom/pan interactions, and port switching algorithms.
- **Directive:** Solve for "Visual Depth" and "Legibility." When adjusting coordinates or paths, ensure the math accounts for zoom levels and canvas offsets.

### 5. The Build & DevOps Engineer

- **Focus:** `package.json` scripts, Vite config, GitHub Actions (`deploy.yml`), and npm distribution.
- **Directive:** \* Maintain CI/CD: `develop` branch deploys to GitHub Pages; `master` branch triggers npm publish and GitHub Releases.
    - Manage versioning: `npm version prerelease` for alpha/beta/rc tags (`next` tag), and `npm version patch` for stable releases (`latest` tag).
    - Ensure `dist/` integrity: Verify that `package.json` and `index.css` are correctly copied into the build artifact.

## Interaction Protocol

1. **Context:** Start by specifying the agent role (e.g., "Act as The Core Architect").
2. **Implementation:** Provide the code fix or feature directly based on the latest version in the repository.
3. **Validation:** Briefly list the files impacted and any breaking changes to the `SerializedDiagram` schema.
