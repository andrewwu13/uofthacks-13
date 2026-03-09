# Plan: Copy Module Drafting Styles to Main Site

## Problem Statement
The elements in the "main" site and the module drafting site are not the same. Modules designed in the module drafting site are not rendering in the main site with the correct visual styles.

## Root Cause Analysis

### Module Drafting Site
- Location: `uofthacks-13/module-drafting-site/`
- Contains: HTML/CSS with genre-specific visual designs
- Genres: Glassmorphism, Brutalism, Neumorphism, Cyberpunk, Minimalist, Monoprint
- Module count: 36 modules (6 genres × 6 bento types)
- Key files:
  - `index.html` - Contains bento grid with 4 types: bento-hero, bento-wide, bento-tall, bento-small
  - `styles.css` - Genre-specific CSS with visual effects
  - `app.js` - JavaScript for genre switching

### Main Frontend Site
- Location: `uofthacks-13/frontend/src/`
- Contains: React components for rendering modules
- Components in `components/modules/layouts/`:
  - BentoHero.tsx
  - BentoWide.tsx
  - BentoTall.tsx
  - BentoSmall.tsx

### The Problem
In `utils/dummyData.ts`, modules are created with `Genre.BASE` (value 9):
```typescript
const genre = Genre.BASE;  // This doesn't have visual styling!
```

The ModuleRegistry correctly maps templateId to genre/bentoType, but the dummyData isn't providing proper genre values.

## Solution Plan

### Step 1: Update createProductModules() in dummyData.ts
- Replace `Genre.BASE` with cycling through drafting site genres (0-5)
- Map each product to a different genre for visual variety
- Include templateId for proper component selection

### Step 2: Update createProductBatch() in dummyData.ts
- Modify to sample from drafting site genres (0-5)
- Ensure variety in displayed modules

### Step 3: Verify ModuleRegistry Integration
- The ModuleRegistry already correctly maps templateId → genre + bentoType
- The CSS class is generated via `getModuleCssClass(id)` which combines genre + bento CSS classes
- This should work correctly once proper templateIds are provided

### Step 4: Verify CSS Application
- Genre-specific CSS exists in `index.css`:
  - `.genre-glassmorphism.bento-item` (lines 544+)
  - `.genre-brutalism.bento-item` (lines 557+)
  - `.genre-cyberpunk.bento-item` (lines 594+)
- These classes are applied via the className from ModuleRegistry

## Files to Modify

1. **`uofthacks-13/frontend/src/utils/dummyData.ts`**
   - Update `createProductModules()` to use genres 0-5
   - Update `createProductBatch()` to use genres 0-5

## Expected Result
After implementation, modules in the main site will display with the same visual styles as designed in the module drafting site:
- Glassmorphism: Translucent, blurred backgrounds with gradients
- Brutalism: Bold, high-contrast with sharp edges
- Neumorphism: Soft shadows with embossed look
- Cyberpunk: Dark theme with neon accents
- Minimalist: Clean, white-space heavy
- Monoprint: Black and white with strong typography
