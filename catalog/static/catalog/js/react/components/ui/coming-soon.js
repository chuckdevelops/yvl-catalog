import React, { useEffect, useState } from "react";
import { cn } from "../../lib/utils";

const ComingSoon = React.forwardRef(
  ({ className, text = "Coming Soon", backUrl = "/", backText = "← BACK TO CATALOG", ...props }, ref) => {
    const [dots, setDots] = useState("");
    
    useEffect(() => {
      // Animated dots effect
      const interval = setInterval(() => {
        setDots(prevDots => {
          if (prevDots.length >= 3) return "";
          return prevDots + ".";
        });
      }, 500);
      
      return () => clearInterval(interval);
    }, []);

    return (
      <div 
        ref={ref}
        className={cn(
          "coming-soon-container min-h-screen flex flex-col items-center justify-center bg-black text-white",
          className
        )}
        {...props}
      >
        <div className="relative">
          <h1 className="coming-soon-text text-6xl font-bold uppercase tracking-wider mb-4">
            {text}<span className="dots-animation">{dots}</span>
          </h1>
          
          <div className="mt-8 w-full max-w-xl">
            <div className="h-1.5 w-full bg-gray-700 rounded overflow-hidden">
              <div className="h-full bg-white animate-pulse" style={{ width: '15%' }}></div>
            </div>
            <p className="text-xs text-gray-500 mt-2">We're working on something special</p>
          </div>
        </div>
        
        <div className="absolute bottom-8 text-center">
          <a href={backUrl} className="text-gray-500 hover:text-white transition duration-300 text-sm tracking-wider">
            {backText}
          </a>
        </div>
      </div>
    );
  }
);

ComingSoon.displayName = "ComingSoon";

export { ComingSoon };