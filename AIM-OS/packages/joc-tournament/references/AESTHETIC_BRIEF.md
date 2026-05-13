# J.A.R.V.I.S. Aesthetic Standard — "The Instrument Brief"

```
  This is not a web app. This is a precision instrument.
  Every surface has purpose. Every pixel is machined.
```

---

## The Reference Objects

Braden provided three reference images that define the aesthetic DNA:

1. **Panavision DXL-262** — $150K cinema camera
   - Matte black with subtle surface texture variation
   - Recessed LCD status panel showing dense telemetry (timecode, FPS, ISO, shutter, color temp)
   - Machined aluminum controls with purposeful knurling
   - Small, unmistakable status LEDs (green/red)
   - Every control is functional — zero decoration

2. **Hasselblad X2D** — $8K medium format camera
   - Single amber accent button against total matte black
   - Engraved typography — permanent, confident, not painted-on
   - Tactile dial with precise detents
   - Small monochrome OLED status display
   - Premium grip material contrast against machined body

3. **Military-spec Panavision DXL rig** — field-grade assembly
   - Picatinny rail modularity (everything mounts, everything configures)
   - Dense information on tiny displays
   - Built to survive deployment — robust, not delicate
   - Multiple subsystems unified into one coherent instrument
   - Hamilton optics module on top = specialist tool mounted to platform

---

## Design DNA — What This Means for J.A.R.V.I.S.

### Material Language
- **Matte black is the base** — but NOT flat CSS `#000`. Use subtle gradients, micro-noise textures, and surface depth to simulate machined aluminum vs rubberized grip vs glass display
- **One warm accent color** — amber/orange (#F5A623 range) used ONLY for primary actions and critical status. Everything else is neutral.
- **Recessed displays** — panels should feel like LCD readouts set INTO the surface, not floating cards on top of it
- **Beveled edges** — not rounded-corner cards. Inner shadows, chamfered borders, inset styling

### Typography
- **Engraved feel** — uppercase labels, tight tracking, subtle text-shadow that simulates laser etching
- **Monospace for data** — timecodes, IDs, status values in monospace font (JetBrains Mono, IBM Plex Mono)
- **Sans-serif for labels** — Inter or similar, small size, uppercase, high contrast against dark surface

### Information Density
- **Dense but hierarchical** — like the Panavision status display: FPS, ISO, shutter, color temp, timecode ALL visible in one small recessed area
- **No whitespace for whitespace's sake** — every gap must be structural (panel border, zone separator), not decorative
- **Status indicators are small but unmistakable** — 8px dots, not large badges. The Panavision uses tiny LEDs.

### Controls
- **Knobs, toggles, switches** — the Surface Engine components (SkeuKnob, SkeuToggle, SkeuButton) exist for this exact reason
- **Press depth** — buttons should feel like they depress into the surface when clicked
- **Knurled textures** — subtle CSS patterns on interactive edges (grip areas, drag handles)

### Color Palette
```
Background:       #0A0A0C (near-black with blue undertone)
Surface Level 1:  #111114 (panel backgrounds)
Surface Level 2:  #1A1A1E (raised elements)
Surface Level 3:  #222228 (hover states, active areas)
Border:           #2A2A30 (subtle, machined-edge feel)
Text Primary:     #E8E8EC (95% white, not pure)
Text Secondary:   #888890 (engraved label feel)
Text Tertiary:    #555560 (ghost text, disabled)
Accent Warm:      #F5A623 (the Hasselblad button — primary action)
Accent Cool:      #3B82F6 (blue — informational)
Status Live:      #22C55E (green LED)
Status Warning:   #F59E0B (amber LED)
Status Critical:  #EF4444 (red LED)
Status Offline:   #6B7280 (dim gray)
```

### The Test
> If you put a screenshot of J.A.R.V.I.S. next to a photo of the Panavision DXL control panel, they should feel like they belong to the same design language. One is physical, one is digital, but the DNA is identical: **precision, density, purpose, and material confidence.**

---

## What This Is NOT

| ❌ Not This | ✅ This Instead |
|------------|----------------|
| Glassmorphism / frosted glass | Machined matte surfaces |
| Neon glow / sci-fi cosplay | Amber accent on matte black |
| Large rounded cards | Recessed panels with beveled edges |
| Thin hairline borders | Structural borders with depth |
| Gratuitous animations | Purposeful motion (press, reveal, status pulse) |
| Flat dark mode (#121212) | Textured dark with surface variation |
| Colorful dashboards | Monochrome with targeted color for status |
| Generic admin panels | Instrument-grade control surfaces |

---

*Build an instrument, not an app.*
