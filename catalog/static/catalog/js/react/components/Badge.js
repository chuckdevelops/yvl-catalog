import React from 'react';
import './Badge.css';
import { cn } from '../lib/utils';

/**
 * Badge component that can be used throughout the application
 * 
 * @param {Object} props - Component props
 * @param {string} props.type - Type of badge (primary, secondary, info, warning, success, danger, outline)
 * @param {string} props.text - Text to display in the badge
 * @param {string} props.className - Additional CSS class names
 * @param {function} props.onClick - Optional click handler
 * @param {boolean} props.removable - Whether badge has a remove button
 * @param {function} props.onRemove - Handler for remove button click
 * @param {string} props.variant - Visual variant (modern, outline, default)
 * @param {string} props.size - Size variant (sm, md, lg)
 */
const Badge = ({ 
  type = 'primary', 
  text, 
  className = '', 
  onClick, 
  removable = false,
  onRemove,
  variant = 'default',
  size = 'default'
}) => {
  const handleRemoveClick = (e) => {
    e.stopPropagation();
    if (onRemove) onRemove();
  };

  // Determine base classes based on type and variant
  const baseClasses = {
    // Default Bootstrap classes
    default: {
      primary: 'bg-primary',
      secondary: 'bg-secondary',
      success: 'bg-success',
      info: 'bg-info',
      warning: 'bg-warning',
      danger: 'bg-danger',
      light: 'bg-light',
      dark: 'bg-dark',
      outline: 'bg-outline',
      ai: 'bg-purple'
    },
    // Modern classes with improved styling
    modern: {
      primary: 'badge-primary',
      secondary: 'badge-secondary',
      success: 'badge-success',
      info: 'badge-info',
      warning: 'badge-warning',
      danger: 'badge-destructive',
      light: 'badge-light',
      dark: 'badge-dark',
      outline: 'badge-outline',
      ai: 'badge-ai'
    },
    // Outline variants
    outline: {
      primary: 'badge-outline-primary',
      secondary: 'badge-outline-secondary',
      success: 'badge-outline-success',
      info: 'badge-outline-info',
      warning: 'badge-outline-warning',
      danger: 'badge-outline-danger',
      light: 'badge-outline-light',
      dark: 'badge-outline-dark',
      ai: 'badge-outline-ai'
    }
  };

  // Size classes
  const sizeClasses = {
    sm: 'badge-sm',
    default: '',
    md: 'badge-md',
    lg: 'badge-lg'
  };
  
  // Get the appropriate class based on variant and type
  const badgeClassMap = baseClasses[variant] || baseClasses.default;
  const badgeClass = badgeClassMap[type] || badgeClassMap.primary;
  const sizeClass = sizeClasses[size] || '';
  
  // Visual effects for modern variant
  const modernEffects = variant === 'modern' ? 'hover-scale fade-in' : '';
  
  // Compose all classes
  const classes = cn(
    'badge',
    'react-badge',
    badgeClass,
    sizeClass,
    modernEffects,
    onClick ? 'clickable' : '',
    className
  );
  
  return (
    <span 
      className={classes}
      onClick={onClick}
    >
      {text}
      {removable && (
        <button 
          type="button" 
          className="badge-remove-btn ms-1"
          onClick={handleRemoveClick}
          aria-label={`Remove ${text}`}
        >
          ×
        </button>
      )}
    </span>
  );
};

export default Badge;