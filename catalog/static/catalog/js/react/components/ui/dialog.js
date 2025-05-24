import React, { useEffect } from "react";
import { cn } from "../../lib/utils";
import { Button } from "./button";

const Dialog = React.forwardRef(
  ({ 
    className, 
    id,
    title, 
    size = "default", 
    children, 
    onClose, 
    fullscreen = false,
    showCloseButton = true,
    closeButtonText = "Close",
    ...props 
  }, ref) => {
    useEffect(() => {
      // Bootstrap modal requires jQuery or Bootstrap's JS
      // This just makes sure the component works with Bootstrap modal
      const modal = document.getElementById(id);
      if (modal) {
        // Add event listener to handle onClose
        if (onClose) {
          modal.addEventListener('hidden.bs.modal', onClose);
        }
        
        // Clean up
        return () => {
          if (onClose) {
            modal.removeEventListener('hidden.bs.modal', onClose);
          }
        };
      }
    }, [id, onClose]);
    
    const sizeClasses = {
      small: "modal-sm",
      default: "",
      large: "modal-lg",
      extraLarge: "modal-xl"
    };
    
    return (
      <div 
        className="modal fade" 
        id={id} 
        tabIndex="-1" 
        aria-labelledby={`${id}Label`} 
        aria-hidden="true" 
        ref={ref}
        {...props}
      >
        <div className={cn(
          "modal-dialog", 
          sizeClasses[size], 
          fullscreen && "modal-fullscreen",
          className
        )}>
          <div className="modal-content">
            <div className="modal-header">
              <h5 className="modal-title" id={`${id}Label`}>{title}</h5>
              <button 
                type="button" 
                className="btn-close" 
                data-bs-dismiss="modal" 
                aria-label="Close"
              ></button>
            </div>
            <div className="modal-body">
              {children}
            </div>
            {showCloseButton && (
              <div className="modal-footer">
                <Button 
                  variant="secondary" 
                  data-bs-dismiss="modal"
                >
                  {closeButtonText}
                </Button>
              </div>
            )}
          </div>
        </div>
      </div>
    );
  }
);
Dialog.displayName = "Dialog";

export { Dialog };