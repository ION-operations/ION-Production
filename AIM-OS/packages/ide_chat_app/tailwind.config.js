/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        // Base colors
        border: 'hsl(214.3 31.8% 91.4%)',
        background: 'hsl(0 0% 100%)',
        foreground: 'hsl(222.2 47.4% 11.2%)',
        // Neumorphic design colors
        neumorphic: {
          light: '#f0f0f3',
          dark: '#2a2a2a',
          shadow: '#d1d9e6',
          highlight: '#ffffff'
        },
        // Theme variations
        space: {
          primary: '#0a0a0a',
          secondary: '#1a1a2e',
          accent: '#16213e',
          text: '#e94560'
        },
        cyberpunk: {
          primary: '#0d1117',
          secondary: '#161b22',
          accent: '#21262d',
          text: '#00ff88'
        },
        matrix: {
          primary: '#000000',
          secondary: '#001100',
          accent: '#003300',
          text: '#00ff00'
        },
        aurora: {
          primary: '#0f0f23',
          secondary: '#1a1a2e',
          accent: '#16213e',
          text: '#e94560'
        }
      },
      fontFamily: {
        'mono': ['JetBrains Mono', 'Fira Code', 'monospace'],
        'sans': ['Inter', 'system-ui', 'sans-serif']
      },
      animation: {
        'wave': 'wave 2s ease-in-out infinite',
        'pulse-slow': 'pulse 3s cubic-bezier(0.4, 0, 0.6, 1) infinite',
        'float': 'float 6s ease-in-out infinite',
        'glow': 'glow 2s ease-in-out infinite alternate'
      },
      keyframes: {
        wave: {
          '0%, 100%': { transform: 'translateY(0px)' },
          '50%': { transform: 'translateY(-10px)' }
        },
        float: {
          '0%, 100%': { transform: 'translateY(0px) rotate(0deg)' },
          '33%': { transform: 'translateY(-20px) rotate(1deg)' },
          '66%': { transform: 'translateY(-10px) rotate(-1deg)' }
        },
        glow: {
          '0%': { boxShadow: '0 0 5px rgba(59, 130, 246, 0.5)' },
          '100%': { boxShadow: '0 0 20px rgba(59, 130, 246, 0.8)' }
        }
      },
      boxShadow: {
        'neumorphic': '20px 20px 60px #d1d9e6, -20px -20px 60px #ffffff',
        'neumorphic-inset': 'inset 20px 20px 60px #d1d9e6, inset -20px -20px 60px #ffffff',
        'neumorphic-dark': '20px 20px 60px #1a1a1a, -20px -20px 60px #2a2a2a',
        'neumorphic-inset-dark': 'inset 20px 20px 60px #1a1a1a, inset -20px -20px 60px #2a2a2a'
      }
    },
  },
  plugins: [],
}
