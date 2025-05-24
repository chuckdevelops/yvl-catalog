import React from "react";
import { cn } from "../../lib/utils";

const Avatar = React.forwardRef(
  ({ className, src, alt = "", fallback, ...props }, ref) => {
    const [hasError, setHasError] = React.useState(false);

    const handleError = () => {
      setHasError(true);
    };

    return (
      <div
        ref={ref}
        className={cn("avatar", className)}
        {...props}
      >
        {!hasError && src ? (
          <img 
            src={src} 
            alt={alt} 
            className="avatar-img rounded-circle" 
            onError={handleError}
          />
        ) : (
          <div className="avatar-fallback rounded-circle d-flex align-items-center justify-content-center bg-secondary text-white">
            {fallback || alt.slice(0, 2) || "?"}
          </div>
        )}
      </div>
    );
  }
);

Avatar.displayName = "Avatar";

export { Avatar };