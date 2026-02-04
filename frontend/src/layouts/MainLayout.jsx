// src/layouts/MainLayout.jsx
import React from "react";
import { Outlet } from "react-router-dom";
import Sidebar from "../components/common/Sidebar";
import Header from "../components/common/Header";

export default function MainLayout() {
  return (
    <div className="flex h-screen bg-gray-50 overflow-hidden">
      {/* 1. Fixed Sidebar */}
      <Sidebar />

      {/* 2. Main Content Area */}
      <div className="flex-1 flex flex-col min-w-0">
        <Header />

        {/* Scrollable Page Content */}
        <main className="flex-1 overflow-y-auto p-6 scroll-smooth">
          <Outlet />
        </main>
      </div>
    </div>
  );
}
