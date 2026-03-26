import { defineConfig } from "vite";
import { viteSingleFile } from "vite-plugin-singlefile";

export default defineConfig({
  base: "./",
  root: "src",
  plugins: [viteSingleFile()],
  build: {
    outDir: "../dist",
    sourcemap: false,
    minify: "terser",
    terserOptions: {
      keep_classnames: true,
      keep_fnames: true,
      mangle: {
        reserved: [
          "RectangleNode",
          "SquareNode",
          "EllipseNode",
          "CircleNode",
          "DiamondNode",
          "TriangleNode",
          "HexagonNode",
          "PentagonNode",
          "OctagonNode",
          "DiagramNode",
          "DiagramEditor",
          "Edge",
          "PathPoint",
          "EventBus",
        ],
      },
    },
  },
  optimizeDeps: {
    include: ["jointjs", "dagre"],
  },
});
