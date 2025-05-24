import React from "react";
import { cn } from "../../lib/utils";
import { Card, CardHeader, CardContent } from "./card";

const ContentBox = React.forwardRef(
  ({ 
    className, 
    title,
    icon,
    children,
    variant = "default",
    ...props 
  }, ref) => {
    const variants = {
      default: "",
      info: "border-info",
      warning: "border-warning",
      success: "border-success",
      danger: "border-danger"
    };
    
    return (
      <Card 
        ref={ref} 
        className={cn("content-box", variants[variant], className)} 
        {...props}
      >
        <CardHeader className="d-flex align-items-center">
          {icon && <span className="me-2">{icon}</span>}
          <h3 className="mb-0">{title}</h3>
        </CardHeader>
        <CardContent>
          {children}
        </CardContent>
      </Card>
    );
  }
);
ContentBox.displayName = "ContentBox";

export { ContentBox };