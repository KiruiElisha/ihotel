import frappeUIPreset from 'frappe-ui/tailwind'

/**
 * Brand palette sampled from the iHotel logo: navy #0D3A65 on white.
 *
 * frappe-ui's solid buttons reach for `bg-blue-500` / `bg-red-500` directly
 * rather than a CSS variable, so the brand has to be applied at the palette
 * level too. Repointing `blue` is what makes a stock <Button theme="blue">
 * come out iHotel navy.
 */
export default {
  presets: [frappeUIPreset],
  content: [
    './index.html',
    './src/**/*.{vue,js,ts,jsx,tsx}',
    './node_modules/frappe-ui/src/**/*.{vue,js,ts,jsx,tsx}',
  ],
  theme: {
    extend: {
      colors: {
        blue: {
          50: '#EEF3F8',
          100: '#D6E2EE',
          200: '#AAC3DA',
          300: '#7A9FC3',
          400: '#42709D',
          500: '#0D3A65',
          600: '#0B3157',
          700: '#092848',
          800: '#071E36',
          900: '#051524',
        },
        navy: {
          50: '#EEF3F8',
          100: '#D6E2EE',
          200: '#AAC3DA',
          300: '#7A9FC3',
          400: '#42709D',
          500: '#0D3A65',
          600: '#0B3157',
          700: '#092848',
          800: '#071E36',
          900: '#051524',
        },
        // A warm accent for occupancy figures, kept clear of the navy.
        brass: {
          50: '#FDF7EC',
          100: '#F8E9CB',
          200: '#F0D08F',
          300: '#E5B454',
          400: '#D69A2B',
          500: '#B87E1B',
          600: '#946315',
        },
      },
      fontFamily: {
        sans: ['Inter', 'ui-sans-serif', 'system-ui', 'sans-serif'],
      },
    },
  },
}
