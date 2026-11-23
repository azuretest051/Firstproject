---
name: TasteMatch AI
colors:
  surface: '#111317'
  surface-dim: '#111317'
  surface-bright: '#37393d'
  surface-container-lowest: '#0c0e11'
  surface-container-low: '#1a1c1f'
  surface-container: '#1e2023'
  surface-container-high: '#282a2d'
  surface-container-highest: '#333538'
  on-surface: '#e2e2e6'
  on-surface-variant: '#e1bfb8'
  inverse-surface: '#e2e2e6'
  inverse-on-surface: '#2f3034'
  outline: '#a88a83'
  outline-variant: '#59413c'
  surface-tint: '#ffb4a3'
  primary: '#ffb4a3'
  on-primary: '#630f00'
  primary-container: '#ff6b4a'
  on-primary-container: '#661000'
  inverse-primary: '#ae3115'
  secondary: '#ffb95f'
  on-secondary: '#472a00'
  secondary-container: '#ee9800'
  on-secondary-container: '#5b3800'
  tertiary: '#ffb59e'
  on-tertiary: '#5e1700'
  tertiary-container: '#eb7a56'
  on-tertiary-container: '#611800'
  error: '#ffb4ab'
  on-error: '#690005'
  error-container: '#93000a'
  on-error-container: '#ffdad6'
  primary-fixed: '#ffdad2'
  primary-fixed-dim: '#ffb4a3'
  on-primary-fixed: '#3d0600'
  on-primary-fixed-variant: '#8c1900'
  secondary-fixed: '#ffddb8'
  secondary-fixed-dim: '#ffb95f'
  on-secondary-fixed: '#2a1700'
  on-secondary-fixed-variant: '#653e00'
  tertiary-fixed: '#ffdbd0'
  tertiary-fixed-dim: '#ffb59e'
  on-tertiary-fixed: '#3a0b00'
  on-tertiary-fixed-variant: '#7f2a0d'
  background: '#111317'
  on-background: '#e2e2e6'
  surface-variant: '#333538'
typography:
  headline-xl:
    fontFamily: Plus Jakarta Sans
    fontSize: 40px
    fontWeight: '800'
    lineHeight: 48px
    letterSpacing: -0.03em
  headline-xl-mobile:
    fontFamily: Plus Jakarta Sans
    fontSize: 30px
    fontWeight: '800'
    lineHeight: 36px
    letterSpacing: -0.02em
  headline-lg:
    fontFamily: Plus Jakarta Sans
    fontSize: 32px
    fontWeight: '700'
    lineHeight: 40px
    letterSpacing: -0.02em
  headline-lg-mobile:
    fontFamily: Plus Jakarta Sans
    fontSize: 24px
    fontWeight: '700'
    lineHeight: 32px
    letterSpacing: -0.02em
  headline-md:
    fontFamily: Plus Jakarta Sans
    fontSize: 22px
    fontWeight: '700'
    lineHeight: 28px
    letterSpacing: -0.015em
  headline-sm:
    fontFamily: Plus Jakarta Sans
    fontSize: 18px
    fontWeight: '600'
    lineHeight: 24px
    letterSpacing: -0.01em
  body-lg:
    fontFamily: Plus Jakarta Sans
    fontSize: 16px
    fontWeight: '400'
    lineHeight: 24px
    letterSpacing: -0.005em
  body-md:
    fontFamily: Plus Jakarta Sans
    fontSize: 14px
    fontWeight: '400'
    lineHeight: 20px
    letterSpacing: 0em
  body-sm:
    fontFamily: Plus Jakarta Sans
    fontSize: 12px
    fontWeight: '400'
    lineHeight: 16px
    letterSpacing: 0.01em
  label-lg:
    fontFamily: Plus Jakarta Sans
    fontSize: 14px
    fontWeight: '600'
    lineHeight: 20px
    letterSpacing: 0.01em
  label-md:
    fontFamily: Plus Jakarta Sans
    fontSize: 12px
    fontWeight: '600'
    lineHeight: 16px
    letterSpacing: 0.02em
  label-sm:
    fontFamily: Plus Jakarta Sans
    fontSize: 11px
    fontWeight: '700'
    lineHeight: 14px
    letterSpacing: 0.04em
rounded:
  sm: 0.25rem
  DEFAULT: 0.5rem
  md: 0.75rem
  lg: 1rem
  xl: 1.5rem
  full: 9999px
spacing:
  gutter: 1rem
  gutter-md: 1.5rem
  margin: 1rem
  margin-md: 2rem
  margin-lg: 3rem
  space-xs: 0.25rem
  space-sm: 0.5rem
  space-md: 1rem
  space-lg: 1.5rem
  space-xl: 2.5rem
