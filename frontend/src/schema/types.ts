export interface DesignTokenOverrides {
  colors?: Record<string, string>;
  typography?: Record<string, string>;
  spacing?: Record<string, string>;
  borderRadius?: Record<string, string>;
}

export interface LayoutModule {
  id: string;
  type: string;
  genre: 'base' | 'minimalist' | 'neobrutalist' | 'glassmorphism' | 'loud';
  props?: Record<string, any>;
  data?: Record<string, any>;
  variants?: Record<string, any>;
}

export interface LayoutSection {
  id: string;
  type: string; // e.g., 'full-width', 'container', 'grid'
  modules: LayoutModule[];
  styles?: Record<string, string>;
}

export interface LayoutSchema {
  id: string;
  name: string;
  sections: LayoutSection[];
  design_system_overrides?: DesignTokenOverrides;
}

// Module Props Interfaces

export interface HeroProps {
  id: string;
  title: string;
  subtitle: string;
  backgroundImage?: string;
  ctaText?: string;
  ctaLink?: string;
}

export interface ProductCardProps {
  id: string;
  title: string;
  price: string;
  image: string;
  currency?: string;
  onAddToCart?: () => void;
}

export interface ProductGridProps {
  id: string;
  title?: string;
  products?: Array<{
    id: string;
    title: string;
    price: string;
    image: string;
  }>;
  columns?: number;
}

export interface CTAProps {
  id: string;
  title: string;
  subtitle?: string;
  buttonText?: string;
  buttonLink?: string;
}
