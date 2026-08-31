# Signature UI Design System Specification
### A reusable visual identity for Pygame-based games

## 1. Purpose
This document defines a **signature UI design system** — a consistent visual and interaction language to be reused across every game built with Pygame. The goal is brand recognition: a player should recognize "your" UI on sight, regardless of the game's individual theme (forest, space, underwater, etc.).

The system is split into two layers:
- **Locked (Signature) Layer** — Never changes between games. This is what makes the UI recognizably "yours": button shapes, typography treatment, shadow/bevel language, iconography style, layout structure.
- **Swappable (Theme) Layer** — Changes per game: background artwork, color palette, panel material/texture, decorative motifs.

Reference basis: forest-themed mockups showing a glossy, cartoon "candy UI" style (in the vein of casual mobile titles like Township or Toon Blast) — chunky outlined typography, wood-toned panels, glossy 3D circular buttons, soft atmospheric backgrounds.

---

## 2. Design Philosophy (Locked)
| Principle | Description |
|---|---|
| **Tactile & glossy** | Every interactive element reads as a physical, pressable object — soft 3D bevel, glossy highlight, drop shadow. Nothing is flat. |
| **Rounded, never sharp** | All shapes use generous corner radii or full circles. No hard rectangular edges anywhere in the UI layer. |
| **Outlined, chunky typography** | Headlines use a bold, rounded display font with a thick contrasting outline and drop shadow — never plain flat text. |
| **Warm foreground, cool background** | UI chrome (panels, buttons) sits in warm tones; the game/background scene sits in cooler, atmospheric tones — so UI always pops forward. |
| **Everything has weight** | Consistent light source (top-left) drives highlight/shadow placement on every asset, so the whole UI feels lit from one place. |

---

## 3. Color System

### 3.1 Color Roles (Locked structure — values are swappable per theme)
Every theme must define a value for each role below. This keeps contrast and hierarchy consistent even when the palette changes.

| Role | Function | Reference value (Forest theme) |
|---|---|---|
| `bg.primary` | Background scene base tone | `#0F2E12` → `#8FCF4A` (radial glow gradient) |
| `panel.fill` | Modal/panel background | `#E8A752` → `#C9822F` (vertical gradient) |
| `panel.border` | Panel outline/rim | `#F5DFA8` |
| `panel.outline` | Panel drop outline | `#8A5A2A` |
| `header.fill` | Tab/banner behind panel titles | `#F0A830` → `#E08A1A` |
| `cta.primary` | Main action button (Save/Play/Confirm) | `#8FD63F` → `#4A9E1E` |
| `cta.border` | CTA outline | `#2D6E10` |
| `danger` | Close/cancel button | `#E8492F` |
| `text.title.fill` | Display headline fill | `#F2D94E` → `#E8C020` |
| `text.title.outline` | Display headline stroke | `#5A1F3D` |
| `text.body` | UI/body text | `#FFFFFF` |
| `icon.slot.1`–`5` | Rotating palette for circular icon buttons | Navy `#1A2530`, Gold `#F0A830`, Green `#5CB82E`, Pink `#E8558A`, Blue `#3AA8E0` |

### 3.2 Rule
Each new game defines its own hex values for these roles, but **the number of roles and their relative contrast (warm chrome / cool scene, bright CTA vs neutral secondary icons) must stay intact.**

---

## 4. Typography (Locked)

| Style | Usage | Treatment |
|---|---|---|
| **Display / Headline** | Game logo, panel titles ("Options", "THE TWINS") | Bold rounded font, thick 3–4px outline in `text.title.outline`, drop shadow offset ~3px down-right, slight baseline wobble per letter for a hand-placed feel, fill gradient using `text.title.fill` |
| **UI / Body** | Buttons, labels, HUD text | Rounded sans-serif, semi-bold to bold weight, white fill, subtle 1–2px soft shadow for legibility over busy backgrounds |
| **Numeric / Score** | Score counters, timers | Same UI font, slightly condensed, often paired with a small "+" pop-in animation on change |

**Recommended free fonts** (Pygame-compatible, permissive licensing): *Fredoka* or *Baloo 2* for Display; *Nunito* or *Quicksand* for UI/Body.

---

## 5. Component Library (Locked shapes & behavior / Swappable color-fill)

### 5.1 Circular Icon Button
- Perfect circle, fixed diameter per context (large: settings/currency row ≈ 64px, small: in-panel actions ≈ 48px)
- Radial glossy highlight occupying top ~40% of the circle
- 2–3px darker rim outline
- Soft drop shadow, offset down ~4px, blur ~6px, 30% opacity
- Centered flat white glyph icon, sized to ~55% of circle diameter
- **States:** default, pressed (scale to 92%, shadow shrinks), disabled (desaturated, 50% opacity)

### 5.2 Panel / Modal
- Rounded rectangle, corner radius ≈ 24px
- Two-tone border: outer dark outline (`panel.outline`) + inner light rim (`panel.border`)
- Vertical gradient fill (`panel.fill`)
- Drop shadow beneath entire panel, offset down ~8px, blur ~16px
- Optional subtle texture overlay (wood grain, stone, metal — theme-dependent) at low opacity

### 5.3 Header Banner
- Pill-shaped tab, overlapping the top edge of the panel by ~30% of its height
- Fill: `header.fill` gradient
- Centered Display-style title text, white fill with dark outline
- Sits above panel in z-order

### 5.4 Close Button
- Small circle (≈ 40px), positioned top-right corner of panel, overlapping the border by ~50%
- Fill: `danger`
- White bold "X" glyph, 3px stroke
- Same glossy/shadow treatment as standard icon buttons

