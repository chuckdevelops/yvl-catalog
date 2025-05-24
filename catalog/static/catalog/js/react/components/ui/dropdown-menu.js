import React, { useState, useRef, useEffect } from "react";
import { cn } from "../../lib/utils";

const DropdownMenu = React.forwardRef(
  ({ className, children, ...props }, ref) => {
    const [open, setOpen] = useState(false);
    const menuRef = useRef(null);

    useEffect(() => {
      const handleClickOutside = (event) => {
        if (menuRef.current && !menuRef.current.contains(event.target)) {
          setOpen(false);
        }
      };

      document.addEventListener("mousedown", handleClickOutside);
      return () => {
        document.removeEventListener("mousedown", handleClickOutside);
      };
    }, []);

    return (
      <div 
        ref={menuRef}
        className={cn("dropdown", className)} 
        {...props}
      >
        {React.Children.map(children, child => {
          if (child.type === DropdownMenuTrigger) {
            return React.cloneElement(child, { 
              onClick: () => setOpen(!open),
              "aria-expanded": open
            });
          }
          if (child.type === DropdownMenuContent) {
            return React.cloneElement(child, { 
              className: cn(child.props.className, { "show": open }),
              style: { display: open ? "block" : "none" }
            });
          }
          return child;
        })}
      </div>
    );
  }
);
DropdownMenu.displayName = "DropdownMenu";

const DropdownMenuTrigger = React.forwardRef(
  ({ className, children, ...props }, ref) => (
    <button 
      ref={ref}
      className={cn("dropdown-toggle", className)} 
      type="button"
      data-bs-toggle="dropdown"
      {...props}
    >
      {children}
    </button>
  )
);
DropdownMenuTrigger.displayName = "DropdownMenuTrigger";

const DropdownMenuContent = React.forwardRef(
  ({ className, children, ...props }, ref) => (
    <ul
      ref={ref}
      className={cn("dropdown-menu", className)}
      {...props}
    >
      {children}
    </ul>
  )
);
DropdownMenuContent.displayName = "DropdownMenuContent";

const DropdownMenuItem = React.forwardRef(
  ({ className, children, ...props }, ref) => (
    <li>
      <a
        ref={ref}
        className={cn("dropdown-item", className)}
        {...props}
      >
        {children}
      </a>
    </li>
  )
);
DropdownMenuItem.displayName = "DropdownMenuItem";

const DropdownMenuSeparator = React.forwardRef(
  ({ className, ...props }, ref) => (
    <li>
      <hr className={cn("dropdown-divider", className)} ref={ref} {...props} />
    </li>
  )
);
DropdownMenuSeparator.displayName = "DropdownMenuSeparator";

export { 
  DropdownMenu, 
  DropdownMenuTrigger, 
  DropdownMenuContent, 
  DropdownMenuItem,
  DropdownMenuSeparator
};