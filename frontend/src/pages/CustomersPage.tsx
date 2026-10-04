import { SEO } from '../components/SEO';
import { useState, useEffect, useMemo } from 'react';
import { Search, Loader2, Users, MessageSquare } from 'lucide-react';
import { useAuthStore } from '../store/useAuthStore';
import { useCustomersQuery } from '../api/customers';
import { useCustomersStore } from '../store/useCustomersStore';
import { useAIChatStore } from '../store/useAIChatStore';
import { Pagination } from '../components/ui/Pagination';
import { LoadingState, EmptyState } from '../components/ui/StateFeedback';
import { CustomerModal } from '../components/customers/CustomerModal';
import { getRandomMessage } from '../utils/messages';

export default function CustomersPage() {
  return (
    <>
      <SEO title="Customers | Customer 360 AI Insights" />
      <OriginalCustomersPage />
    </>
  );
}

function OriginalCustomersPage() {
  const agent = useAuthStore((state) => state.agent);


  const [page, setPage] = useState(1);
  const [pageSize, setPageSize] = useState(10);
  const [searchTerm, setSearchTerm] = useState('');
  const [debouncedSearch, setDebouncedSearch] = useState('');
  const [selectedCustomerId, setSelectedCustomerId] = useState<string | null>(null);

  const { mergeCustomers, getAllCustomers } = useCustomersStore();
  const { setIsOpen: setChatOpen, setActiveCustomer } = useAIChatStore();


  useEffect(() => {
    const timer = setTimeout(() => {
      setDebouncedSearch(searchTerm.trim().toLowerCase());
      setPage(1); 
    }, 500);
    return () => clearTimeout(timer);
  }, [searchTerm]);


  const { data, isLoading, isFetching } = useCustomersQuery({
    insurance_agent_id: agent?.id || '',
    search_term: debouncedSearch,
    page,
    page_size: pageSize,
  }, !!agent?.id);


  useEffect(() => {
    if (data?.items && data.items.length > 0) {
      mergeCustomers(data.items);
    }
  }, [data, mergeCustomers]);


  const displayItems = useMemo(() => {

    if (data) {
      return data.items;
    }


    const all = getAllCustomers();

    let filtered = all.sort((a, b) => a.name.localeCompare(b.name));

    if (debouncedSearch) {
      const lower = debouncedSearch.toLowerCase();
      filtered = filtered.filter(c => 
        c.name.toLowerCase().includes(lower) ||
        c.email.toLowerCase().includes(lower) ||
        c.phone_number.toLowerCase().includes(lower)
      );
    }

    const startIndex = (page - 1) * pageSize;
    return filtered.slice(startIndex, startIndex + pageSize);
  }, [data, isFetching, getAllCustomers, debouncedSearch, pageSize, page]);


  const totalItems = data?.total_items ?? displayItems.length;
  const totalPages = data?.total_pages ?? Math.ceil(displayItems.length / pageSize);
  const currentPage = data?.current_page ?? page;

  return (
    <div className="space-y-6">

      <div className="flex flex-col gap-4 rounded-xl border border-white/5 bg-black/40 backdrop-blur-xl border border-white/10 shadow-2xl p-4 shadow-sm md:flex-row md:items-center md:justify-between">
        <div className="flex items-center gap-2">
          <div className="rounded-lg bg-primary/10 p-2 text-primary">
            <Users className="h-6 w-6" />
          </div>
          <h1 className="text-xl font-semibold tracking-tight">Customers Management</h1>
        </div>

        <div className="flex flex-col gap-3 md:flex-row md:items-center">

          <div className="relative">
            <Search className="absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-white/70" />
            <input
              type="text"
              placeholder="Search Name, Email..."
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              className="h-10 w-full rounded-lg border border-input bg-transparent pl-9 pr-4 text-sm ring-offset-background file:border-0 file:bg-transparent file:text-sm file:font-medium placeholder:text-white/70 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring disabled:cursor-not-allowed disabled:opacity-50 md:w-[250px]"
            />
            {isFetching && (
              <Loader2 className="absolute right-3 top-1/2 h-4 w-4 -translate-y-1/2 animate-spin text-primary" />
            )}
          </div>
        </div>
      </div>


      <div className="rounded-xl border border-white/5 bg-black/40 backdrop-blur-xl border border-white/10 shadow-2xl shadow-sm">
        <div className="overflow-x-auto">
          {isLoading && !data && displayItems.length === 0 ? (
            <LoadingState message={getRandomMessage('loadingCustomers')} />
          ) : displayItems.length === 0 ? (
            <EmptyState 
              icon={Users} 
              title={getRandomMessage('emptyCustomers')} 
              description="Try adjusting your search criteria" 
            />
          ) : (
            <table className="w-full text-left text-sm">
              <thead className="bg-black/20 border-b border-white/5">
                <tr>
                  <th className="px-6 py-4 font-medium text-white/70">Name</th>
                  <th className="px-6 py-4 font-medium text-white/70">Email</th>
                  <th className="px-6 py-4 font-medium text-white/70">Phone Number</th>
                  <th className="px-6 py-4 font-medium text-white/70">Date of Birth</th>
                  <th className="px-6 py-4 font-medium text-white/70">Address</th>
                  <th className="px-6 py-4 font-medium text-white/70">Actions</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-border">
                {displayItems.map((customer) => (
                  <tr 
                    key={customer.id} 
                    className="hover:bg-white/5 transition-colors cursor-pointer"
                    onClick={() => setSelectedCustomerId(customer.id)}
                  >
                    <td className="px-6 py-4 font-medium text-white">{customer.name}</td>
                    <td className="px-6 py-4 text-white/70">{customer.email}</td>
                    <td className="px-6 py-4 text-white/70">{customer.phone_number}</td>
                    <td className="px-6 py-4 text-white/70">
                      {new Date(customer.date_of_birth).toLocaleDateString(undefined, { month: 'long', day: 'numeric', year: 'numeric' })}
                    </td>
                    <td className="px-6 py-4 text-white/70 max-w-[200px] truncate" title={customer.address}>
                      {customer.address}
                    </td>
                    <td className="px-6 py-4">
                      <button
                        onClick={(e) => {
                          e.stopPropagation();
                          setActiveCustomer(customer.id, customer.name);
                          setChatOpen(true);
                        }}
                        className="inline-flex h-8 items-center justify-center gap-2 rounded-md bg-white/5 border-white/10 px-3 text-xs font-medium text-secondary-foreground shadow-sm transition-colors hover:bg-secondary hover:text-white"
                        title="Ask AI about this customer"
                      >
                        <MessageSquare className="h-3.5 w-3.5" />
                        Ask AI
                      </button>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          )}
        </div>


        {totalItems > 0 && (
          <Pagination
            currentPage={currentPage}
            totalPages={totalPages}
            pageSize={pageSize}
            totalItems={totalItems}
            onPageChange={setPage}
            onPageSizeChange={(size) => {
              setPageSize(size);
              setPage(1);
            }}
          />
        )}
      </div>


      <CustomerModal 
        customerId={selectedCustomerId} 
        onClose={() => setSelectedCustomerId(null)} 
      />
    </div>
  );
}
