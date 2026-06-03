---
name: Precision Marketing Logic
colors:
  surface: '#f8f9ff'
  surface-dim: '#cbdbf5'
  surface-bright: '#f8f9ff'
  surface-container-lowest: '#ffffff'
  surface-container-low: '#eff4ff'
  surface-container: '#e5eeff'
  surface-container-high: '#dce9ff'
  surface-container-highest: '#d3e4fe'
  on-surface: '#0b1c30'
  on-surface-variant: '#424754'
  inverse-surface: '#213145'
  inverse-on-surface: '#eaf1ff'
  outline: '#727785'
  outline-variant: '#c2c6d6'
  surface-tint: '#005ac2'
  primary: '#0058be'
  on-primary: '#ffffff'
  primary-container: '#2170e4'
  on-primary-container: '#fefcff'
  inverse-primary: '#adc6ff'
  secondary: '#545f73'
  on-secondary: '#ffffff'
  secondary-container: '#d5e0f8'
  on-secondary-container: '#586377'
  tertiary: '#006947'
  on-tertiary: '#ffffff'
  tertiary-container: '#00855b'
  on-tertiary-container: '#f5fff6'
  error: '#ba1a1a'
  on-error: '#ffffff'
  error-container: '#ffdad6'
  on-error-container: '#93000a'
  primary-fixed: '#d8e2ff'
  primary-fixed-dim: '#adc6ff'
  on-primary-fixed: '#001a42'
  on-primary-fixed-variant: '#004395'
  secondary-fixed: '#d8e3fb'
  secondary-fixed-dim: '#bcc7de'
  on-secondary-fixed: '#111c2d'
  on-secondary-fixed-variant: '#3c475a'
  tertiary-fixed: '#6ffbbe'
  tertiary-fixed-dim: '#4edea3'
  on-tertiary-fixed: '#002113'
  on-tertiary-fixed-variant: '#005236'
  background: '#f8f9ff'
  on-background: '#0b1c30'
  surface-variant: '#d3e4fe'
typography:
  display-lg:
    fontFamily: Inter
    fontSize: 48px
    fontWeight: '700'
    lineHeight: 56px
    letterSpacing: -0.02em
  headline-lg:
    fontFamily: Inter
    fontSize: 32px
    fontWeight: '600'
    lineHeight: 40px
    letterSpacing: -0.01em
  headline-lg-mobile:
    fontFamily: Inter
    fontSize: 24px
    fontWeight: '600'
    lineHeight: 32px
  headline-md:
    fontFamily: Inter
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
    lineHeight: 20px
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
  base: 4px
  xs: 8px
  sm: 16px
  md: 24px
  lg: 32px
  xl: 48px
  gutter: 24px
  margin-mobile: 16px
  margin-desktop: 40px
  max-width: 1280px
---

## Brand & Style

The design system is engineered for a high-performance AI marketing platform. The brand personality is authoritative yet accessible, positioning the tool as an intelligent partner rather than just a utility. It targets marketing professionals and growth hackers who value speed, data accuracy, and clarity over decorative flair.

The visual style is **Modern Corporate Minimalism**. It utilizes heavy whitespace to reduce cognitive load during complex marketing workflows. The aesthetic is "tech-native"—clean, structured, and intentional. Every element serves a functional purpose, using high-contrast typography and a systematic grid to ensure that AI-generated insights remain the focal point of the user experience.

## Colors

The palette is anchored by a vibrant **Primary Blue (#3B82F6)**, used specifically for primary actions and active states to guide user intent. 

- **Primary:** #3B82F6 (Action, Focus, Selection)
- **Secondary:** #1E293B (Headers, Dark Mode foundations, High-contrast text)
- **Success/Tertiary:** #10B981 (Growth metrics, active campaigns, positive AI status)
- **Neutral/Surface:** A range of cool grays (#F8FAFC to #64748B) used for input backgrounds, borders, and secondary labels.

The background uses a pure white or very light gray (#F8FAFC) to maintain a sterile, professional environment. Text contrast follows WCAG AA standards strictly to ensure readability of dense data sets.

## Typography

The design system relies exclusively on **Inter** for its systematic, utilitarian qualities and exceptional legibility at small sizes. 

- **Headlines:** Use tighter letter-spacing and semi-bold weights to create a strong visual hierarchy.
- **Body:** Standard weight (400) with generous line heights (1.5x) to ensure long-form AI copy results are easy to scan.
- **Labels:** Small caps or all-caps are used sparingly for category headers and table columns to differentiate metadata from content.

## Layout & Spacing

The design system employs a **12-column fluid grid** for desktop and a **4-column grid** for mobile. 

- **Grid Logic:** Uses a 4px baseline shift. Most components use 16px (sm) or 24px (md) internal padding.
- **Desktop:** 12 columns, 24px gutters, 40px side margins. 
- **Tablet:** 8 columns, 16px gutters, 24px side margins.
- **Mobile:** 4 columns, 16px gutters, 16px side margins.

Content is grouped into logical modules using cards. Spacing between major sections should be 48px (xl) to maintain the minimalist, airy feel required for a professional SaaS tool.

## Elevation & Depth

Depth is conveyed through **Tonal Layering** and **Ambient Shadows**. 

1. **Surface Level (0dp):** The main background (#F8FAFC).
2. **Card Level (1dp):** White backgrounds (#FFFFFF) with a subtle 1px border (#E2E8F0) and a soft, low-opacity shadow (Y: 2px, Blur: 4px, Opacity: 4%).
3. **Overlay Level (2dp):** Modals and dropdowns use a more pronounced shadow (Y: 10px, Blur: 15px, Opacity: 8%) to indicate temporary priority.

Avoid heavy blacks; shadows should use the secondary color (#1E293B) at very low opacity to maintain a "clean tech" look.

## Shapes

The design system uses a **Rounded** shape language to soften the "industrial" feel of data-heavy marketing tools.

- **Standard Elements:** 8px (0.5rem) radius for buttons, inputs, and small cards.
- **Container Elements:** 16px (1rem) radius for large dashboard cards and tool containers.
- **Selection Toggles:** Fully pill-shaped (rounded-full) to distinguish them from standard buttons.

Interactive elements like checkboxes retain a smaller 4px radius to feel precise and technical.

## Components

### Buttons & Actions
- **Primary:** Solid #3B82F6 background, white text, 8px radius.
- **Secondary:** #F1F5F9 background, #1E293B text.
- **States:** Hover states should darken the background by 10%. Active/Pressed states should have a 2px focus ring of the primary color with 4px offset.

### Selection & Inputs
- **Toggle Switches:** Segmented controls (e.g., SEO vs Copywriting) use a background-track style where the active state is a white "floating" card inside a gray track.
- **Checkboxes:** 18px squares with a 4px radius. When checked, the primary blue fills the box with a white checkmark icon.
- **Input Fields:** 1px border (#E2E8F0), 8px radius, 12px horizontal padding. On focus, the border changes to the primary blue.

### Cards & Lists
- **Tool Cards:** Should contain a 24px icon, headline-md, and body-sm description.
- **Interactive Lists:** Used for platform selection (e.g., Google, Facebook). Each list item should have a hover state background (#F1F5F9) and a trailing checkbox for multi-select.

### AI Indicators
- Small chips with a "sparkle" icon and #10B981 background (low opacity) to indicate which content was generated or optimized by AI.