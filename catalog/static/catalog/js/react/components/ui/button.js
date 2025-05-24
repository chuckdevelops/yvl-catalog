import React from "react";
import { cn } from "../../lib/utils";

// Define button variants and sizes - updated for modern shadcn/ui styling
const buttonVariants = {
  variant: {
    default: "btn btn-secondary hover-lift hover-glow scale-in",
    primary: "btn btn-primary hover-lift hover-glow scale-in",
    secondary: "btn btn-secondary hover-lift hover-glow scale-in",
    destructive: "btn btn-danger hover-lift hover-glow scale-in",
    outline: "btn btn-outline-secondary hover-lift scale-in",
    ghost: "btn btn-outline-secondary hover-lift scale-in",
    link: "btn btn-link hover-scale scale-in",
    // Modern variants
    glass: "btn glass hover-lift hover-glow scale-in",
    gradient: "btn text-gradient hover-lift hover-bright scale-in",
    accent: "btn bg-accent hover-lift hover-glow text-white scale-in",
    // New shadcn/ui-inspired variants
    muted: "btn btn-dark text-muted hover-lift",
    success: "btn btn-success hover-lift hover-glow scale-in",
    warning: "btn btn-warning hover-lift hover-glow scale-in",
    info: "btn btn-info hover-lift hover-glow scale-in"
  },
  size: {
    default: "",
    sm: "btn-sm",
    lg: "btn-lg fs-5 py-2 px-4",
    xl: "btn-lg fs-4 py-3 px-5",
    icon: "p-2 d-inline-flex align-items-center justify-content-center",
    // New shadcn/ui-inspired sizes
    xs: "btn-sm py-1 px-2 fs-6",
    "2xl": "btn-lg fs-3 py-4 px-6"
  }
};

// Create button component with variants - enhanced with modern interactions
const Button = React.forwardRef(
  ({ className, variant = "default", size = "default", asChild = false, withRipple = true, isLoading = false, icon, iconPosition = "left", ...props }, ref) => {
    const Comp = asChild ? props.as || "a" : "button";
    const buttonRef = React.useRef(null);
    
    // Enhanced ripple effect handler
    const handleRipple = React.useCallback((event) => {
      if (!withRipple) return;
      
      const button = buttonRef.current;
      if (!button) return;
      
      const rect = button.getBoundingClientRect();
      const x = event.clientX - rect.left;
      const y = event.clientY - rect.top;
      
      const circle = document.createElement('span');
      circle.className = 'ripple-effect';
      circle.style.left = `${x}px`;
      circle.style.top = `${y}px`;
      
      // Use larger ripple for bigger buttons
      if (size === "lg" || size === "xl" || size === "2xl") {
        circle.style.width = '150px';
        circle.style.height = '150px';
        circle.style.marginTop = '-75px';
        circle.style.marginLeft = '-75px';
      }
      
      button.appendChild(circle);
      
      setTimeout(() => {
        circle.remove();
      }, 600);
    }, [withRipple, size]);
    
    React.useImperativeHandle(ref, () => buttonRef.current);
    
    // Prepare content with icon if provided
    const content = (
      <>
        {isLoading && (
          <span className="spinner-border spinner-border-sm me-2" role="status" aria-hidden="true"></span>
        )}
        
        {!isLoading && icon && iconPosition === "left" && (
          <span className="me-2">{typeof icon === 'string' ? <i className={icon}></i> : icon}</span>
        )}
        
        {props.children}
        
        {!isLoading && icon && iconPosition === "right" && (
          <span className="ms-2">{typeof icon === 'string' ? <i className={icon}></i> : icon}</span>
        )}
      </>
    );
    
    return (
      <Comp
        ref={buttonRef}
        className={cn(
          buttonVariants.variant[variant],
          buttonVariants.size[size],
          withRipple && "position-relative overflow-hidden",
          isLoading && "opacity-75 cursor-not-allowed",
          className
        )}
        disabled={isLoading || props.disabled}
        onClick={(e) => {
          if (!isLoading && !props.disabled) {
            handleRipple(e);
            if (props.onClick) props.onClick(e);
          }
        }}
        {...props}
        type={props.type || (Comp === "button" ? "button" : undefined)}
      >
        {content}
      </Comp>
    );
  }
);

Button.displayName = "Button";

export { Button, buttonVariants };