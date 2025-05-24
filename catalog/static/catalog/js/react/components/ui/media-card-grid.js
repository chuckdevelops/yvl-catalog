import React from "react";
import { cn } from "../../lib/utils";
import { Card, CardContent, CardFooter } from "./card";

const MediaCategoryCard = React.forwardRef(
  ({ 
    className, 
    title,
    description,
    imageSrc,
    linkUrl,
    linkText = "View",
    ...props 
  }, ref) => {
    return (
      <Card 
        ref={ref} 
        className={cn("h-100 media-category-card glass hover-scale fade-in", className)} 
        {...props}
      >
        <CardContent className="text-center p-4 scale-in">
          {imageSrc && (
            <div className="media-image-container mb-3 slide-up">
              <img 
                src={imageSrc} 
                alt={title || "Media"} 
                className="img-fluid scale-in" 
                style={{ maxHeight: "170px" }}
              />
            </div>
          )}
          
          {title && <h2 className="card-title h3 mb-2 text-glow">{title}</h2>}
          {description && <p className="card-text text-white/70 mb-4 slide-up">{description}</p>}
        </CardContent>
        
        {linkUrl && (
          <CardFooter className="text-center border-light p-3">
            <a href={linkUrl} className="btn btn-primary hover-lift">
              {linkText}
            </a>
          </CardFooter>
        )}
      </Card>
    );
  }
);
MediaCategoryCard.displayName = "MediaCategoryCard";

const MediaCategoryGrid = React.forwardRef(
  ({ 
    className, 
    categories = [],
    colSize = "col-md-6 col-lg-3",
    ...props 
  }, ref) => {
    return (
      <div 
        ref={ref}
        className={cn("row fade-in", className)}
        {...props}
      >
        {categories.map((category, index) => (
          <div key={index} className={`${colSize} mb-4`} style={{ animationDelay: `${index * 0.1}s` }}>
            <MediaCategoryCard
              title={category.title}
              description={category.description}
              imageSrc={category.imageSrc}
              linkUrl={category.linkUrl}
              linkText={category.linkText || "View"}
            />
          </div>
        ))}
      </div>
    );
  }
);
MediaCategoryGrid.displayName = "MediaCategoryGrid";

export { MediaCategoryCard, MediaCategoryGrid };