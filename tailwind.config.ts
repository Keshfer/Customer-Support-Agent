import type { Config } from 'tailwindcss'

/**
 * Tailwind CSS configuration for Customer Support AI Agent
 * 
 * This configuration sets up a dark theme with a custom color palette
 * matching the finAI.png design reference:
 * - Dark backgrounds for the main UI
 * - Light grey for agent message bubbles
 * - Orange for user message bubbles
 * - Grey tones for header elements
 */
const config: Config = {
  content: [
    './src/pages/**/*.{js,ts,jsx,tsx,mdx}',
    './src/components/**/*.{js,ts,jsx,tsx,mdx}',
    './src/app/**/*.{js,ts,jsx,tsx,mdx}',
  ],
  theme: {
    extend: {
      colors: {
        // Dark theme background colors
        // Used for main app background and dark UI elements
        background: {
          DEFAULT: '#1a1a1a', // Main dark background
          dark: '#0f0f0f',     // Darker variant for contrast
        },
        // Light blue colors for agent messages
        // Agent messages appear as light blue bubbles, left-aligned
        agent: {
          DEFAULT: '#35c9ff', // Main agent message bubble color
          light: '#54cffd',    // Lighter variant for hover states
          text: '#1a1a1a',     // Dark text on light agent bubbles
        },
        // Orange colors for user messages
        // User messages appear as orange rounded rectangles, right-aligned
        user: {
          DEFAULT: '#ff6b35', // Main user message bubble color
          dark: '#e55a2b',    // Darker variant for hover/pressed states
          text: '#ffffff',     // White text on orange user bubbles
        },
        // Header grey tones
        // Used for header bar and navigation elements
        header: {
          DEFAULT: '#2d2d2d', // Main header background
          light: '#3d3d3d',   // Lighter variant for interactive elements
          text: '#ffffff',     // White text on header
        },
        // Additional utility colors
        text: {
          primary: '#ffffff',   // Primary text color (white)
          secondary: '#a0a0a0', // Secondary text color (grey)
          muted: '#666666',     // Muted text color
        },
      },
    },
  },
  plugins: [],
  // Enable dark mode using class strategy
  // The 'dark' class is applied to the html element in layout.tsx
  darkMode: 'class',
}
export default config
