import React from 'react';
import { cn } from '../../lib/utils';

const Badge = React.forwardRef(({
  className,
  variant = "default",
  ...props
}, ref) => {
  return (
    <div
      ref={ref}
      className={cn(
        "inline-flex items-center rounded-full px-2.5 py-0.5 text-xs font-semibold transition-colors",
        "focus:outline-none focus:ring-2 focus:ring-ring focus:ring-offset-2",
        
        // Variants
        variant === "default" && 
          "bg-primary text-primary-foreground hover:bg-primary/80",
        variant === "secondary" && 
          "bg-secondary text-secondary-foreground hover:bg-secondary/80",
        variant === "destructive" && 
          "bg-destructive text-destructive-foreground hover:bg-destructive/80",
        variant === "outline" && 
          "text-foreground border border-input hover:bg-accent hover:text-accent-foreground",
        variant === "carti" && 
          "bg-red-600 text-white hover:bg-red-700",
        variant === "glass" && 
          "carti-glass text-white hover:bg-white/10",
        variant === "emoji" && 
          "bg-blue-500 text-white hover:bg-blue-600",
          
        className
      )}
      {...props}
    />
  );
});
Badge.displayName = "Badge";

export { Badge };