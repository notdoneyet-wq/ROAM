import type { Config } from "tailwindcss";

const config: Config = {
  content: [
    "./src/pages/**/*.{js,ts,jsx,tsx,mdx}",
    "./src/components/**/*.{js,ts,jsx,tsx,mdx}",
    "./src/app/**/*.{js,ts,jsx,tsx,mdx}",
  ],
  theme: {
    extend: {
      colors: {
        roam: {
          ivory: {
            DEFAULT: '#FEFDF8',
            dark: '#FAF7F0',
          },
          green: {
            DEFAULT: '#1B4332',
            light: '#2D6A4F',
          },
          ink: {
            DEFAULT: '#1A1A2E',
            light: '#2C2C3E',
          },
          terracotta: {
            DEFAULT: '#C17F59',
            light: '#D4956A',
          },
          gold: {
            DEFAULT: '#D4A853',
            light: '#E5B96B',
          },
          beige: {
            DEFAULT: '#E8DED1',
            dark: '#D5C9B8',
          },
          gray: {
            DEFAULT: '#C9BFA8',
          },
          blue: {
            DEFAULT: '#4A90D9',
          }
        }
      },
      fontFamily: {
        serif: ['var(--font-playfair)', 'serif'],
        sans: ['var(--font-dmsans)', 'sans-serif'],
        mono: ['var(--font-ibm-plex-mono)', 'monospace'],
      },
      backgroundImage: {
        'topo-pattern': 'var(--topo-pattern)',
      }
    },
  },
  plugins: [],
};
export default config;
