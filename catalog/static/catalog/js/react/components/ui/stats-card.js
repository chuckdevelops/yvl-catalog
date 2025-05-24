import React from "react";
import { cn } from "../../lib/utils";
import { Card, CardContent } from "./card";

const StatsCard = React.forwardRef(
  ({ 
    className, 
    value, 
    label, 
    icon, 
    description,
    trend,
    trendValue, 
    variant = "default", 
    layout = "vertical",
    size = "default",
    animation = true,
    ...props 
  }, ref) => {
    // Modern variants with HSL colors and enhanced styling
    const variants = {
      default: {
        cardClass: "glass",
        valueClass: "text-white",
        iconClass: "text-white/70",
        gradientColors: "rgba(255,255,255,0.05), rgba(255,255,255,0.02), rgba(0,0,0,0.05)",
        accentColor: "rgba(255,255,255,0.1)"
      },
      primary: {
        cardClass: "card-primary border-primary/30",
        valueClass: "text-primary text-glow",
        iconClass: "text-primary",
        gradientColors: "rgba(244,63,94,0.03), rgba(244,63,94,0.01), rgba(244,63,94,0.07)",
        accentColor: "rgba(244,63,94,0.15)"
      },
      secondary: {
        cardClass: "card-secondary border-secondary/30",
        valueClass: "text-secondary",
        iconClass: "text-secondary/70",
        gradientColors: "rgba(35,35,35,0.1), rgba(35,35,35,0.05), rgba(0,0,0,0.05)",
        accentColor: "rgba(35,35,35,0.2)"
      },
      success: {
        cardClass: "border-success/30",
        valueClass: "text-success",
        iconClass: "text-success",
        gradientColors: "rgba(25,135,84,0.03), rgba(25,135,84,0.01), rgba(25,135,84,0.07)",
        accentColor: "rgba(25,135,84,0.15)"
      },
      warning: {
        cardClass: "border-warning/30",
        valueClass: "text-warning",
        iconClass: "text-warning",
        gradientColors: "rgba(255,193,7,0.03), rgba(255,193,7,0.01), rgba(255,193,7,0.07)",
        accentColor: "rgba(255,193,7,0.15)"
      },
      danger: {
        cardClass: "border-destructive/30",
        valueClass: "text-destructive",
        iconClass: "text-destructive",
        gradientColors: "rgba(220,53,69,0.03), rgba(220,53,69,0.01), rgba(220,53,69,0.07)",
        accentColor: "rgba(220,53,69,0.15)"
      },
      info: {
        cardClass: "border-info/30",
        valueClass: "text-info",
        iconClass: "text-info",
        gradientColors: "rgba(13,202,240,0.03), rgba(13,202,240,0.01), rgba(13,202,240,0.07)",
        accentColor: "rgba(13,202,240,0.15)"
      },
      dark: {
        cardClass: "bg-dark border-0",
        valueClass: "text-white",
        iconClass: "text-white/80",
        gradientColors: "rgba(0,0,0,0.2), rgba(0,0,0,0.1), rgba(0,0,0,0.3)",
        accentColor: "rgba(255,255,255,0.05)"
      },
      gradient: {
        cardClass: "border-0",
        valueClass: "text-gradient",
        iconClass: "text-gradient",
        gradientColors: "rgba(244,63,94,0.1), rgba(59,130,246,0.05), rgba(168,85,247,0.1)",
        accentColor: "rgba(244,63,94,0.2)",
        backgroundGradient: "linear-gradient(135deg, rgba(20,20,20,1) 0%, rgba(35,35,35,1) 100%)"
      }
    };
    
    // Size variations
    const sizes = {
      sm: {
        padding: "p-3",
        valueSize: "fs-4",
        labelSize: "fs-6",
        iconSize: "fs-4"
      },
      default: {
        padding: "p-4",
        valueSize: "fs-2",
        labelSize: "fs-6",
        iconSize: "fs-3"
      },
      lg: {
        padding: "p-5",
        valueSize: "fs-1",
        labelSize: "fs-5",
        iconSize: "fs-2"
      },
      xl: {
        padding: "p-6",
        valueSize: "display-5",
        labelSize: "fs-4",
        iconSize: "display-6"
      }
    };
    
    // Get variant and size properties
    const variantProps = variants[variant] || variants.default;
    const sizeProps = sizes[size] || sizes.default;
    
    // Layout classes
    const layoutClasses = {
      vertical: "flex-column text-center",
      horizontal: "flex-row text-start align-items-center justify-content-between"
    };
    
    // Animation classes based on layout
    const animationClasses = animation ? {
      vertical: {
        card: "fade-in",
        icon: "bounce-subtle",
        value: "scale-in",
        label: "slide-up"
      },
      horizontal: {
        card: "fade-in",
        icon: "slide-right",
        value: "slide-down",
        label: "slide-up"
      }
    } : {
      vertical: { card: "", icon: "", value: "", label: "" },
      horizontal: { card: "", icon: "", value: "", label: "" }
    };
    
    // Determine trend icon and color
    let trendIcon = null;
    let trendColor = "";
    
    if (trend === "up") {
      trendIcon = <i className="fas fa-arrow-up me-1"></i>;
      trendColor = "text-success";
    } else if (trend === "down") {
      trendIcon = <i className="fas fa-arrow-down me-1"></i>;
      trendColor = "text-destructive";
    } else if (trend === "neutral") {
      trendIcon = <i className="fas fa-minus me-1"></i>;
      trendColor = "text-muted-foreground";
    }
    
    return (
      <Card
        ref={ref}
        className={cn(
          "stats-card h-100", 
          animationClasses[layout].card,
          variantProps.cardClass,
          "hover-scale",
          className
        )}
        style={{
          overflow: "visible",
          position: "relative",
          background: variantProps.backgroundGradient || undefined,
          transition: "all 0.3s cubic-bezier(0.22, 1, 0.36, 1)",
          borderWidth: "1px",
          borderStyle: "solid",
        }}
        {...props}
      >
        <CardContent 
          className={cn(
            sizeProps.padding, 
            "d-flex", 
            layoutClasses[layout],
            "position-relative"
          )}
          style={{ zIndex: 2 }}
        >
          {/* Stats information */}
          <div className={layout === "horizontal" ? "me-auto" : ""}>
            {icon && layout === "vertical" && (
              <div className={cn(
                "stats-card-icon mb-3", 
                animationClasses[layout].icon,
                variantProps.iconClass,
                sizeProps.iconSize
              )}>
                {typeof icon === 'string' ? <i className={icon}></i> : icon}
              </div>
            )}
            
            <h2 
              className={cn(
                "fw-bold mb-1", 
                variantProps.valueClass,
                sizeProps.valueSize,
                animationClasses[layout].value
              )}
              style={{
                lineHeight: "1.2",
                letterSpacing: "-0.025em"
              }}
            >
              {value}
              
              {/* Show trend if provided */}
              {trend && trendValue && (
                <small className={cn("ms-2 fw-normal", trendColor, "fs-6")}>
                  {trendIcon} {trendValue}
                </small>
              )}
            </h2>
            
            <p className={cn(
              "text-white/70 mb-1", 
              sizeProps.labelSize,
              animationClasses[layout].label
            )}>
              {label}
            </p>
            
            {description && (
              <p className="text-white/50 small mt-2 mb-0">
                {description}
              </p>
            )}
          </div>
          
          {/* Icon for horizontal layout */}
          {icon && layout === "horizontal" && (
            <div className={cn(
              "ms-4 text-center", 
              animationClasses[layout].icon,
              variantProps.iconClass,
              sizeProps.iconSize
            )}>
              {typeof icon === 'string' ? <i className={icon}></i> : icon}
            </div>
          )}
          
          {/* Modern subtle gradient overlay */}
          <div 
            className="position-absolute top-0 start-0 w-100 h-100 pointer-events-none"
            style={{
              background: `linear-gradient(135deg, ${variantProps.gradientColors})`,
              borderRadius: "inherit",
              zIndex: -1
            }}
          />
          
          {/* Accent light effect */}
          <div 
            className="position-absolute bottom-0 end-0 pointer-events-none rounded-circle"
            style={{
              width: "80px",
              height: "80px",
              background: variantProps.accentColor,
              filter: "blur(20px)",
              opacity: "0.5",
              zIndex: -1,
              transform: "translate(20%, 20%)"
            }}
          />
        </CardContent>
      </Card>
    );
  }
);

StatsCard.displayName = "StatsCard";

export { StatsCard };