import React from "react";
import { cn } from "../../lib/utils";

const Pagination = React.forwardRef(
  ({ 
    className, 
    totalPages = 1, 
    currentPage = 1, 
    baseUrl = "?page=", 
    urlParams = "",
    showEndButtons = true,
    maxVisiblePages = 5,
    ariaLabel = "Page navigation",
    ...props 
  }, ref) => {
    // Create full URL with parameters
    const createUrl = (pageNum) => {
      return `${baseUrl}${pageNum}${urlParams}`;
    };
    
    // Determine the range of pages to show
    const getVisibleRange = () => {
      if (totalPages <= maxVisiblePages) {
        return Array.from({ length: totalPages }, (_, i) => i + 1);
      }
      
      let start = Math.max(1, currentPage - Math.floor(maxVisiblePages / 2));
      let end = start + maxVisiblePages - 1;
      
      if (end > totalPages) {
        end = totalPages;
        start = Math.max(1, end - maxVisiblePages + 1);
      }
      
      return Array.from({ length: end - start + 1 }, (_, i) => start + i);
    };
    
    const visiblePages = getVisibleRange();
    const hasPrevious = currentPage > 1;
    const hasNext = currentPage < totalPages;
    
    return (
      <nav aria-label={ariaLabel} className="mt-4" ref={ref} {...props}>
        <ul className={cn("pagination justify-content-center", className)}>
          {/* First Page Button */}
          {showEndButtons && (
            <li className={cn("page-item", !hasPrevious && "disabled")}>
              {hasPrevious ? (
                <a 
                  className="page-link" 
                  href={createUrl(1)} 
                  aria-label="First"
                >
                  <span aria-hidden="true">&laquo;&laquo;</span>
                </a>
              ) : (
                <span className="page-link" aria-hidden="true">&laquo;&laquo;</span>
              )}
            </li>
          )}
          
          {/* Previous Button */}
          <li className={cn("page-item", !hasPrevious && "disabled")}>
            {hasPrevious ? (
              <a 
                className="page-link" 
                href={createUrl(currentPage - 1)} 
                aria-label="Previous"
              >
                <span aria-hidden="true">&laquo;</span>
              </a>
            ) : (
              <span className="page-link" aria-hidden="true">&laquo;</span>
            )}
          </li>
          
          {/* Page Numbers */}
          {visiblePages.map(pageNum => (
            <li 
              key={pageNum} 
              className={cn("page-item", currentPage === pageNum && "active")}
            >
              {currentPage === pageNum ? (
                <span className="page-link">{pageNum}</span>
              ) : (
                <a className="page-link" href={createUrl(pageNum)}>
                  {pageNum}
                </a>
              )}
            </li>
          ))}
          
          {/* Next Button */}
          <li className={cn("page-item", !hasNext && "disabled")}>
            {hasNext ? (
              <a 
                className="page-link" 
                href={createUrl(currentPage + 1)} 
                aria-label="Next"
              >
                <span aria-hidden="true">&raquo;</span>
              </a>
            ) : (
              <span className="page-link" aria-hidden="true">&raquo;</span>
            )}
          </li>
          
          {/* Last Page Button */}
          {showEndButtons && (
            <li className={cn("page-item", !hasNext && "disabled")}>
              {hasNext ? (
                <a 
                  className="page-link" 
                  href={createUrl(totalPages)} 
                  aria-label="Last"
                >
                  <span aria-hidden="true">&raquo;&raquo;</span>
                </a>
              ) : (
                <span className="page-link" aria-hidden="true">&raquo;&raquo;</span>
              )}
            </li>
          )}
        </ul>
      </nav>
    );
  }
);
Pagination.displayName = "Pagination";

export { Pagination };