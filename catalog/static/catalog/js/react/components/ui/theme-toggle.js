import React, { useState, useEffect } from "react";
import { cn } from "../../lib/utils";
import { Button } from "./button";

const ThemeToggle = React.forwardRef(({ className, ...props }, ref) => {
  const [darkMode, setDarkMode] = useState(false);
  
  useEffect(() => {
    // Check if dark mode preference exists in localStorage
    const savedPreference = localStorage.getItem("carti-dark-mode");
    if (savedPreference === "true") {
      setDarkMode(true);
      document.body.classList.add("dark-mode");
    }
    
    // Check system preference if no saved preference
    if (savedPreference === null) {
      const systemPrefersDark = window.matchMedia("(prefers-color-scheme: dark)").matches;
      if (systemPrefersDark) {
        setDarkMode(true);
        document.body.classList.add("dark-mode");
        localStorage.setItem("carti-dark-mode", "true");
      }
    }
  }, []);
  
  const toggleTheme = () => {
    const newDarkMode = !darkMode;
    setDarkMode(newDarkMode);
    
    if (newDarkMode) {
      document.body.classList.add("dark-mode");
      localStorage.setItem("carti-dark-mode", "true");
    } else {
      document.body.classList.remove("dark-mode");
      localStorage.setItem("carti-dark-mode", "false");
    }
  };
  
  return (
    <button
      onClick={toggleTheme}
      ref={ref}
      className={cn("btn btn-sm", darkMode ? "btn-light" : "btn-dark", className)}
      title={darkMode ? "Switch to Light Mode" : "Switch to Dark Mode"}
      {...props}
    >
      {darkMode ? (
        <React.Fragment>
          <i className="fas fa-sun me-1"></i>
          <span className="d-none d-md-inline">Light</span>
        </React.Fragment>
      ) : (
        <React.Fragment>
          <i className="fas fa-moon me-1"></i>
          <span className="d-none d-md-inline">Dark</span>
        </React.Fragment>
      )}
    </button>
  );
});

ThemeToggle.displayName = "ThemeToggle";

export { ThemeToggle };