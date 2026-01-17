import { type FC } from 'react';
import { type HeroProps } from '../../schema/types';
import './Hero.css';

export const Hero: FC<HeroProps> = ({
  id,
  title,
  subtitle,
  backgroundImage,
  ctaText,
  ctaLink
}) => {
  return (
    <section 
      className="hero-module" 
      data-module-id={id}
      data-module-type="hero"
      data-module-genre="base"
      style={{ backgroundImage: backgroundImage ? `url(${backgroundImage})` : undefined }}
    >
      <div className="hero-overlay" />
      <div className="hero-content">
        <h1 className="hero-title" data-track-id={`${id}_title`}>{title}</h1>
        <p className="hero-subtitle" data-track-id={`${id}_subtitle`}>{subtitle}</p>
        {ctaText && (
          <a 
            href={ctaLink || '#'} 
            className="hero-cta"
            data-track-id={`${id}_cta`}
            role="button"
          >
            {ctaText}
          </a>
        )}
      </div>
    </section>
  );
};
