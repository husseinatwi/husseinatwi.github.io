import React from "react";
import ReactDOM from "react-dom/client";
import { ArabCoachFunnel } from "./components/ArabCoachFunnel";
import "./index.css";

// Mount the component into a container
// In GHL custom code, this will target the div we create
const rootEl = document.getElementById("arab-coach-funnel-root");
if (rootEl) {
  ReactDOM.createRoot(rootEl).render(
    <React.StrictMode>
      <ArabCoachFunnel />
    </React.StrictMode>
  );
}
