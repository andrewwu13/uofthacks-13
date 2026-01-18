import type { ProductData, Genre } from '../../../schema/types';

export interface LayoutProps {
    product: ProductData;
    genre: Genre;
    onAddToCart?: () => void;
    className?: string;
    showDebug?: boolean;
}
