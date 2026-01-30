// src/App.jsx
import React, { useState, useEffect } from "react";
import { BrowserRouter as Router, Routes, Route, Navigate } from "react-router-dom";
import MainLayout from "./layouts/MainLayout";
import LoginPage from "./pages/LoginPage";

// Pages
import Overview from "./pages/Overview";
import TrafficAnalysis from "./pages/TrafficAnalysis";
import DDoSDashboard from "./pages/DDoSDashboard";
import EventsLog from "./pages/EventsLog";
import HelpPage from "./pages/HelpPage";
import SettingsPage from "./pages/SettingsPage";

function App() {
  // Authentication State
  const [isAuthenticated, setIsAuthenticated] = useState(false);

  // Optional: Check if user was already logged in (persists on refresh)
  useEffect(() => {
    const loggedInUser = localStorage.getItem("user");
    if (loggedInUser) {
      setIsAuthenticated(true);
    }
  }, []);

  const handleLogin = (userData) => {
    setIsAuthenticated(true);
    localStorage.setItem("user", JSON.stringify(userData)); // Save login state
  };

  const handleLogout = () => {
    setIsAuthenticated(false);
    localStorage.removeItem("user");
  };

  return (
    <Router>
      <Routes>
        {/* PUBLIC ROUTE: Login Page */}
        <Route 
          path="/login" 
          element={
            !isAuthenticated ? (
              <LoginPage onLogin={handleLogin} />
            ) : (
              <Navigate to="/" replace />
            )
          } 
        />

        {/* PROTECTED ROUTES */}
        {isAuthenticated ? (
          <>
            {/* We wrap each page individually with MainLayout */}
            <Route path="/" element={<MainLayout><Overview /></MainLayout>} />
            <Route path="/traffic" element={<MainLayout><TrafficAnalysis /></MainLayout>} />
            <Route path="/ddos" element={<MainLayout><DDoSDashboard /></MainLayout>} />
            <Route path="/events" element={<MainLayout><EventsLog /></MainLayout>} />
            <Route path="/settings" element={<MainLayout><SettingsPage /></MainLayout>} />
            <Route path="/support" element={<MainLayout><HelpPage /></MainLayout>} />
            
            {/* Catch-all: Redirect unknown URLs to Dashboard */}
            <Route path="*" element={<Navigate to="/" replace />} />
          </>
        ) : (
          /* If NOT logged in, redirect everything to Login */
          <Route path="*" element={<Navigate to="/login" replace />} />
        )}
      </Routes>
    </Router>
  );
}

export default App;