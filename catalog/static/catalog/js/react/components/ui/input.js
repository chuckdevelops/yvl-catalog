import React from "react";
import { cn } from "../../lib/utils";

// Input variants 
const inputVariants = {
  default: "border bg-transparent",
  ghost: "bg-transparent border-0 shadow-none",
  plain: "bg-transparent border-white/10",
  filled: "bg-dark border-dark",
  outline: "bg-transparent border-white/30",
  "with-ring": "with-focus-ring" // Custom class for focus ring effect
};

// Input sizes
const inputSizes = {
  xs: "h-7 px-2 py-0 text-xs",
  sm: "h-8 px-2 py-0.5 text-sm",
  default: "h-9 px-3 py-1 text-sm",
  lg: "h-10 px-4 py-2 text-base",
  xl: "h-12 px-5 py-3 text-lg"
};

// Enhanced Input component with modern styling
const Input = React.forwardRef(
  ({ 
    className, 
    variant = "default", 
    size = "default",
    type = "text", 
    error, 
    icon,
    iconPosition = "left",
    rounded = false,
    glassmorphism = false,
    label,
    hint,
    animation = "fade-in",
    ...props 
  }, ref) => {
    // Generate unique ID for the input if needed for label
    const id = React.useId();
    
    // Base input styles that apply to all variants
    const baseInputStyles = cn(
      "flex w-full rounded-md shadow-sm transition-colors",
      "focus:outline-none focus:ring-1 focus:ring-white/30 focus:border-white/30",
      "placeholder:text-white/50 disabled:cursor-not-allowed disabled:opacity-50"
    );
    
    // Combine all input classes
    const inputClasses = cn(
      baseInputStyles,
      inputVariants[variant],
      inputSizes[size],
      error && "border-red-500 focus:border-red-500 focus:ring-red-500/30",
      rounded && "rounded-full",
      glassmorphism && "backdrop-blur-sm",
      iconPosition === "left" && icon && "pl-9",
      iconPosition === "right" && icon && "pr-9",
      animation,
      className
    );
    
    // Input with all variations
    const inputElement = (
      <div className="input-wrapper">
        {/* Input Label */}
        {label && (
          <label htmlFor={id} className="block text-sm font-medium text-white/70 mb-1.5 slide-up">
            {label}
          </label>
        )}
        
        {/* Input with icon position handling */}
        <div className="relative">
          {/* Left icon */}
          {icon && iconPosition === "left" && (
            <div className="absolute inset-y-0 left-0 flex items-center pl-3 pointer-events-none text-white/50">
              {typeof icon === 'string' ? <i className={icon}></i> : icon}
            </div>
          )}
          
          {/* Actual input element */}
          <input
            id={id}
            type={type}
            className={inputClasses}
            ref={ref}
            {...props}
          />
          
          {/* Right icon */}
          {icon && iconPosition === "right" && (
            <div className="absolute inset-y-0 right-0 flex items-center pr-3 pointer-events-none text-white/50">
              {typeof icon === 'string' ? <i className={icon}></i> : icon}
            </div>
          )}
        </div>
        
        {/* Error message */}
        {error && (
          <p className="mt-1 text-xs text-red-500 slide-up">
            {error}
          </p>
        )}
        
        {/* Hint text */}
        {hint && !error && (
          <p className="mt-1 text-xs text-white/50">
            {hint}
          </p>
        )}
      </div>
    );
    
    return inputElement;
  }
);

// Create a specialized search input component
const SearchInput = React.forwardRef(
  ({ className, placeholder = "Search...", ...props }, ref) => {
    return (
      <Input
        type="search"
        className={className}
        placeholder={placeholder}
        icon={
          <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 20 20" fill="currentColor" className="w-4 h-4">
            <path fillRule="evenodd" d="M9 3.5a5.5 5.5 0 100 11 5.5 5.5 0 000-11zM2 9a7 7 0 1112.452 4.391l3.328 3.329a.75.75 0 11-1.06 1.06l-3.329-3.328A7 7 0 012 9z" clipRule="evenodd" />
          </svg>
        }
        iconPosition="left"
        variant="ghost"
        rounded={true}
        {...props}
        ref={ref}
      />
    );
  }
);

// Create textarea component
const Textarea = React.forwardRef(
  ({ 
    className, 
    variant = "default", 
    size = "default",
    error, 
    rows = 3,
    autoResize = false,
    label,
    hint,
    ...props 
  }, ref) => {
    // Generate unique ID for the textarea
    const id = React.useId();
    const textareaRef = React.useRef(null);
    
    React.useImperativeHandle(ref, () => textareaRef.current);
    
    // Handle auto-resize functionality
    React.useEffect(() => {
      if (autoResize && textareaRef.current) {
        const handleResize = () => {
          const textarea = textareaRef.current;
          if (!textarea) return;
          
          textarea.style.height = 'auto';
          textarea.style.height = `${textarea.scrollHeight}px`;
        };
        
        const textarea = textareaRef.current;
        textarea.addEventListener('input', handleResize);
        
        // Initial resize
        handleResize();
        
        return () => {
          textarea.removeEventListener('input', handleResize);
        };
      }
    }, [autoResize]);
    
    // Get size-appropriate padding
    const sizeStyles = {
      xs: "px-2 py-1 text-xs",
      sm: "px-2 py-1.5 text-sm",
      default: "px-3 py-2 text-sm",
      lg: "px-4 py-2.5 text-base",
      xl: "px-5 py-3 text-lg"
    };
    
    return (
      <div className="textarea-wrapper">
        {/* Textarea Label */}
        {label && (
          <label htmlFor={id} className="block text-sm font-medium text-white/70 mb-1.5 slide-up">
            {label}
          </label>
        )}
        
        <textarea
          id={id}
          className={cn(
            "w-full rounded-md shadow-sm transition-colors min-h-[70px]",
            "focus:outline-none focus:ring-1 focus:ring-white/30 focus:border-white/30",
            "placeholder:text-white/50 disabled:cursor-not-allowed disabled:opacity-50",
            inputVariants[variant],
            sizeStyles[size],
            error && "border-red-500 focus:border-red-500 focus:ring-red-500/30",
            className
          )}
          rows={rows}
          ref={textareaRef}
          {...props}
        />
        
        {/* Error message */}
        {error && (
          <p className="mt-1 text-xs text-red-500 slide-up">
            {error}
          </p>
        )}
        
        {/* Hint text */}
        {hint && !error && (
          <p className="mt-1 text-xs text-white/50">
            {hint}
          </p>
        )}
      </div>
    );
  }
);

Input.displayName = "Input";
SearchInput.displayName = "SearchInput";
Textarea.displayName = "Textarea";

export { Input, SearchInput, Textarea, inputVariants };
