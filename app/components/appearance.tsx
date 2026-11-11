"use client";
import { useState } from "react";
export function Appearance({ initial }: { initial: "light" | "dark" }) {
  const [theme, setTheme] = useState(initial);
  return (
    <button
      type="button"
      className="icon-button"
      aria-label={`Use ${theme === "light" ? "dark" : "light"} theme`}
      onClick={() => {
        const next = theme === "light" ? "dark" : "light";
        document.documentElement.dataset.theme = next;
        document.cookie = `outcomia_canton_theme=${next}; Path=/; Max-Age=31536000; SameSite=Lax`;
        setTheme(next);
      }}
    >
      <svg
        viewBox="0 0 24 24"
        aria-hidden="true"
        fill="none"
        stroke="currentColor"
        strokeWidth="1.5"
      >
        <circle cx="12" cy="12" r="8" />
        <path d="M12 4a8 8 0 0 1 0 16Z" fill="currentColor" />
      </svg>
    </button>
  );
}
