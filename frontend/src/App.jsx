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
  const [isAuthenticated, setIsAuthenticated] = useState(false);
  
  // 1. NEW: Add a loading state to prevent premature redirects
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    // Check local storage immediately when app mounts
    const loggedInUser = localStorage.getItem("user");
    if (loggedInUser) {
      setIsAuthenticated(true);
    }
    // 2. NEW: Mark loading as done
    setIsLoading(false);
  }, []);

  const handleLogin = (userData) => {
    setIsAuthenticated(true);
    localStorage.setItem("user", JSON.stringify(userData));
  };

  // 3. NEW: Show nothing (or a spinner) while checking auth
  if (isLoading) {
    return <div className="h-screen bg-gray-900 flex items-center justify-center text-white">Loading...</div>;
  }

  return (
    <Router>
      <Routes>
        {/* PUBLIC ROUTE */}
        <Route 
          path="/login" 
          element={!isAuthenticated ? <LoginPage onLogin={handleLogin} /> : <Navigate to="/" replace />} 
        />

        {/* PROTECTED ROUTES */}
        {isAuthenticated ? (
          <>
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
          /* Use 'replace' to prevent browser history stack buildup */
          <Route path="*" element={<Navigate to="/login" replace />} />
        )}
      </Routes>
    </Router>
  );
}

export default App;