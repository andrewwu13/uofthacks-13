import { type FC } from 'react';
import { type ProductGridProps } from '../../schema/types';
import { ProductCard } from './ProductCard';
import './ProductGrid.css';

// Mock data for development
const MOCK_PRODUCTS = [
  { id: 'p1', title: 'Running Essentials', price: '$45.00', image: 'https://images.unsplash.com/photo-1571019614242-c5c5dee9f50b?w=500' },
  { id: 'p2', title: 'Utility Jacket', price: '$120.00', image: 'https://images.unsplash.com/photo-1591047139829-d91aecb6caea?w=500' },
  { id: 'p3', title: 'Carbon Runner', price: '$180.00', image: 'https://images.unsplash.com/photo-1606107557195-0e29a4b5b4aa?w=500' },
  { id: 'p4', title: 'Smart Watch', price: '$299.00', image: 'https://images.unsplash.com/photo-1523275335684-37898b6baf30?w=500' },
];

export const ProductGrid: FC<ProductGridProps> = ({
  id,
  title,
  products = MOCK_PRODUCTS, // Use mock if not provided
  // columns = 4 // Unused for now
}) => {
  return (
    <section 
      className="product-grid-module" 
      data-module-id={id}
      data-module-type="product-grid"
    >
      <div className="container">
        {title && <h2 className="section-title" data-track-id={`${id}_header`}>{title}</h2>}
        
        <div 
          className="grid-layout"
          style={{ gridTemplateColumns: `repeat(auto-fit, minmax(280px, 1fr))` }}
        >
          {products.map((product) => (
            <ProductCard
              key={product.id}
              {...product}
              currency="USD"
              onAddToCart={() => console.log('Added', product.id)}
            />
          ))}
        </div>
      </div>
    </section>
  );
};
