
import { FitPic } from '@/types/fitpics';
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogFooter } from '@/components/ui/dialog';
import { Button } from '@/components/ui/button';

interface FitPicDetailsProps {
  fitpic: FitPic | null;
  isOpen: boolean;
  onOpenChange: (open: boolean) => void;
  onImageError: (e: React.SyntheticEvent<HTMLImageElement, Event>) => void;
}

const FitPicDetails = ({
  fitpic,
  isOpen,
  onOpenChange,
  onImageError
}: FitPicDetailsProps) => {
  if (!fitpic) return null;
  
  return (
    <Dialog open={isOpen} onOpenChange={onOpenChange}>
      <DialogContent className="max-w-4xl">
        <DialogHeader>
          <DialogTitle>{fitpic.caption || "Fit Pic"} ({fitpic.release_date})</DialogTitle>
        </DialogHeader>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          <div>
            {fitpic.thumbnail ? (
              <img 
                src={fitpic.thumbnail} 
                alt={fitpic.caption} 
                className="w-full rounded-md"
                onError={onImageError}
              />
            ) : (
              <div className="w-full h-64 flex items-center justify-center bg-gray-100 rounded-md">
                <span className="text-gray-400 text-6xl">👕</span>
              </div>
            )}
          </div>
          <div>
            <h5 className="text-lg font-bold mb-4">Details</h5>
            <div className="space-y-2">
              <p><strong>Caption:</strong> {fitpic.caption || "N/A"}</p>
              <p><strong>Era:</strong> {fitpic.era}</p>
              <p><strong>Date:</strong> {fitpic.release_date}</p>
              <p><strong>Type:</strong> {fitpic.pic_type}</p>
              <p><strong>Portion:</strong> {fitpic.portion}</p>
              <p><strong>Quality:</strong> {fitpic.quality}</p>
              <p><strong>Photographer:</strong> {fitpic.photographer || "Unknown"}</p>
            </div>
            
            {fitpic.notes && (
              <>
                <h5 className="text-lg font-bold mt-4 mb-2">Notes</h5>
                <p>{fitpic.notes}</p>
              </>
            )}
            
            <h5 className="text-lg font-bold mt-4 mb-2">Links</h5>
            {fitpic.source_links.length > 0 ? (
              <div className="space-y-1">
                {fitpic.source_links.map((link, index) => (
                  <p key={index}>
                    <a 
                      href={link} 
                      target="_blank" 
                      rel="noopener noreferrer"
                      className="text-blue-600 hover:underline break-all"
                    >
                      {link}
                    </a>
                  </p>
                ))}
              </div>
            ) : (
              <p>No links available</p>
            )}
          </div>
        </div>
        <DialogFooter>
          <Button onClick={() => onOpenChange(false)}>Close</Button>
        </DialogFooter>
      </DialogContent>
    </Dialog>
  );
};

export default FitPicDetails;
