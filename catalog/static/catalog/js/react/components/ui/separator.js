import React from "react";
import { cn } from "../../lib/utils";

const Separator = React.forwardRef((
  { className, orientation = "horizontal", decorative = true, ...props },
  ref
) => (
  <div
    ref={ref}
    className={cn(
      "shrink-0 bg-white/10",
      orientation === "horizontal" ? "h-[1px] w-full" : "h-full w-[1px]",
      className
    )}
    {...props}
    aria-orientation={orientation}
    role={decorative ? "none" : "separator"}
  />
));
Separator.displayName = "Separator";

export { Separator };
