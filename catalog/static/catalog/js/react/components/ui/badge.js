import React from "react";
import { cn } from "../../lib/utils";

// Enhanced badge variants with modern styling
const badgeVariants = {
  primary: "bg-white/15 text-white border border-white/20 hover-scale slide-up backdrop-blur-sm",
  secondary: "bg-black/50 text-white/90 border border-white/10 hover-scale slide-up backdrop-blur-sm",
  info: "bg-blue-500/20 text-white/90 border border-blue-500/30 hover-scale slide-up backdrop-blur-sm",
  success: "bg-green-500/20 text-white/90 border border-green-500/30 hover-scale slide-up backdrop-blur-sm",
  warning: "bg-yellow-500/20 text-white/90 border border-yellow-500/30 hover-scale slide-up backdrop-blur-sm",
  danger: "bg-red-500/20 text-white/90 border border-red-500/30 hover-scale slide-up backdrop-blur-sm",
  destructive: "bg-red-500/20 text-white/90 border border-red-500/30 hover-scale slide-up backdrop-blur-sm",
  outline: "bg-transparent text-white border border-white/30 hover-scale slide-up",
  'outline-secondary': "bg-transparent text-white/70 border border-white/20 hover-scale slide-up",
  ai: "bg-purple-500/20 text-white/90 border border-purple-500/30 hover-scale slide-up backdrop-blur-sm text-glow",
  muted: "bg-white/5 text-white/70 border border-white/10 hover-scale slide-up backdrop-blur-sm",
  gradient: "bg-gradient-to-r from-primary/20 to-accent/20 text-white border border-white/10 hover-scale slide-up backdrop-blur-sm text-glow",
  glass: "glass text-white border border-white/20 hover-scale slide-up"
};

// Badge sizes for more flexibility
const badgeSizes = {
  xs: "px-1.5 py-0 text-xxs",
  sm: "px-2 py-0.25 text-xs",
  default: "px-2.5 py-0.5 text-xs",
  md: "px-3 py-1 text-sm",
  lg: "px-4 py-1.5 text-sm font-medium",
  pill: "rounded-full px-3 py-0.5 text-xs"
};

// Modern Badge component
const Badge = React.forwardRef(
  ({ 
    className, 
    variant = "primary", 
    size = "default",
    icon,
    iconPosition = "left",
    glow = false,
    animation = "slide-up",
    children, 
    removable = false, 
    onRemove, 
    ...props 
  }, ref) => {
    const handleRemove = (e) => {
      e.stopPropagation();
      if (onRemove) onRemove(e);
    };

    // Get size class
    const sizeClass = badgeSizes[size] || badgeSizes.default;
    
    return (
      <span
        ref={ref}
        className={cn(
          "d-inline-flex align-items-center rounded-2 font-medium transition-all",
          badgeVariants[variant],
          sizeClass,
          glow && "text-glow",
          animation,
          removable ? "pe-1" : "",
          className
        )}
        {...props}
      >
        {/* Icon on left side if specified */}
        {icon && iconPosition === "left" && (
          <span className="me-1 d-inline-flex">
            {typeof icon === 'string' ? <i className={icon}></i> : icon}
          </span>
        )}
        
        {children}
        
        {/* Icon on right side if specified */}
        {icon && iconPosition === "right" && (
          <span className="ms-1 d-inline-flex">
            {typeof icon === 'string' ? <i className={icon}></i> : icon}
          </span>
        )}
        
        {/* Remove button */}
        {removable && (
          <button
            className="ms-1 rounded-circle bg-transparent hover:bg-white/20 p-0 border-0 hover-scale"
            onClick={handleRemove}
            aria-label="Remove badge"
            style={{
              width: "16px",
              height: "16px",
              display: "inline-flex",
              alignItems: "center",
              justifyContent: "center"
            }}
            type="button"
          >
            <svg width="12" height="12" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
              <path d="M18 6L6 18M6 6L18 18" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" />
            </svg>
          </button>
        )}
      </span>
    );
  }
);

Badge.displayName = "Badge";

export { Badge, badgeVariants };