/**
 * japandi-starter - Tailwind preset
 * Consumes the same tokens as tokens.json.
 * GENERATED - do not edit by hand. Edit tokens.json, then run:
 *   python3 tools/build-tokens.py
 *
 * Usage:
 *   // tailwind.config.js
 *   module.exports = {
 *     presets: [require('./tailwind.preset.js')],
 *     content: ['./src/*.{html,js,jsx,ts,tsx,vue,svelte}'],
 *   }
 *
 * Colors are literal values (not var() references) so opacity modifiers
 * like bg-sage/50 keep working.
 */

/** @type {import('tailwindcss').Config} */
module.exports = {
  theme: {
    extend: {
      colors: {
        paper  : '#F6F3EC',
        surface: '#FBF9F4',
        sand   : '#E9E2D3',
        clay   : '#D3C6B0',
        stone  : '#A79C89',
        ink    : {
          DEFAULT: '#2C2823',
          soft   : '#6B6357',
        },
        sage   : {
          DEFAULT: '#7C8471',
          deep   : '#62685A',
        },
        rust   : {
          DEFAULT: '#B0795B',
          deep   : '#8A5A3E',
        },
        border : {
          DEFAULT: '#E2DACB',
          strong : '#878177',
        },
        success: {
          DEFAULT: '#7C8B6C',
          deep   : '#5C6B4E',
        },
        warning: {
          DEFAULT: '#A8874F',
          deep   : '#7E5F2C',
        },
        danger : {
          DEFAULT: '#A4695B',
          deep   : '#8C4A3C',
        },
        info   : {
          DEFAULT: '#8B8574',
          deep   : '#615C4E',
        },
      },
      fontFamily: {
        sans : ['Inter', 'system-ui', '-apple-system', 'Segoe UI', 'sans-serif'],
        serif: ['Fraunces', 'Newsreader', 'Georgia', 'serif'],
      },
      fontSize: {
        xs  : ['0.8rem', { lineHeight: '1.6' }],
        sm  : ['0.889rem', { lineHeight: '1.6' }],
        base: ['1rem', { lineHeight: '1.6' }],
        lg  : ['1.25rem', { lineHeight: '1.2', letterSpacing: '-0.01em' }],
        xl  : ['1.563rem', { lineHeight: '1.2', letterSpacing: '-0.01em' }],
        '2xl': ['1.953rem', { lineHeight: '1.2', letterSpacing: '-0.01em' }],
        '3xl': ['2.441rem', { lineHeight: '1.2', letterSpacing: '-0.01em' }],
      },
      borderRadius: {
        sm: '4px',
        md: '8px',
        lg: '16px',
      },
      boxShadow: {
        sm: '0 1px 2px rgba(44, 40, 35, 0.05)',
        md: '0 4px 12px rgba(44, 40, 35, 0.06)',
        lg: '0 12px 32px rgba(44, 40, 35, 0.08)',
      },
    },
  },
  plugins: [],
};
