
import { FitPic } from '@/types/fitpics';
import FitPicCard from './FitPicCard';
import { Pagination, PaginationContent, PaginationEllipsis, PaginationItem, PaginationLink, PaginationNext, PaginationPrevious } from '@/components/ui/pagination';

interface FitPicGridProps {
  fitpics: FitPic[];
  currentPage: number;
  totalPages: number;
  onPageChange: (page: number) => void;
  onShowDetails: (fitpic: FitPic) => void;
  onImageError: (e: React.SyntheticEvent<HTMLImageElement, Event>) => void;
}

const FitPicGrid = ({
  fitpics,
  currentPage,
  totalPages,
  onPageChange,
  onShowDetails,
  onImageError
}: FitPicGridProps) => {
  return (
    <>
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
        {fitpics.length > 0 ? (
          fitpics.map(fitpic => (
            <FitPicCard 
              key={fitpic.id} 
              fitpic={fitpic} 
              onShowDetails={onShowDetails} 
              onImageError={onImageError} 
            />
          ))
        ) : (
          <div className="col-span-full p-6 text-center bg-gray-50 rounded-lg">
            <p className="text-gray-500">No fit pics found. Try changing your filters.</p>
          </div>
        )}
      </div>
      
      {/* Pagination */}
      {totalPages > 1 && (
        <Pagination className="my-6">
          <PaginationContent>
            <PaginationItem>
              <PaginationPrevious 
                onClick={() => currentPage > 1 && onPageChange(currentPage - 1)}
                className={currentPage <= 1 ? 'pointer-events-none opacity-50' : 'cursor-pointer'}
              />
            </PaginationItem>
            
            {Array.from({ length: totalPages }, (_, i) => i + 1).map(page => {
              // Show current page and 2 pages on either side
              if (
                page === 1 || 
                page === totalPages || 
                (page >= currentPage - 2 && page <= currentPage + 2)
              ) {
                return (
                  <PaginationItem key={page}>
                    <PaginationLink
                      isActive={page === currentPage}
                      onClick={() => onPageChange(page)}
                    >
                      {page}
                    </PaginationLink>
                  </PaginationItem>
                );
              } else if (
                (page === currentPage - 3 && currentPage > 3) ||
                (page === currentPage + 3 && currentPage < totalPages - 2)
              ) {
                return <PaginationEllipsis key={page} />;
              }
              return null;
            })}
            
            <PaginationItem>
              <PaginationNext 
                onClick={() => currentPage < totalPages && onPageChange(currentPage + 1)}
                className={currentPage >= totalPages ? 'pointer-events-none opacity-50' : 'cursor-pointer'}
              />
            </PaginationItem>
          </PaginationContent>
        </Pagination>
      )}
    </>
  );
};

export default FitPicGrid;
