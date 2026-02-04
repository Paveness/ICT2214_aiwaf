import React, { useState } from "react";
import { useNavigate } from "react-router-dom";
import { Lock, User, Hexagon, ArrowRight } from "lucide-react";

const LoginPage = ({ onLogin }) => {
  const [username, setUsername] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState("");

  const navigate = useNavigate();

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError("");

    try {
      const response = await fetch("/api/login", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      credentials: "include", // 👈 important
      body: JSON.stringify({ username, password }),
    });

    if (!response.ok) {
      throw new Error("Login failed");
    }
    navigate("/dashboard", { replace: true });

    } catch (err) {
      setError(err.message || "Network error");
    }
  };

  return (
    <div className="min-h-screen bg-gray-900 flex items-center justify-center p-4">
      <div className="bg-white rounded-2xl shadow-2xl w-full max-w-md overflow-hidden">
        {/* Header Section */}
        <div className="bg-blue-600 p-8 text-center">
          <div className="flex justify-center mb-4">
            <div className="bg-white p-3 rounded-xl">
              <Hexagon className="text-blue-600" size={32} />
            </div>
          </div>
          <h1 className="text-2xl font-bold text-white tracking-wide">NEURO-WAF</h1>
          <p className="text-blue-100 text-sm mt-2">Next-Gen AI Security Defense</p>
        </div>

        {/* Form Section */}
        <div className="p-8">
          <h2 className="text-xl font-bold text-gray-800 mb-6 text-center">
            Welcome Back
          </h2>

          {error && (
            <div className="mb-4 p-3 bg-red-100 border border-red-200 text-red-700 text-sm rounded-lg text-center font-semibold">
              {error}
            </div>
          )}

          <form onSubmit={handleSubmit} className="space-y-4">
            <div>
              <label className="block text-xs font-bold text-gray-700 uppercase mb-1">
                Username
              </label>
              <div className="relative">
                <User
                  className="absolute left-3 top-1/2 -translate-y-1/2 text-gray-400"
                  size={18}
                />
                <input
                  type="text"
                  required
                  value={username}
                  onChange={(e) => setUsername(e.target.value)}
                  className="w-full pl-10 pr-4 py-3 rounded-lg border border-gray-200 focus:outline-none focus:ring-2 focus:ring-blue-500 transition-all"
                  placeholder="Enter your username"
                />
              </div>
            </div>

            <div>
              <label className="block text-xs font-bold text-gray-700 uppercase mb-1">
                Password
              </label>
              <div className="relative">
                <Lock
                  className="absolute left-3 top-1/2 -translate-y-1/2 text-gray-400"
                  size={18}
                />
                <input
                  type="password"
                  required
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                  className="w-full pl-10 pr-4 py-3 rounded-lg border border-gray-200 focus:outline-none focus:ring-2 focus:ring-blue-500 transition-all"
                  placeholder="••••••••"
                />
              </div>
            </div>

            <button
              type="submit"
              className="w-full bg-gray-900 text-white font-bold py-3 rounded-lg hover:bg-black transition-colors flex items-center justify-center gap-2 mt-2"
            >
              Sign In to Dashboard
              <ArrowRight size={18} />
            </button>
          </form>

          <div className="mt-6 text-center text-sm text-gray-500">
            New to Neuro-WAF?{" "}
            <button
              onClick={() => navigate("/setup")}
              className="text-blue-600 font-bold hover:underline"
              type="button"
            >
              Setup
            </button>
          </div>
        </div>
      </div>
    </div>
  );
};

export default LoginPage;
