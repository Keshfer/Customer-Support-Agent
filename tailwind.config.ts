import type { Config } from 'tailwindcss'

const config: Config = {
  content: [
    './src/pages/**/*.{js,ts,jsx,tsx,mdx}',
    './src/components/**/*.{js,ts,jsx,tsx,mdx}',
    './src/app/**/*.{js,ts,jsx,tsx,mdx}',
  ],
  theme: {
    extend: {
      colors: {
        // Dark theme colors
        background: {
          DEFAULT: '#1a1a1a',
          dark: '#0f0f0f',
        },
        // Light grey for agent messages
        agent: {
          DEFAULT: '#e5e5e5',
          light: '#f5f5f5',
        },
        // Orange for user messages
        user: {
          DEFAULT: '#ff6b35',
          dark: '#e55a2b',
        },
        // Header grey tones
        header: {
          DEFAULT: '#2d2d2d',
          light: '#3d3d3d',
        },
      },
    },
  },
  plugins: [],
  darkMode: 'class',
}
export default config
