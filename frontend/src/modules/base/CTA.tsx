import { type FC } from 'react';
import { type CTAProps } from '../../schema/types';
import './CTA.css';

export const CTA: FC<CTAProps> = ({
  id,
  title,
  subtitle,
  buttonText,
  buttonLink
}) => {
  return (
    <section 
      className="cta-module" 
      data-module-id={id}
      data-module-type="cta"
    >
      <div className="cta-content">
        <h2 className="cta-title" data-track-id={`${id}_title`}>{title}</h2>
        {subtitle && <p className="cta-subtitle" data-track-id={`${id}_subtitle`}>{subtitle}</p>}
        {buttonText && (
          <a 
            href={buttonLink} 
            className="cta-button"
            data-track-id={`${id}_button`}
          >
            {buttonText}
          </a>
        )}
      </div>
      <div className="cta-bg-effect" />
    </section>
  );
};
