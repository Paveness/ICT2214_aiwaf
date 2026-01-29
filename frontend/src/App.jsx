// src/App.jsx
import React from "react";
import {
  BrowserRouter as Router,
  Routes,
  Route,
  Navigate,
} from "react-router-dom";
import MainLayout from "./layouts/MainLayout";
import Overview from "./pages/Overview";
import TrafficAnalysis from "./pages/TrafficAnalysis";

// Placeholder components for pages we haven't built yet
const Placeholder = ({ title }) => (
  <div className="p-10 text-gray-500 text-center border-2 border-dashed border-gray-300 rounded-lg h-96 flex items-center justify-center">
    <h2 className="text-2xl font-semibold">TEMP</h2>
  </div>
);

function App() {
  return (
    <Router>
      <MainLayout>
        <Routes>
          {/* Dashboard Home */}
          <Route path="/" element={<Overview />} />

          {/* Traffic Analysis Page */}
          <Route path="/traffic" element={<TrafficAnalysis />} />

          {/* Placeholders for other links */}
          <Route path="/ddos" element={<Placeholder title="DDoS Monitor" />} />
          <Route path="/events" element={<Placeholder title="Event Logs" />} />
          <Route
            path="/support"
            element={<Placeholder title="Support Center" />}
          />

          {/* Catch-all redirect */}
          <Route path="*" element={<Navigate to="/" replace />} />
        </Routes>
      </MainLayout>
    </Router>
  );
}

export default App;
