import { useEffect, useRef, useState } from "react";
import { Navigate, useLocation } from "react-router-dom";

export default function RequireAuth({ children }) {
  const location = useLocation();
  const ran = useRef(false);

  const [loading, setLoading] = useState(true);
  const [ok, setOk] = useState(false);

  useEffect(() => {
    if (ran.current) return;   // ✅ prevents StrictMode double-run
    ran.current = true;

    fetch("/api/auth/check", {
      credentials: "include",
    })
      .then((r) => setOk(r.ok))
      .finally(() => setLoading(false));
  }, []);

  if (loading) return null; // or spinner

  if (!ok) {
    return <Navigate to="/login" replace state={{ from: location }} />;
  }

  return children;
}
