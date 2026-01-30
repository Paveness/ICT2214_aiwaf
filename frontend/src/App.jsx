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
import DDoSDashboard from "./pages/DDoSDashboard";
import EventsLog from "./pages/EventsLog";
import HelpPage from "./pages/HelpPage";
import SettingsPage from "./pages/SettingsPage";

function App() {
  return (
    <Router>
      <MainLayout>
        <Routes>
          {/* Dashboard Home */}
          <Route path="/" element={<Overview />} />

          {/* Traffic Analysis Page */}
          <Route path="/traffic" element={<TrafficAnalysis />} />

          {/* Security Pages */}
          <Route path="/ddos" element={<DDoSDashboard />} />
          <Route path="/events" element={<EventsLog />} />

          {/* Settings & Support */}
          <Route path="/settings" element={<SettingsPage />} />
          <Route path="/support" element={<HelpPage />} />

          {/* Catch-all redirect */}
          <Route path="*" element={<Navigate to="/" replace />} />
        </Routes>
      </MainLayout>
    </Router>
  );
}

export default App;