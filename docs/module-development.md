# Module Development Guide

This guide explains how to create UI modules for the schema-driven rendering system.

## Module Structure

Each module belongs to a **genre** (visual style):
- `base/` - Neutral, default styling
- `minimalist/` - Clean, typography-focused
- `neobrutalist/` - Bold, raw aesthetic
- `glassmorphism/` - Blurred glass effects
- `loud/` - High-contrast A/B testing modules

## Creating a Module

1. Create component in the appropriate genre folder
2. Register in `src/schema/registry.ts`
3. Accept props from layout schema

### Example

```tsx
// src/modules/minimalist/ProductCard.tsx
import React from 'react';
import { registerComponent } from '../../schema/registry';
import './ProductCard.css';

interface ProductCardProps {
  title: string;
  price: number;
  imageUrl: string;
}

const ProductCard: React.FC<ProductCardProps> = ({ title, price, imageUrl }) => (
  <div className="product-card minimalist">
    <img src={imageUrl} alt={title} />
    <h3>{title}</h3>
    <span className="price">${price.toFixed(2)}</span>
  </div>
);

// Register with the schema system
registerComponent('product-card', 'minimalist', ProductCard);

export default ProductCard;
```

## Module Types

| Type | Description |
|------|-------------|
| `hero` | Hero sections with headline |
| `product-grid` | Grid of product cards |
| `product-card` | Individual product card |
| `banner` | Promotional banner |
| `testimonial` | Customer testimonial |
| `cta` | Call-to-action block |
| `feature-list` | Feature showcase |

## Loud Modules

"Loud" modules are used for A/B testing. They should be:
- Visually distinct from other modules
- Designed to test specific hypotheses
- Marked with `data-is-loud="true"` attribute
