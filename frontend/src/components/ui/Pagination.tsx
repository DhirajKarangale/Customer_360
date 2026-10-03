import { ChevronLeft, ChevronRight, ChevronsLeft, ChevronsRight } from 'lucide-react';
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from './select';

interface PaginationProps {
  currentPage: number;
  totalPages: number;
  totalItems: number;
  pageSize: number;
  onPageChange: (page: number) => void;
  onPageSizeChange: (size: number) => void;
}

export function Pagination({
  currentPage,
  totalPages,
  totalItems,
  pageSize,
  onPageChange,
  onPageSizeChange,
}: PaginationProps) {
  
  const handlePageChange = (newPage: number) => {
    if (newPage >= 1 && newPage <= totalPages) {
      onPageChange(newPage);
    }
  };

  return (
    <div className="flex flex-col sm:flex-row items-center justify-between px-4 py-3 bg-black/40 backdrop-blur-xl border border-white/10 shadow-2xl border-t border-white/5 mt-4 rounded-b-xl shadow-sm">
      {/* Page Size Dropdown & Info */}
      <div className="flex items-center gap-4 text-sm text-white/70 mb-4 sm:mb-0">
        <div className="flex items-center gap-2">
          <span>Show</span>
          <Select 
            value={pageSize.toString()} 
            onValueChange={(val) => onPageSizeChange(Number(val))}
          >
            <SelectTrigger className="h-8 w-[70px] bg-transparent">
              <SelectValue placeholder={pageSize.toString()} />
            </SelectTrigger>
            <SelectContent>
              {[10, 20, 50, 100].map((size) => (
                <SelectItem key={size} value={size.toString()}>
                  {size}
                </SelectItem>
              ))}
            </SelectContent>
          </Select>
          <span>per page</span>
        </div>
        <div className="hidden sm:block">
          Total: <span className="font-medium text-white">{totalItems}</span> records
        </div>
      </div>

      {/* Pagination Controls */}
      <div className="flex items-center gap-2">
        <div className="text-sm text-white/70 mr-4">
          Page <span className="font-medium text-white">{currentPage}</span> of <span className="font-medium text-white">{totalPages || 1}</span>
        </div>
        
        <button
          onClick={() => handlePageChange(1)}
          disabled={currentPage === 1 || totalPages === 0}
          className="flex h-8 w-8 items-center justify-center rounded-md border border-input bg-transparent hover:bg-white/5 text-white disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
          title="First Page"
        >
          <ChevronsLeft className="h-4 w-4" />
        </button>
        <button
          onClick={() => handlePageChange(currentPage - 1)}
          disabled={currentPage === 1 || totalPages === 0}
          className="flex h-8 w-8 items-center justify-center rounded-md border border-input bg-transparent hover:bg-white/5 text-white disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
          title="Previous Page"
        >
          <ChevronLeft className="h-4 w-4" />
        </button>
        <button
          onClick={() => handlePageChange(currentPage + 1)}
          disabled={currentPage >= totalPages || totalPages === 0}
          className="flex h-8 w-8 items-center justify-center rounded-md border border-input bg-transparent hover:bg-white/5 text-white disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
          title="Next Page"
        >
          <ChevronRight className="h-4 w-4" />
        </button>
        <button
          onClick={() => handlePageChange(totalPages)}
          disabled={currentPage >= totalPages || totalPages === 0}
          className="flex h-8 w-8 items-center justify-center rounded-md border border-input bg-transparent hover:bg-white/5 text-white disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
          title="Last Page"
        >
          <ChevronsRight className="h-4 w-4" />
        </button>
      </div>
    </div>
  );
}