### 5.5 Primary CTA Button
- Wide rounded rectangle or full pill shape, spans a fixed proportion of panel width (≈ 70–80%)
- Gradient fill: `cta.primary`, glossy highlight band across top third
- Outline: `cta.border`, 2–3px
- Bold white UI-font label, centered
- Decorative accent: 2–4 small sparkle/star particles scattered near the button corners, subtle idle twinkle animation
- **States:** default, pressed (scale 96%, highlight band flattens), disabled (desaturated)

### 5.6 Side Navigation Arrows
- Rounded triangular or chevron shape inside a soft rounded tab
- Positioned flush against the panel's left/right edge, vertically centered
- Same warm palette as panel chrome, subtle shadow
- Used for pagination between panel "pages" (e.g., multiple option tabs)

### 5.7 Progress / Loading Bar
- Rounded rectangle track, dark tone, inset shadow (reads as a groove)
- Rounded rectangle fill bar, gradient using a bright accent color, glossy top highlight
- Percentage label in UI font, either centered on the bar or directly below it

### 5.8 Decorative Accents (Theme-dependent motif, locked placement logic)
- Small motif elements (leaves/vines for forest, stars/comets for space, bubbles for underwater, etc.) frame the Display headline and flank key CTAs
- Ambient particle layer drifting slowly across the background (fireflies, dust motes, snow, bubbles) for atmosphere
- Rule: motif changes with theme; **the placement pattern (framing the title, flanking the CTA) stays consistent.**

---

## 6. Layout & Spacing Rules (Locked)
- Base spacing unit: 8px grid; all padding/margins are multiples of 8.
- Top-left corner reserved for a persistent icon-button row (currency, settings, share) across all screens.
- Modals are horizontally and vertically centered, occupying ≈ 60–75% of screen width on desktop-scale windows.
- Primary CTA is always the lowest element in a modal, full-width-relative, and visually the largest button on screen.
- Minimum tap/click target: 44×44px for any interactive element.

---

## 7. Motion Guidelines (Locked behavior, implemented via Pygame timers/tweening)
| Interaction | Animation |
|---|---|
| Button press | Scale down to ~92–96%, spring back on release (≈150ms) |
| Panel open | Scale + fade in from 85% → 100% opacity/size (≈200ms), slight overshoot bounce |
| Panel close | Reverse of open, faster (≈120ms) |
| Score increment | "+N" text spawns above score, floats up and fades over ≈600ms |
| CTA idle | Subtle looping sparkle twinkle every 2–3s; optional gentle scale pulse (100% → 103% → 100%) every few seconds to draw attention |
| Screen transitions | Cross-fade or iris-wipe, ≈300ms |

---

## 8. Theming System — What Changes Per Game

| Layer | Locked (Signature) | Swappable (Per-Game Theme) |
|---|---|---|
| Button/panel **shapes**, bevel & shadow logic | ✅ | — |
| Typography **treatment** (outline+shadow style) | ✅ | — |
| Component **layout positions** | ✅ | — |
| Motion/animation timing curves | ✅ | — |
| Color **role values** (hex codes) | — | ✅ |
| Background **scene art** | — | ✅ |
| Panel **material texture** (wood/stone/metal/ice) | — | ✅ |
| Decorative **motif** (leaves/stars/bubbles) | — | ✅ |
| Font **family choice** (within Display/UI role pairing) | Optional lock | ✅ (if not locked) |

Each new game ships a **theme pack**: a set of background art, a palette mapped to the color roles in Section 3.1, and a motif set — while reusing the same component code and layout logic untouched.

---

## 9. Pygame Implementation Notes
Pygame has no native rounded-rect gradients, glossy bevels, or blur — this style is achieved via **pre-rendered sprite assets**, not procedural drawing.

**Recommended architecture:**
- `ui/components.py` — reusable classes: `IconButton`, `Panel`, `HeaderBanner`, `CTAButton`, `ProgressBar`, `NavArrow`. Each class handles state (default/pressed/disabled), position, and draws from a themed asset reference rather than hardcoded colors.
- `ui/theme.py` — a `Theme` data object holding the color-role dictionary (Section 3.1) and asset paths for the active game; loaded once at startup.
- `assets/themes/<theme_name>/` — one folder per game/theme containing: `panel.png`, `header.png`, `cta_default.png`, `cta_pressed.png`, `icon_bg_*.png`, `close.png`, `nav_arrow.png`, `progress_track.png`, `progress_fill.png`, `bg_scene.png`, plus theme fonts if not using the shared default fonts.
- Components should accept a `theme` object at construction so the same `CTAButton` class renders correctly whether it's pulling the "Forest" or a future "Space" theme pack.
- Use a simple tween/easing helper (e.g., a small `lerp`-based animator) for the motion rules in Section 7, since Pygame has no built-in animation system.

---

## 10. Asset Checklist (per new theme pack)
- [ ] Background scene (layered: back/mid/foreground if parallax desired)
- [ ] Ambient particle sprite (firefly/dust/bubble/star, per theme)
- [ ] Panel fill + border texture
- [ ] Header banner shape
- [ ] Close button
- [ ] CTA button (default + pressed states)
- [ ] Icon button backgrounds ×5 (default + pressed states)
- [ ] Icon glyphs (settings, share, currency, gift, mail, or game-specific set)
- [ ] Nav arrow (left/right)
- [ ] Progress bar track + fill
- [ ] Decorative motif elements (frame accents for title/CTA)
- [ ] Display font file
- [ ] UI font file