---

## Brand & Style

This design system establishes an atmospheric, late-night epicurean environment tailored for high-intent diners across dynamic urban metro centers. The visual atmosphere departs from utilitarian listing directories, offering an intimate, low-light ambiance reminiscent of a dimly lit chef’s counter. The interface pairs tactile culinary warmth with precise algorithmic curation, deliberately rejecting generic hyper-digital AI tropes—specifically avoiding purple-blue neon washes, electric sparkles, and synthetic gradients.

The aesthetic fuses tactile dark minimalism with vibrant editorial framing:
- **Atmospheric Immersion:** Pure charcoal and near-black surfaces layer depth through tone and illumination rather than high-contrast daylight dividers.
- **Culinary Warmth:** Tonal energy draws entirely from searing corals, wood-fire ambers, and tandoor-inspired warmth, casting soft, appetizing glows across key decisions and discovery highlights.
- **Urban Editorial Precision:** Typographic weight is punchy, grounded, and modern, blending the energy of metropolitan food culture with the crisp structure of a high-performance utility.

## Colors

The color palette centers on a strict dark mode, structured to prioritize vibrant food photography and concentrated culinary accents. 

### Palette Architecture
- **Canvas & Surface Tier:**
  - Base Background: `#0B0D10` (Deep caviar charcoal canvas)
  - Surface Level 1 (Cards, elevated modules): `#14171D`
  - Surface Level 2 (Flyouts, active sheets, segmented controls): `#1B2028`
  - Surface Level 3 (Hover overlays, high-priority badges): `#222832`
  - Structural Stroke / Subtle Border: `#262D38`
  - Divider Subtle: `rgba(255, 255, 255, 0.06)`

- **Accent & Illumination:**
  - Primary Accent: `#FF6B4A` (Tandoor Coral; anchors primary CTAs, algorithm match highlights, and primary states)
  - Secondary Accent: `#F59E0B` (Warm Amber; reserves for Michelin/curator accolades, user ratings, and gold-standard curation tags)
  - Tertiary / Ember Tint: `#FF8A65` (Light Coral; interactive hovers and gradient terminates)
  - Culinary Glow: `rgba(255, 107, 74, 0.15)` to `rgba(245, 158, 11, 0.08)` (Used sparingly for radial spotlights behind top dish matches)

- **Typography & Content Contrast:**
  - Text Primary: `#F3F4F6` (High-contrast soft white)
  - Text Secondary: `#9CA3AF` (Muted warm slate)
  - Text Tertiary / Disabled: `#6B7280`

## Typography

The typographic hierarchy relies on Plus Jakarta Sans across all levels, utilizing heavy weight variations for punchy restaurant branding, dish titles, and AI match tags, while maintaining open letterforms for dense ingredient lists and micro-labels.

### Typographic Principles
- **Headlines:** Display weights (700 and 800) use negative letter tracking to give editorial force to neighborhood titles, restaurant names, and match percentages.
- **Numerical Hierarchy:** Ratings, prices, and percentage affinities utilize `label-lg` or `headline-md` weights, ensuring scannability during fast thumb-scroll discovery.
- **Labels & Microcopy:** Badges, cuisine tags, and metro-neighborhood markers default to uppercase `label-sm` with widened tracking (+0.04em) for legibility against dark slate surfaces.

## Layout & Spacing

The layout model adapts a dense, mobile-first feed into an expansive desktop editorial spread.

### Grid & Form Factors
- **Mobile (< 768px):** Single-column layout anchored with edge margins of `margin` (`1rem`). Card elements span the full width or flow in horizontal edge-to-edge carousels with peek overscrolls.
- **Tablet (768px – 1024px):** 6-column fluid grid, `gutter-md` (`1.5rem`), edge margins of `margin-md` (`2rem`). Restaurant discovery cards sit in 2-column or 3-column splits.
- **Desktop (> 1024px):** 12-column fixed-max grid (capped at 1280px), centered with `margin-lg` (`3rem`) padding. Left 4-columns lock contextual AI filters, taste maps, and taste profile selectors; right 8-columns stream curated venues and map overlays.

### Vertical Rhythm
Internal card padding aligns strictly to `space-md` (16px), maintaining a compact, data-rich experience. Section dividers, collections, and editorial storytelling blocks are separated by `space-xl` (40px) to give negative space breathing room.

## Elevation & Depth

Visual hierarchy does not use diffuse, generic white drop-shadows. Depth relies on tonal surface progression, precise hairline borders, and localized thermal backlights.

