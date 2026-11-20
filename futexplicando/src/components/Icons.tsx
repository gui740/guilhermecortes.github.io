import React from "react";

/** Ícones SVG desenhados (sem logos). */
export const Icon: React.FC<{ name: string; size?: number; color: string; ink: string }> = ({ name, size = 120, color, ink }) => {
  const s = { width: size, height: size };
  switch (name) {
    case "trophy":
      return (
        <svg {...s} viewBox="0 0 100 100">
          <path d="M28 12h44v20c0 16-10 28-22 28S28 48 28 32z" fill={color} stroke={ink} strokeWidth={5} />
          <path d="M28 18H14c0 14 6 22 16 24M72 18h14c0 14-6 22-16 24" fill="none" stroke={ink} strokeWidth={5} />
          <rect x="44" y="60" width="12" height="14" fill={color} stroke={ink} strokeWidth={5} />
          <rect x="30" y="74" width="40" height="12" rx="2" fill={ink} />
        </svg>
      );
    case "cup":
      return (
        <svg {...s} viewBox="0 0 100 100">
          <path d="M35 10h30l-4 30c-2 10-20 10-22 0z" fill={color} stroke={ink} strokeWidth={5} />
          <path d="M42 48h16l-2 22H44z" fill={color} stroke={ink} strokeWidth={5} />
          <ellipse cx="50" cy="20" rx="20" ry="5" fill="none" stroke={ink} strokeWidth={4} />
          <rect x="30" y="70" width="40" height="18" rx="3" fill={ink} />
        </svg>
      );
    case "ball":
      return (
        <svg {...s} viewBox="0 0 100 100">
          <circle cx="50" cy="50" r="38" fill="#F4EFE6" stroke={ink} strokeWidth={5} />
          <polygon points="50,34 64,44 59,60 41,60 36,44" fill={ink} />
          <path d="M50 34V14M64 44l18-6M59 60l12 16M41 60L29 76M36 44l-18-6" stroke={ink} strokeWidth={4} />
        </svg>
      );
    case "clipboard":
      return (
        <svg {...s} viewBox="0 0 100 100">
          <rect x="18" y="14" width="64" height="78" rx="6" fill={color} stroke={ink} strokeWidth={5} />
          <rect x="36" y="8" width="28" height="14" rx="3" fill={ink} />
          <rect x="26" y="28" width="48" height="56" fill="#F4EFE6" stroke={ink} strokeWidth={3} />
          <path d="M36 44l8 8m0-8l-8 8M58 60a6 6 0 1 0 0.1 0M40 70c8-14 14-16 16-12" stroke={ink} strokeWidth={4} fill="none" />
        </svg>
      );
    case "flag":
      return (
        <svg {...s} viewBox="0 0 100 100">
          <line x1="20" y1="10" x2="20" y2="92" stroke={ink} strokeWidth={6} />
          <path d="M22 14c20-8 30 8 56 0v40c-26 8-36-8-56 0z" fill={color} stroke={ink} strokeWidth={5} />
        </svg>
      );
    case "stadium":
      return (
        <svg {...s} viewBox="0 0 100 100">
          <ellipse cx="50" cy="60" rx="44" ry="22" fill={color} stroke={ink} strokeWidth={5} />
          <ellipse cx="50" cy="60" rx="26" ry="10" fill="#2FA84F" stroke={ink} strokeWidth={4} />
          <path d="M6 60V44c0-12 88-12 88 0v16" fill="none" stroke={ink} strokeWidth={5} />
        </svg>
      );
    case "ship":
      return (
        <svg {...s} viewBox="0 0 100 100">
          <path d="M10 60h80l-12 18H22z" fill={ink} />
          <rect x="30" y="40" width="40" height="20" fill={color} stroke={ink} strokeWidth={4} />
          <rect x="44" y="22" width="10" height="18" fill={ink} />
          <path d="M8 86c10-6 20 6 30 0s20 6 30 0 20 6 30 0" stroke={ink} strokeWidth={4} fill="none" />
        </svg>
      );
    default:
      return null;
  }
};
