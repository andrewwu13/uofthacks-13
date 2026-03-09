import type { ProductData, Genre, BentoType } from '../../../schema/types';

export interface LayoutProps {
    product: ProductData;
    genre: Genre;
    onAddToCart?: () => void;
    className?: string;
}

export interface BentoLayoutProps extends LayoutProps {
    bentoType: BentoType;
    moduleId?: string;
    semanticId?: string;
}
