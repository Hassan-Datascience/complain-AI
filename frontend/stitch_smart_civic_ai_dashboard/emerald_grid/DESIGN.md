---
name: Emerald Grid
colors:
  surface: '#0e1513'
  surface-dim: '#0e1513'
  surface-bright: '#343b38'
  surface-container-lowest: '#090f0e'
  surface-container-low: '#161d1b'
  surface-container: '#1a211f'
  surface-container-high: '#252b29'
  surface-container-highest: '#2f3634'
  on-surface: '#dde4e1'
  on-surface-variant: '#c2cab0'
  inverse-surface: '#dde4e1'
  inverse-on-surface: '#2b3230'
  outline: '#8c947c'
  outline-variant: '#424936'
  surface-tint: '#98da27'
  primary: '#ccff80'
  on-primary: '#213600'
  primary-container: '#a3e635'
  on-primary-container: '#416400'
  inverse-primary: '#446900'
  secondary: '#74dd7e'
  on-secondary: '#003910'
  secondary-container: '#007f2d'
  on-secondary-container: '#c4ffc2'
  tertiary: '#ffecd9'
  on-tertiary: '#472a00'
  tertiary-container: '#ffc989'
  on-tertiary-container: '#805000'
  error: '#ffb4ab'
  on-error: '#690005'
  error-container: '#93000a'
  on-error-container: '#ffdad6'
  primary-fixed: '#b2f746'
  primary-fixed-dim: '#98da27'
  on-primary-fixed: '#121f00'
  on-primary-fixed-variant: '#334f00'
  secondary-fixed: '#90fa97'
  secondary-fixed-dim: '#74dd7e'
  on-secondary-fixed: '#002106'
  on-secondary-fixed-variant: '#00531b'
  tertiary-fixed: '#ffddb8'
  tertiary-fixed-dim: '#ffb95f'
  on-tertiary-fixed: '#2a1700'
  on-tertiary-fixed-variant: '#653e00'
  background: '#0e1513'
  on-background: '#dde4e1'
  surface-variant: '#2f3634'
typography:
  headline-xl:
    fontFamily: Manrope
    fontSize: 40px
    fontWeight: '800'
    lineHeight: 48px
    letterSpacing: -0.02em
  headline-lg:
    fontFamily: Manrope
    fontSize: 32px
    fontWeight: '700'
    lineHeight: 40px
    letterSpacing: -0.01em
  headline-lg-mobile:
    fontFamily: Manrope
    fontSize: 24px
    fontWeight: '700'
    lineHeight: 32px
  headline-md:
    fontFamily: Manrope
    fontSize: 24px
    fontWeight: '600'
    lineHeight: 32px
  body-lg:
    fontFamily: Inter
    fontSize: 18px
    fontWeight: '400'
    lineHeight: 28px
  body-md:
    fontFamily: Inter
    fontSize: 16px
    fontWeight: '400'
    lineHeight: 24px
  body-sm:
    fontFamily: Inter
    fontSize: 14px
    fontWeight: '400'
    lineHeight: 20px
  label-md:
    fontFamily: Inter
    fontSize: 14px
    fontWeight: '600'
    lineHeight: 16px
    letterSpacing: 0.05em
  label-sm:
    fontFamily: Inter
    fontSize: 12px
    fontWeight: '500'
    lineHeight: 16px
rounded:
  sm: 0.25rem
  DEFAULT: 0.5rem
  md: 0.75rem
  lg: 1rem
  xl: 1.5rem
  full: 9999px
spacing:
  base: 8px
  container-padding-desktop: 32px
  container-padding-mobile: 16px
  gutter: 24px
  stack-sm: 8px
  stack-md: 16px
  stack-lg: 32px
---

## Brand & Style
The design system is engineered for a high-utility civic platform, blending professional reliability with a forward-thinking, data-driven aesthetic. The style is **Modern Corporate** with a **Tactile** edge, utilizing high-contrast accents against a deep, structural background. It aims to evoke a sense of precision, efficiency, and clarity.

The interface prioritizes accessibility and information density without sacrificing visual breathing room. It leverages subtle glass-like properties and vibrant accent colors to guide user attention through complex civic data and service workflows.

