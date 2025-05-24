import React from "react";
import { cn } from "../../lib/utils";

// Card component with enhanced variants and modern styling
const Card = React.forwardRef(
  ({ 
    className, 
    variant = "default", 
    size = "default", 
    hover = true, 
    animation = "fade-in", 
    glassmorphism = true, 
    withShadow = true,
    ...props
  }, ref) => {
    // Card variants
    const cardVariants = {
      default: "card mb-4 bg-dark-card",
      primary: "card mb-4 border-primary",
      secondary: "card mb-4 border-secondary",
      accent: "card mb-4 border-accent",
      destructive: "card mb-4 border-destructive",
      success: "card mb-4 border-success",
      warning: "card mb-4 border-warning",
      info: "card mb-4 border-info",
      muted: "card mb-4 bg-muted border-0"
    };
    
    // Card sizes
    const cardSizes = {
      default: "",
      sm: "p-3",
      lg: "p-5",
      compact: "p-2",
      expanded: "p-6"
    };
    
    // Card hover effects
    const hoverEffects = hover ? "hover-scale" : "";
    
    return (
      <div
        ref={ref}
        className={cn(
          cardVariants[variant],
          cardSizes[size],
          glassmorphism && "glass",
          animation,
          hoverEffects,
          className
        )}
        style={{
          backdropFilter: glassmorphism ? "blur(12px)" : undefined,
          WebkitBackdropFilter: glassmorphism ? "blur(12px)" : undefined,
          boxShadow: withShadow ? "0 8px 30px rgba(0, 0, 0, 0.25)" : undefined,
          transition: "all 0.3s cubic-bezier(0.22, 1, 0.36, 1)",
          border: "1px solid hsla(var(--border), 0.8)"
        }}
        {...props}
      />
    );
  }
);
Card.displayName = "Card";

// Enhanced CardHeader with more formatting options
const CardHeader = React.forwardRef(
  ({ 
    className, 
    variant = "default", 
    alignment = "between", 
    animation = "slide-down", 
    ...props 
  }, ref) => {
    // Header variants
    const headerVariants = {
      default: "bg-dark-card",
      transparent: "bg-transparent",
      accent: "bg-accent",
      primary: "bg-primary",
      muted: "bg-muted"
    };
    
    // Alignment options
    const alignmentOptions = {
      between: "justify-content-between",
      start: "justify-content-start",
      center: "justify-content-center",
      end: "justify-content-end"
    };
    
    return (
      <div
        ref={ref}
        className={cn(
          "card-header",
          headerVariants[variant],
          animation,
          className
        )}
        style={{
          display: "flex",
          alignItems: "center",
          justifyContent: alignmentOptions[alignment],
          borderBottom: "1px solid hsla(var(--border), 0.8)"
        }}
        {...props}
      />
    );
  }
);
CardHeader.displayName = "CardHeader";

// Enhanced CardTitle with typography options
const CardTitle = React.forwardRef(
  ({ 
    className, 
    size = "default", 
    glow = true, 
    animation = "slide-right", 
    ...props 
  }, ref) => {
    // Title sizes
    const titleSizes = {
      sm: "fs-5",
      default: "fs-4",
      lg: "fs-3",
      xl: "fs-2"
    };
    
    return (
      <h3
        ref={ref}
        className={cn(
          titleSizes[size],
          "fw-semibold",
          "d-block",
          "mb-2",
          glow && "text-glow",
          animation,
          className
        )}
        style={{
          letterSpacing: "-0.025em",
          lineHeight: 1.2
        }}
        {...props}
      />
    );
  }
);
CardTitle.displayName = "CardTitle";

// Enhanced CardDescription
const CardDescription = React.forwardRef(
  ({ 
    className, 
    muted = true, 
    animation = "slide-up", 
    ...props 
  }, ref) => (
    <p
      ref={ref}
      className={cn(
        "fs-6",
        muted && "text-white/70",
        animation,
        className
      )}
      style={{
        marginBottom: "0.5rem"
      }}
      {...props}
    />
  )
);
CardDescription.displayName = "CardDescription";

// Enhanced CardContent with padding options
const CardContent = React.forwardRef(
  ({ 
    className, 
    noPadding = false, 
    animation = "scale-in", 
    ...props 
  }, ref) => (
    <div 
      ref={ref} 
      className={cn(
        !noPadding && "card-body",
        animation,
        className
      )} 
      style={{
        position: "relative",
        zIndex: 1
      }}
      {...props} 
    />
  )
);
CardContent.displayName = "CardContent";

// Enhanced CardFooter with alignment
const CardFooter = React.forwardRef(
  ({ 
    className, 
    alignment = "between", 
    bordered = true, 
    animation = "slide-up", 
    ...props 
  }, ref) => {
    // Alignment options
    const alignmentOptions = {
      between: "justify-content-between",
      start: "justify-content-start",
      center: "justify-content-center",
      end: "justify-content-end"
    };
    
    return (
      <div
        ref={ref}
        className={cn(
          "card-footer",
          bordered && "border-light",
          animation,
          className
        )}
        style={{
          position: "relative",
          zIndex: 1,
          display: "flex",
          alignItems: "center",
          justifyContent: alignmentOptions[alignment]
        }}
        {...props}
      />
    );
  }
);
CardFooter.displayName = "CardFooter";

// New card components for advanced layouts
const CardActions = React.forwardRef(
  ({ className, ...props }, ref) => (
    <div
      ref={ref}
      className={cn(
        "d-flex flex-wrap gap-2 align-items-center justify-content-end mt-3",
        className
      )}
      {...props}
    />
  )
);
CardActions.displayName = "CardActions";

const CardMedia = React.forwardRef(
  ({ className, src, alt = "", aspectRatio = "16/9", position = "top", ...props }, ref) => {
    // Position options
    const positionStyles = {
      top: { 
        borderRadius: "calc(var(--radius) - 2px) calc(var(--radius) - 2px) 0 0",
        marginBottom: "1rem"
      },
      bottom: { 
        borderRadius: "0 0 calc(var(--radius) - 2px) calc(var(--radius) - 2px)",
        marginTop: "1rem"
      },
      full: {
        borderRadius: "calc(var(--radius) - 2px)",
        margin: "0"
      }
    };
    
    return (
      <div
        ref={ref}
        className={cn(
          "card-img-container position-relative overflow-hidden",
          className
        )}
        style={{
          aspectRatio,
          ...positionStyles[position]
        }}
      >
        <img
          src={src}
          alt={alt}
          className="card-img w-100 h-100 object-fit-cover"
          {...props}
        />
      </div>
    );
  }
);
CardMedia.displayName = "CardMedia";

// Export all card components
export { 
  Card, 
  CardHeader, 
  CardFooter, 
  CardTitle, 
  CardDescription, 
  CardContent,
  CardActions,
  CardMedia
};