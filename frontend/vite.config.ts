import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";

export default defineConfig({
  plugins: [react()],
  build: {
    rollupOptions: {
      output: {
        manualChunks(id) {
          if (!id.includes("node_modules")) {
            return undefined;
          }
          if (/node_modules[\\/](react|react-dom|scheduler)[\\/]/.test(id)) {
            return "vendor-react";
          }
          if (id.includes("recharts") || /node_modules[\\/]d3-/.test(id)) {
            return "vendor-charts";
          }
          if (id.includes("cytoscape") || id.includes("react-cytoscapejs")) {
            return "vendor-graph";
          }
          if (id.includes("lucide-react")) {
            return "vendor-icons";
          }
          return undefined;
        }
      }
    }
  }
});
