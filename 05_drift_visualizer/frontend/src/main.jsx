import { StrictMode } from "react";
import { createRoot } from "react-dom/client";
import DriftVisualizer from "./DriftVisualizer.jsx";

createRoot(document.getElementById("root")).render(
  <StrictMode>
    <DriftVisualizer />
  </StrictMode>
);
