---
name: Professional Marketing Suite
colors:
  surface: '#f8f9fa'
  surface-dim: '#d9dadb'
  surface-bright: '#f8f9fa'
  surface-container-lowest: '#ffffff'
  surface-container-low: '#f3f4f5'
  surface-container: '#edeeef'
  surface-container-high: '#e7e8e9'
  surface-container-highest: '#e1e3e4'
  on-surface: '#191c1d'
  on-surface-variant: '#424752'
  inverse-surface: '#2e3132'
  inverse-on-surface: '#f0f1f2'
  outline: '#727783'
  outline-variant: '#c2c6d4'
  surface-tint: '#005db7'
  primary: '#004d99'
  on-primary: '#ffffff'
  primary-container: '#1565c0'
  on-primary-container: '#dae5ff'
  inverse-primary: '#a9c7ff'
  secondary: '#526069'
  on-secondary: '#ffffff'
  secondary-container: '#d3e2ed'
  on-secondary-container: '#56656e'
  tertiary: '#005c16'
  on-tertiary: '#ffffff'
  tertiary-container: '#00771f'
  on-tertiary-container: '#96fc92'
  error: '#ba1a1a'
  on-error: '#ffffff'
  error-container: '#ffdad6'
  on-error-container: '#93000a'
  primary-fixed: '#d6e3ff'
  primary-fixed-dim: '#a9c7ff'
  on-primary-fixed: '#001b3d'
  on-primary-fixed-variant: '#00468c'
  secondary-fixed: '#d6e5ef'
  secondary-fixed-dim: '#bac9d3'
  on-secondary-fixed: '#0f1d25'
  on-secondary-fixed-variant: '#3b4951'
  tertiary-fixed: '#94f990'
  tertiary-fixed-dim: '#78dc77'
  on-tertiary-fixed: '#002204'
  on-tertiary-fixed-variant: '#005313'
  background: '#f8f9fa'
  on-background: '#191c1d'
  surface-variant: '#e1e3e4'
typography:
  headline-xl:
    fontFamily: Plus Jakarta Sans
    fontSize: 24px
    fontWeight: '700'
    lineHeight: 32px
  headline-lg:
    fontFamily: Plus Jakarta Sans
    fontSize: 20px
    fontWeight: '600'
    lineHeight: 28px
  headline-md:
    fontFamily: Plus Jakarta Sans
    fontSize: 16px
    fontWeight: '600'
    lineHeight: 24px
  body-lg:
    fontFamily: Inter
    fontSize: 16px
    fontWeight: '400'
    lineHeight: 24px
  body-md:
    fontFamily: Inter
    fontSize: 14px
    fontWeight: '400'
    lineHeight: 20px
  body-sm:
    fontFamily: Inter
    fontSize: 12px
    fontWeight: '400'
    lineHeight: 18px
  label-md:
    fontFamily: Inter
    fontSize: 14px
    fontWeight: '500'
    lineHeight: 16px
    letterSpacing: 0.02em
  label-sm:
    fontFamily: Inter
    fontSize: 12px
    fontWeight: '600'
    lineHeight: 14px
    letterSpacing: 0.01em
rounded:
  sm: 0.25rem
  DEFAULT: 0.5rem
  md: 0.75rem
  lg: 1rem
  xl: 1.5rem
  full: 9999px
spacing:
  sidebar-width: 240px
  container-padding: 24px
  gutter-md: 16px
  stack-sm: 8px
  stack-md: 16px
  stack-lg: 24px
---

## Brand & Style

The design system is engineered for a professional SaaS environment focused on digital marketing and data analytics. It prioritizes clarity, efficiency, and trust through a **Corporate / Modern** design style. The visual language utilizes a clean, high-contrast interface with a primary focus on data readability and structured information architecture.

The personality is authoritative yet accessible, using ample white space and a systematic grid to reduce cognitive load for users managing complex marketing tasks. Subtle roundedness and soft shadows are employed to provide a modern feel without sacrificing the professional rigor expected in a business-to-business platform.

## Colors

The palette is anchored by a deep "Vibrant Blue" primary color, symbolizing stability and professional focus. 

- **Primary:** Used for high-emphasis actions, active navigation states, and key progress indicators.
- **Secondary:** A soft blue tint used for background highlights, hover states, and subtle UI accents.
- **Surface & Neutrals:** A range of cool greys is used to define the canvas and container hierarchy. The sidebar and main content area utilize different shades of white and off-white to create clear separation.
- **Status:** Standardized semantic colors for success (Green), error (Red), and warning (Amber) follow global accessibility standards, ensuring clear feedback for user interactions and system notifications.

## Typography

This design system uses a dual-font strategy. **Plus Jakarta Sans** provides a modern, slightly geometric feel for headlines and brand elements, while **Inter** is the workhorse for body copy and data-dense tables, ensuring maximum legibility across all screen densities.

Large headlines (Headline XL) are reserved for page titles and major section headers. Body text defaults to 14px for standard content, scaling down to 12px for supporting metadata and labels. Line heights are generous to prevent text-heavy dashboards from feeling cramped.

## Layout & Spacing

The layout follows a **Fixed-Fluid Hybrid** model. A permanent vertical sidebar is fixed to the left, while the main content area utilizes a fluid grid that adapts to the viewport width.

- **Grid:** A 12-column grid is used for the main dashboard content.
- **Sidebar:** Maintains a constant width of 240px to ensure navigation items remain legible.
- **Rhythm:** An 8px base unit drives all spacing decisions. Component internal padding is typically 16px, while vertical stacking of cards and sections uses 24px increments to create a clear visual rhythm.
- **Breakpoints:** The layout collapses to a single column with a hidden drawer menu on mobile devices (< 768px).

## Elevation & Depth

Visual hierarchy is established primarily through **Tonal Layers** and **Low-contrast Outlines**. 

The main background uses a neutral off-white, while primary containers (cards) are pure white with a 1px border. Shadows are used sparingly; when applied, they are highly diffused "Ambient Shadows" (0px 4px 20px rgba(0,0,0,0.05)) to suggest subtle lift for interactive elements like modals or dropdown menus. This approach keeps the interface feeling flat and modern while providing just enough depth to guide the user's eye.

## Shapes

The shape language is consistently **Rounded**, striking a balance between the rigidity of corporate software and the friendliness of modern SaaS products. 

Standard components like buttons, input fields, and cards use a 0.5rem (8px) corner radius. "Pill" shapes are reserved specifically for status chips, tags, and secondary action buttons to differentiate them from primary structural elements. Avatars and specific decorative icons may use a fully circular (50%) radius.

## Components

### Buttons
- **Primary:** Solid blue background with white text. High prominence for main actions.
- **Secondary:** Blue border with a transparent background or light blue tint.
- **Ghost:** No background or border, used for utility actions or within navigation.

### Cards
Cards are the primary organizational unit. They feature a white background, 1px grey border, and 16px to 24px of internal padding. Header areas within cards often have a subtle bottom divider.

### Input Fields
Inputs use a white background with a 1px border. On focus, the border transitions to the primary blue with a soft outer glow. Labels are positioned above the field in a bold, small font (Label SM).

### Sidebar Navigation
Navigation items use a vertical stack. The active state is indicated by a solid blue background or a bold blue accent bar on the side, ensuring the user always knows their location within the app hierarchy.

### Chips & Tags
Small, rounded-pill components used for filtering or status. They utilize the secondary color palette (tinted backgrounds) to remain distinct but subordinate to primary buttons.