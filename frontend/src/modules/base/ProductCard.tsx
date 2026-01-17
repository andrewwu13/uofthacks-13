import { type FC } from 'react';
import { type ProductCardProps } from '../../schema/types';
import './ProductCard.css';

export const ProductCard: FC<ProductCardProps> = ({
  id,
  title,
  price,
  image,
  currency = 'USD',
  onAddToCart
}) => {
  return (
    <div className="product-card" data-module-id={id} data-module-type="product-card" data-module-genre="base">
      <div className="product-image-container">
        <img src={image} alt={title} className="product-image" loading="lazy" />
        <div className="product-overlay">
          <button 
            className="quick-view-btn"
            data-track-id={`${id}_quickview`}
          >
            Quick View
          </button>
        </div>
      </div>
      
      <div className="product-info">
        <h3 className="product-title" data-track-id={`${id}_title`}>{title}</h3>
        
        {/* Frustration Signal: Price Context */}
        <div 
          className="product-price" 
          data-track-context="price"
          data-track-id={`${id}_price`}
        >
          <span className="currency">{currency}</span>
          <span className="amount">{price}</span>
        </div>
        
        <button 
          className="add-to-cart-btn"
          onClick={onAddToCart}
          data-track-id={`${id}_add_cart`}
        >
          Add to Cart
        </button>
      </div>
    </div>
  );
};
