import React from "react";
import { cn } from "../../lib/utils";
import { Card, CardContent, CardFooter } from "./card";
import { Badge } from "./badge";
import { Button } from "./button";

const MediaCard = React.forwardRef(
  ({ 
    className, 
    item = {}, 
    imagePosition = "top",
    aspectRatio = "auto",
    badgeVariants = {},
    onDetailsClick,
    ...props 
  }, ref) => {
    const getBadgeVariant = (type, value) => {
      if (badgeVariants && badgeVariants[type] && badgeVariants[type][value]) {
        return badgeVariants[type][value];
      }
      
      // Default mappings
      if (type === 'mediaType') {
        return 'primary';
      } else if (type === 'usage') {
        return value === true ? 'success' : 'secondary';
      }
      
      return 'primary';
    };
    
    return (
      <Card 
        ref={ref} 
        className={cn("media-card h-100 glass hover-scale fade-in", className)} 
        {...props}
      >
        {imagePosition === "top" && item.imageUrl && (
          <div className={cn("media-card-image-container", `aspect-ratio-${aspectRatio}`)}>
            <img 
              src={item.imageUrl} 
              className="card-img-top scale-in" 
              alt={item.name || "Media"} 
            />
          </div>
        )}
        
        <CardContent>
          <h5 className="card-title text-glow">{item.name}</h5>
          
          {(item.mediaType || item.wasUsed !== undefined) && (
            <div className="d-flex justify-content-between align-items-center mb-2 slide-up">
              {item.mediaType && (
                <Badge variant={getBadgeVariant('mediaType', item.mediaType)}>
                  {item.mediaType}
                </Badge>
              )}
              
              {item.wasUsed !== undefined && (
                <Badge variant={getBadgeVariant('usage', item.wasUsed)}>
                  {item.wasUsed ? 'Used' : 'Unused'}
                </Badge>
              )}
            </div>
          )}
          
          {item.era && <p className="small text-white/70 mb-2 slide-up">Era: {item.era}</p>}
          
          {item.notes && (
            <p className="card-text small fade-in">
              {typeof item.notes === 'string' && item.notes.length > 100
                ? `${item.notes.substring(0, 97)}...`
                : item.notes}
            </p>
          )}
        </CardContent>
        
        {(onDetailsClick || item.links) && (
          <CardFooter className="text-center border-light">
            {onDetailsClick && (
              <Button 
                size="sm" 
                variant="glass" 
                className="me-2 slide-up"
                onClick={() => onDetailsClick(item)}
              >
                Details
              </Button>
            )}
            
            {item.links && (
              <Button 
                size="sm" 
                variant="outline-secondary" 
                className="hover-lift slide-up"
                as="a" 
                href={item.links} 
                target="_blank"
              >
                Source
              </Button>
            )}
          </CardFooter>
        )}
        
        {imagePosition === "bottom" && item.imageUrl && (
          <div className={cn("media-card-image-container", `aspect-ratio-${aspectRatio}`)}>
            <img 
              src={item.imageUrl} 
              className="card-img-bottom" 
              alt={item.name || "Media"} 
            />
          </div>
        )}
      </Card>
    );
  }
);
MediaCard.displayName = "MediaCard";

export { MediaCard };