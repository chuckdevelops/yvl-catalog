import React from "react";
import { cn } from "../../lib/utils";

const List = React.forwardRef(
  ({ className, variant = "default", ...props }, ref) => {
    const variants = {
      default: "list-group",
      flush: "list-group list-group-flush",
      horizontal: "list-group list-group-horizontal",
      numbered: "list-group list-group-numbered",
    };

    return (
      <ul
        ref={ref}
        className={cn(variants[variant], className)}
        {...props}
      />
    );
  }
);
List.displayName = "List";

const ListItem = React.forwardRef(
  ({ className, asChild, active = false, disabled = false, action = false, ...props }, ref) => {
    const Comp = asChild ? React.Children.only(props.children).type : "li";
    
    return (
      <Comp
        ref={ref}
        className={cn(
          "list-group-item",
          active && "active",
          disabled && "disabled",
          action && "list-group-item-action",
          className
        )}
        {...props}
        aria-disabled={disabled ? true : undefined}
        aria-selected={active ? true : undefined}
      />
    );
  }
);
ListItem.displayName = "ListItem";

export { List, ListItem };