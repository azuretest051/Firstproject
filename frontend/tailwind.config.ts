import type { Config } from "tailwindcss";

const config: Config = {
  darkMode: "class",
  content: [
    "./src/pages/**/*.{js,ts,jsx,tsx,mdx}",
    "./src/components/**/*.{js,ts,jsx,tsx,mdx}",
    "./src/app/**/*.{js,ts,jsx,tsx,mdx}",
  ],
  theme: {
    extend: {
      colors: {
        "on-surface": "#e2e2e6",
        error: "#ffb4ab",
        "on-error-container": "#ffdad6",
        "on-tertiary": "#5e1700",
        "surface-dim": "#111317",
        "on-secondary": "#472a00",
        "surface-bright": "#37393d",
        "secondary-fixed-dim": "#ffb95f",
        "inverse-primary": "#ae3115",
        "surface-container-high": "#282a2d",
        "secondary-fixed": "#ffddb8",
        "secondary-container": "#ee9800",
        "on-tertiary-fixed-variant": "#7f2a0d",
        "on-secondary-container": "#5b3800",
        "on-secondary-fixed-variant": "#653e00",
        "surface-container-lowest": "#0c0e11",
        "inverse-on-surface": "#2f3034",
        secondary: "#ffb95f",
        "surface-container-highest": "#333538",
        primary: "#ffb4a3",
        "on-tertiary-fixed": "#3a0b00",
        "on-primary": "#630f00",
        "on-primary-container": "#661000",
        "on-secondary-fixed": "#2a1700",
        "primary-fixed": "#ffdad2",
        "error-container": "#93000a",
        "tertiary-fixed-dim": "#ffb59e",
        "surface-tint": "#ffb4a3",
        "on-error": "#690005",
        "inverse-surface": "#e2e2e6",
        "primary-container": "#ff6b4a",
        "primary-fixed-dim": "#ffb4a3",
        "tertiary-container": "#eb7a56",
        tertiary: "#ffb59e",
        outline: "#a88a83",
        "surface-container-low": "#1a1c1f",
        "on-primary-fixed": "#3d0600",
        surface: "#111317",
        "on-surface-variant": "#e1bfb8",
        "outline-variant": "#59413c",
        "tertiary-fixed": "#ffdbd0",
        "on-primary-fixed-variant": "#8c1900",
        "surface-container": "#1e2023",
        "on-background": "#e2e2e6",
        "on-tertiary-container": "#611800",
        "surface-variant": "#333538",
        background: "#111317",
      },
      borderRadius: {
        DEFAULT: "0.25rem",
        lg: "0.5rem",
        xl: "0.75rem",
        "2xl": "1rem",
        full: "9999px",
      },
      spacing: {
        "space-xl": "2.5rem",
        gutter: "1rem",
        "space-sm": "0.5rem",
        "margin-lg": "3rem",
        "margin-md": "2rem",
        "space-md": "1rem",
        margin: "1rem",
        "space-xs": "0.25rem",
        "space-lg": "1.5rem",
        "gutter-md": "1.5rem",
      },
      fontFamily: {
        sans: ["var(--font-plus-jakarta)", "system-ui", "sans-serif"],
      },
      fontSize: {
        "body-sm": [
          "12px",
          { lineHeight: "16px", letterSpacing: "0.01em", fontWeight: "400" },
        ],
        "headline-md": [
          "22px",
          { lineHeight: "28px", letterSpacing: "-0.015em", fontWeight: "700" },
        ],
        "label-sm": [
          "11px",
          { lineHeight: "14px", letterSpacing: "0.04em", fontWeight: "700" },
        ],
        "headline-xl": [
          "40px",
          { lineHeight: "48px", letterSpacing: "-0.03em", fontWeight: "800" },
        ],
        "label-lg": [
          "14px",
          { lineHeight: "20px", letterSpacing: "0.01em", fontWeight: "600" },
        ],
        "headline-sm": [
          "18px",
          { lineHeight: "24px", letterSpacing: "-0.01em", fontWeight: "600" },
        ],
        "body-md": [
          "14px",
          { lineHeight: "20px", letterSpacing: "0em", fontWeight: "400" },
        ],
        "label-md": [
          "12px",
          { lineHeight: "16px", letterSpacing: "0.02em", fontWeight: "600" },
        ],
        "body-lg": [
          "16px",
          { lineHeight: "24px", letterSpacing: "-0.005em", fontWeight: "400" },
        ],
        "headline-lg": [
          "32px",
          { lineHeight: "40px", letterSpacing: "-0.02em", fontWeight: "700" },
        ],
      },
      keyframes: {
        "fade-up": {
          "0%": { opacity: "0", transform: "translateY(12px)" },
          "100%": { opacity: "1", transform: "translateY(0)" },
        },
        "glow-pulse": {
          "0%, 100%": { opacity: "0.45" },
          "50%": { opacity: "0.85" },
        },
      },
      animation: {
        "fade-up": "fade-up 0.55s ease-out both",
        "glow-pulse": "glow-pulse 3.2s ease-in-out infinite",
      },
    },
  },
  plugins: [],
};

export default config;