### Surface Tiers
- **Tier 0 (Base Canvas):** `#0B0D10` – The endless viewport canvas.
- **Tier 1 (Resting Cards & Feeds):** `#14171D` with a persistent hairline outline of `1px solid #262D38`.
- **Tier 2 (Popovers, Active Drawer, Floating Navigation):** `#1B2028` with `1px solid #262D38` and a deep floor shadow (`0 12px 32px -4px rgba(0, 0, 0, 0.7)`).
- **Tier 3 (Modals & Critical System Sheets):** `#222832` overlaid on an 80% opacity `#0B0D10` backdrop blur (12px blur radius).

### Culinary AI Glow
When an item holds an AI taste match affinity of 90% or higher, the card gains a directional amber-coral underglow instead of a border change:
- `box-shadow: 0 4px 24px -2px rgba(255, 107, 74, 0.12), 0 0 1px 1px rgba(255, 107, 74, 0.3);`
This draws the eye to high-confidence dining matches without breaking the dark aesthetic.

## Shapes

The design system implements a `roundedness: 2` scale (0.5rem base radius), producing a modern, refined balance between industrial utility and consumer polish.

- **Micro Components (Tags, Badges, Micro-chips):** Use `0.375rem` (6px) to keep small text units tight and structured.
- **Standard Controls (Input fields, standard buttons, segmented segments):** Set to `0.5rem` (`rounded-md`, 8px).
- **Cards & Interactive Containers:** Use `1rem` (`rounded-lg`, 16px) to cleanly frame visual food assets.
- **Bottom Sheets & Modal Overlays:** Use `1.5rem` (`rounded-xl`, 24px) on top radii to soften presentation against the screen edges.
- **Pill Exceptions:** User avatars, match percentage chips, and taste filter pills use fully rounded circular pills (`9999px`).

## Components

### Buttons
- **Primary Action (Book Table, View Match):** Filled background of `#FF6B4A`, text `#0B0D10` (ultra-bold for contrast) or crisp white `#FFFFFF`. Hover shifts to `#FF8A65` with a subtle thermal aura (`box-shadow: 0 0 16px rgba(255, 107, 74, 0.4)`).
- **Secondary Action (Save to List, Share):** Transparent background, border `1px solid #262D38`, text `#F3F4F6`. Hover triggers background `#1B2028` and border `#FF6B4A`.
- **Tertiary / Ghost:** No border, text `#9CA3AF`, hover text `#F3F4F6`.

### Segmented Controls (Delivery vs. Dine-in vs. Nightlife)
- Track background of `#14171D` with `1px solid #262D38`.
- Active segment rises to `#1B2028` with text `#F3F4F6` and an amber/coral active indicator pip or border accent. Inactive options remain `#9CA3AF`.

### Rating Sliders & Visual Pickers
- **Track:** 6px height, background `#1B2028`.
- **Filled Progress:** Gradient fill from `#F59E0B` (Amber) to `#FF6B4A` (Coral).
- **Thumb Handle:** Solid `#FFFFFF`, 20px circle, with a soft drop shadow and a glowing coral focus ring.

### Food & Flavor Profile Tags
- Base tag background: `#1B2028`.
- Border: `1px solid #262D38`.
- Text: `#F3F4F6` at `label-sm`.
- **Selected Flavor Tag (e.g., "Smoky Tandoor", "Coastal Malabari"):** Background tint of `rgba(255, 107, 74, 0.12)`, border `1px solid #FF6B4A`, text `#FF6B4A`.

### Rank & Affinity Badges
- **TasteMatch % Chip:** Pill container with background `rgba(255, 107, 74, 0.15)`, text `#FF6B4A`, featuring a small flame or spark icon. For matches >95%, add subtle border `1px solid rgba(255, 107, 74, 0.4)`.
- **Rating Badge:** Solid `#14171D` badge, `1px solid #F59E0B`, text `#F59E0B` with an integrated star glyph.

### AI Explanation Callouts ("Why TasteMatch Picked This")
- Background: Surface `#14171D` with a subtle gradient bleed from the left edge (`rgba(255, 107, 74, 0.08)` transitioning to transparent).
- Border: Left accent border of `3px solid #FF6B4A`; remaining borders `1px solid #262D38`.
- Layout: Contains an avatar/icon badge, followed by a concise 2-sentence rationale highlighting user-flavor alignments (e.g., *"Matched for high heat tolerance and your preference for sourdough wood-fired crusts in Indiranagar"*).

### Restaurant Cards
- Multi-layer element containing an edge-to-edge 16:9 image container, darkened with a bottom gradient fade (`rgba(11, 13, 16, 0.8)` to transparent).
- Price, distance, and neighborhood hover inside image lower bounds.
- Body container (#14171D) hosts title, verified dietary markers (e.g., pure veg / non-veg pips), match score, and top three AI dish tags.