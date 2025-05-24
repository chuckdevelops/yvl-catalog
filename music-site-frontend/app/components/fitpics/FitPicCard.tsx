
interface FitPicCardProps {
  fitpic: FitPic;
  onShowDetails: (fitpic: FitPic) => void;
  onImageError: (e: React.SyntheticEvent<HTMLImageElement, Event>) => void;
}

const FitPicCard = ({ fitpic, onShowDetails, onImageError }: FitPicCardProps) => {
  return (
    <Card key={fitpic.id} className="overflow-hidden h-full flex flex-col">
      <div className="h-64 overflow-hidden">
        {fitpic.thumbnail ? (
          <img 
            src={fitpic.thumbnail} 
            alt={fitpic.caption} 
            className="w-full h-full object-cover"
            onError={onImageError} 
          />
        ) : (
          <div className="h-full flex items-center justify-center bg-gray-100">
            <span className="text-gray-400 text-4xl">👕</span>
          </div>
        )}
      </div>
      <CardContent className="flex-grow">
        <h5 className="text-lg font-semibold">{fitpic.caption || "Fit Pic"}</h5>
        <h6 className="text-sm text-gray-500 mb-2">{fitpic.release_date}</h6>
        {fitpic.photographer && (
          <p className="text-sm">📸: {fitpic.photographer}</p>
        )}
        <div className="flex justify-between items-center my-2">
          <Badge variant="default">{fitpic.pic_type}</Badge>
          <Badge variant="secondary">{fitpic.quality}</Badge>
        </div>
        <p className="text-xs text-gray-500 mb-4">Era: {fitpic.era}</p>
        <div className="flex justify-center space-x-2 mt-auto">
          <Button variant="outline" size="sm" onClick={() => onShowDetails(fitpic)}>Details</Button>
          {fitpic.source_links.length > 0 && (
            <Button variant="secondary" size="sm" asChild>
              <a href={fitpic.source_links[0]} target="_blank" rel="noopener noreferrer">View Source</a>
            </Button>
          )}
        </div>
      </CardContent>
    </Card>
  );
};

import { FitPic } from '@/types/fitpics';
import { Card, CardContent } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';

export default FitPicCard;
