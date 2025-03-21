import React from 'react';

export const Badge = ({ children, variant = 'primary', size = 'md' }) => {
  const getVariantStyles = () => {
    switch (variant) {
      case 'primary':
        return {
          background: 'var(--c-primary, #333)',
          color: 'var(--c-primary-on, #fff)'
        };
      case 'secondary':
        return {
          background: 'var(--c-secondary, #666)',
          color: 'var(--c-secondary-on, #fff)'
        };
      case 'outline':
        return {
          background: 'transparent',
          color: 'var(--text-muted, #666)',
          border: '1px solid currentColor'
        };
      default:
        return {
          background: 'var(--c-primary, #333)',
          color: 'var(--c-primary-on, #fff)'
        };
    }
  };

  const getSizeStyles = () => {
    switch (size) {
      case 'sm':
        return {
          fontSize: '0.65rem',
          padding: '0.15rem 0.35rem'
        };
      case 'lg':
        return {
          fontSize: '0.85rem',
          padding: '0.35rem 0.75rem'
        };
      default: // md
        return {
          fontSize: '0.75rem',
          padding: '0.25rem 0.5rem'
        };
    }
  };

  const variantStyles = getVariantStyles();
  const sizeStyles = getSizeStyles();

  return (
    <span className="badge">
      {children}
      <style jsx>{`
        .badge {
          display: inline-flex;
          align-items: center;
          border-radius: 9999px;
          font-weight: 500;
          letter-spacing: 0.05em;
          text-transform: uppercase;
          font-size: ${sizeStyles.fontSize};
          padding: ${sizeStyles.padding};
          background-color: ${variantStyles.background};
          color: ${variantStyles.color};
          ${variantStyles.border ? `border: ${variantStyles.border};` : ''}
          white-space: nowrap;
        }
      `}</style>
    </span>
  );
};