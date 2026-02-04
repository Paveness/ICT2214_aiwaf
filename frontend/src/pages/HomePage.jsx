import { Link } from "react-router-dom";

export default function HomePage() {
  return (
    <div className="h-screen bg-gray-900 flex items-center justify-center text-white">
      <div className="text-center space-y-6">
        <h1 className="text-3xl font-bold text-blue-400">
          Neuro-WAF Dashboard
        </h1>

        <p className="text-gray-400">
          Choose how you want to proceed
        </p>

        <div className="flex gap-4 justify-center">
          <Link
            to="/setup"
            className="px-6 py-3 bg-blue-600 hover:bg-blue-700 rounded"
          >
            Setup WAF
          </Link>

          <Link
            to="/login"
            className="px-6 py-3 bg-gray-700 hover:bg-gray-600 rounded"
          >
            Login
          </Link>
        </div>
      </div>
    </div>
  );
}