## Colors
This design system utilizes a sophisticated dark palette anchored by a near-black green (#0D0F0D). The primary engine of the UI is the Lime accent (#A3E635), which serves as the high-visibility signal for interactive elements and primary call-to-actions.

- **Primary Accent:** Use for primary buttons, active toggles, and critical data highlights.
- **Secondary Accent:** Use for hover states, success indicators, and secondary action paths.
- **Surface Strategy:** Use #1A1D1A for cards and containers to create a clear layer of separation from the base background.
- **Borders:** Use #2A2D2A for structural definition. Interactive elements may transition borders to the primary accent on focus.

## Typography
The typography system uses a dual-font approach to balance character with utility. 

**Manrope** is used for headlines to provide a modern, geometric, and authoritative voice. Its slightly condensed nature allows for impactful titling even with long civic service names.

**Inter** is the workhorse for body text, data tables, and labels. It provides exceptional legibility at small sizes and high-density layouts. 

- Use `label-md` for section headers within cards.
- Use `headline-xl` sparingly for high-level dashboard metrics or landing hero sections.
- Ensure all body text uses #F5F5F5 (Primary Text) for maximum contrast against the dark background.

## Layout & Spacing
The design system employs a **Fluid Grid** system based on an 8px root rhythm. 

- **Desktop (1440px+):** 12-column grid with 24px gutters and 32px side margins.
- **Tablet (768px - 1439px):** 8-column grid with 20px gutters and 24px side margins.
- **Mobile (< 767px):** 4-column grid with 16px gutters and 16px side margins.

Vertical rhythm should follow the `stack` variables to maintain consistency between related elements (sm), components (md), and sections (lg).

## Elevation & Depth
Depth is communicated through **Tonal Layers** and **Subtle Glows** rather than heavy shadows.

1.  **Level 0 (Background):** #0D0F0D - The canvas.
2.  **Level 1 (Cards/Surfaces):** #1A1D1A - Raised elements with a 1px solid border of #2A2D2A.
3.  **Level 2 (Interaction):** On hover, cards should transition their border color to a 20% opacity version of the Primary Accent (#A3E635) and apply a very soft, diffused outer glow (0px 4px 20px) using the same color at 10% opacity.
4.  **Level 3 (Modals/Popovers):** Surface #1A1D1A with a distinct 1px border of #3A3D3A and a background blur (12px) applied to the backdrop overlay.

## Shapes
The shape language is "Soft-Square," utilizing a 8px to 12px corner radius to balance friendliness with professional structure.

- **Standard Elements (Buttons, Inputs):** 8px (rounded).
- **Large Containers (Cards, Modals):** 12px (rounded-lg).
- **Status Pills/Tags:** 100px (rounded-xl/pill) to distinguish them from interactive buttons.
- **Icon Enclosures:** 8px for consistency with inputs.

## Components

### Buttons
- **Primary:** Solid #A3E635 fill with #0D0F0D text. 8px radius.
- **Secondary:** Transparent fill, #7EE787 border (1px), #7EE787 text. 
- **Tertiary/Ghost:** No border, #F5F5F5 text, primary lime icon.

### Input Fields
- **Default:** #1A1D1A background, #2A2D2A border, 8px radius.
- **Focus:** Border changes to #A3E635 with a subtle 2px outer glow.
- **Placeholder:** #6B7280.

### Cards
- Background: #1A1D1A.
- Border: 1px solid #2A2D2A.
- Padding: 24px (desktop), 16px (mobile).
- Hover: Border color shifts to #A3E635 (30% opacity).

### Status Indicators
- **Critical:** #EF4444 fill (10% opacity) with #EF4444 text and a 4px solid dot.
- **Resolved:** #7EE787 fill (10% opacity) with #7EE787 text.
- Use pill shapes for all status badges to ensure they are visually distinct from buttons.

### Lists & Data Tables
- Use subtle #2A2D2A horizontal dividers. 
- Rows should have a subtle #F5F5F5 (5% opacity) highlight on hover to assist with horizontal tracking of data.