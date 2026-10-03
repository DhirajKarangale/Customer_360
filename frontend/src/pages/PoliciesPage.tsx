import { useState, useEffect, useMemo } from 'react';
import { Search, Loader2, FileText, ShieldAlert, CalendarDays, ArrowRight, MessageSquare } from 'lucide-react';
import { useAuthStore } from '../store/useAuthStore';
import { usePoliciesQuery } from '../api/policies';
import { usePoliciesStore } from '../store/usePoliciesStore';
import { useAIChatStore } from '../store/useAIChatStore';
import { Pagination } from '../components/ui/Pagination';
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
} from '../components/ui/select';
import { CustomerModal } from '../components/customers/CustomerModal';

// Fallback constant filters since no API is available to fetch unique ones
const POLICY_TYPES = ["Life", "Health", "Auto", "Home", "Liability", "Property", "Business"];
const POLICY_STATUSES = ["Active", "Pending", "Expired", "Cancelled", "Suspended", "Claimed"];

export default function PoliciesPage() {
  const agent = useAuthStore((state) => state.agent);
  
  // Local state
  const [page, setPage] = useState(1);
  const [pageSize, setPageSize] = useState(10);
  const [searchTerm, setSearchTerm] = useState('');
  const [debouncedSearch, setDebouncedSearch] = useState('');
  const [policyType, setPolicyType] = useState('all');
  const [status, setStatus] = useState('all');
  const [selectedCustomerId, setSelectedCustomerId] = useState<string | null>(null);

  const { mergePolicies, getAllPolicies } = usePoliciesStore();
  const { setIsOpen: setChatOpen, setActivePolicy } = useAIChatStore();

  // Debounce search term
  useEffect(() => {
    const timer = setTimeout(() => {
      setDebouncedSearch(searchTerm.trim().toLowerCase());
      setPage(1); // Reset to page 1 on new search
    }, 500);
    return () => clearTimeout(timer);
  }, [searchTerm]);

  // Reset page when filters change
  useEffect(() => {
    setPage(1);
  }, [policyType, status, pageSize]);

  // Query Backend
  // If "all" is selected, we pass undefined to the backend
  const { data, isFetching, isError } = usePoliciesQuery(
    {
      insurance_agent_id: agent?.id || '',
      page,
      page_size: pageSize,
      search_term: debouncedSearch,
      policy_type: policyType === 'all' ? undefined : policyType,
      status: status === 'all' ? undefined : status,
    },
    !!agent?.id
  );

  // Sync incoming API data into our global deduplicated store
  useEffect(() => {
    if (data?.items && data.items.length > 0) {
      mergePolicies(data.items);
    }
  }, [data, mergePolicies]);

  // Intelligent Local Fallback logic
  const displayItems = useMemo(() => {
    // If API response is ready, just show authoritative data (even while fetching)
    if (data) {
      return data.items;
    }

    // While fetching initial data, optimistic search local store cache
    const all = getAllPolicies();
    // Sort local cache by date descending to prevent random jumping
    let filtered = all.sort((a, b) => new Date(b.start_date).getTime() - new Date(a.start_date).getTime());

    if (policyType !== 'all') {
      filtered = filtered.filter(p => p.policy_type === policyType);
    }
    if (status !== 'all') {
      filtered = filtered.filter(p => p.status === status);
    }
    if (debouncedSearch) {
      const lower = debouncedSearch.toLowerCase();
      filtered = filtered.filter(p => 
        p.policy_number.toLowerCase().includes(lower) ||
        p.customer_id.toLowerCase().includes(lower) ||
        p.agent_id.toLowerCase().includes(lower)
      );
    }

    const startIndex = (page - 1) * pageSize;
    return filtered.slice(startIndex, startIndex + pageSize);
  }, [data, isFetching, getAllPolicies, policyType, status, debouncedSearch, pageSize, page]);

  // Calculate pagination props
  const totalItems = data?.total_items ?? displayItems.length;
  const totalPages = data?.total_pages ?? Math.ceil(displayItems.length / pageSize);
  const currentPage = data?.current_page ?? page;

  return (
    <div className="space-y-6">
      {/* Page Header & Filters */}
      <div className="flex flex-col gap-4 rounded-xl border border-white/5 bg-black/40 backdrop-blur-xl border border-white/10 shadow-2xl p-4 shadow-sm md:flex-row md:items-center md:justify-between">
        <div className="flex items-center gap-2">
          <div className="rounded-lg bg-primary/10 p-2 text-primary">
            <ShieldAlert className="h-6 w-6" />
          </div>
          <h1 className="text-xl font-semibold tracking-tight">Policies Management</h1>
        </div>

        <div className="flex flex-col gap-3 sm:flex-row sm:items-center">
          {/* Search Bar */}
          <div className="relative">
            <Search className="absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-white/70" />
            <input
              type="text"
              placeholder="Search ID, Policy #..."
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              className="h-10 w-full rounded-md border border-input bg-transparent pl-9 pr-4 text-sm font-medium focus:outline-none focus:ring-1 focus:ring-primary sm:w-[250px] shadow-sm"
            />
          </div>

          {/* Filters */}
          <div className="flex items-center gap-3">
            <Select value={policyType} onValueChange={(val) => setPolicyType(val || 'all')}>
              <SelectTrigger className="w-full sm:w-[160px] bg-transparent">
                <div className="flex items-center gap-1.5 truncate">
                  <span className="text-white/70 font-normal">Type:</span>
                  <span>{policyType === 'all' ? 'All' : policyType}</span>
                </div>
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="all">All Types</SelectItem>
                {POLICY_TYPES.map((type) => (
                  <SelectItem key={type} value={type}>{type}</SelectItem>
                ))}
              </SelectContent>
            </Select>

            <Select value={status} onValueChange={(val) => setStatus(val || 'all')}>
              <SelectTrigger className="w-full sm:w-[160px] bg-transparent">
                <div className="flex items-center gap-1.5 truncate">
                  <span className="text-white/70 font-normal">Status:</span>
                  <span>{status === 'all' ? 'All' : status}</span>
                </div>
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="all">All Statuses</SelectItem>
                {POLICY_STATUSES.map((stat) => (
                  <SelectItem key={stat} value={stat}>{stat}</SelectItem>
                ))}
              </SelectContent>
            </Select>
          </div>
        </div>
      </div>

      {/* Main Content Area */}
      <div className="rounded-xl border border-white/5 bg-black/40 backdrop-blur-xl border border-white/10 shadow-2xl shadow-sm overflow-hidden">
        
        {/* Loading State Overlay (Only if totally empty) */}
        {isFetching && displayItems.length === 0 && (
          <div className="flex h-64 flex-col items-center justify-center gap-4 text-white/70">
            <Loader2 className="h-8 w-8 animate-spin text-primary" />
            <p>Searching Policies...</p>
          </div>
        )}

        {/* Error State */}
        {isError && !isFetching && (
          <div className="flex h-64 flex-col items-center justify-center gap-2 text-destructive">
            <ShieldAlert className="h-10 w-10" />
            <p className="font-medium">Failed to load policies</p>
            <p className="text-sm opacity-80">Please check your connection and try again.</p>
          </div>
        )}

        {/* Empty State */}
        {!isFetching && !isError && displayItems.length === 0 && (
          <div className="flex h-64 flex-col items-center justify-center gap-2 text-white/70">
            <FileText className="h-10 w-10 opacity-50" />
            <p className="text-lg font-medium text-white">No Policies Found</p>
            <p className="text-sm">Try adjusting your search terms or filters.</p>
          </div>
        )}

        {/* Data Table */}
        {displayItems.length > 0 && (
          <div className="overflow-x-auto relative">
            <table className="w-full text-left text-sm">
              <thead className="bg-black/20 border-b border-white/5">
                <tr>
                  <th className="px-6 py-4 font-medium text-white/70">Policy Number</th>
                  <th className="px-6 py-4 font-medium text-white/70">Type</th>
                  <th className="px-6 py-4 font-medium text-white/70">Status</th>
                  <th className="px-6 py-4 font-medium text-white/70">Premium</th>
                  <th className="px-6 py-4 font-medium text-white/70">Coverage</th>
                  <th className="px-6 py-4 font-medium text-white/70">Dates</th>
                  <th className="px-6 py-4 font-medium text-white/70">Actions</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-border">
                {displayItems.map((policy) => (
                  <tr 
                    key={policy.id} 
                    className="hover:bg-white/5 transition-colors cursor-pointer"
                    onClick={() => setSelectedCustomerId(policy.customer_id)}
                  >
                    <td className="px-6 py-4 font-medium text-white">{policy.policy_number}</td>
                    <td className="px-6 py-4">
                      <span className="inline-flex items-center rounded-full bg-secondary px-2.5 py-0.5 text-xs font-semibold text-secondary-foreground border border-white/5">
                        {policy.policy_type}
                      </span>
                    </td>
                    <td className="px-6 py-4">
                      <span className={`inline-flex items-center rounded-full px-2.5 py-0.5 text-xs font-semibold border ${
                        policy.status === 'Active' ? 'bg-emerald-500/10 text-emerald-500 border-emerald-500/20' : 
                        policy.status === 'Expired' ? 'bg-destructive/10 text-destructive border-destructive/20' :
                        'bg-amber-500/10 text-amber-500 border-amber-500/20'
                      }`}>
                        {policy.status}
                      </span>
                    </td>
                    <td className="px-6 py-4 text-white">${policy.premium_amount.toLocaleString(undefined, { minimumFractionDigits: 2 })}</td>
                    <td className="px-6 py-4 text-white/70">${policy.coverage_amount.toLocaleString()}</td>
                    <td className="px-6 py-4">
                      <div className="flex flex-col gap-1 text-xs">
                        <div className="flex items-center gap-2 text-white font-medium">
                          <CalendarDays className="h-3.5 w-3.5 text-white/70" />
                          {new Date(policy.start_date).toLocaleDateString(undefined, { month: 'short', day: 'numeric', year: 'numeric' })}
                        </div>
                        <div className="flex items-center gap-2 text-white/70">
                          <ArrowRight className="h-3 w-3 ml-[2px] opacity-70" />
                          {new Date(policy.end_date).toLocaleDateString(undefined, { month: 'short', day: 'numeric', year: 'numeric' })}
                        </div>
                      </div>
                    </td>
                    <td className="px-6 py-4">
                      <button
                        onClick={(e) => {
                          e.stopPropagation();
                          setActivePolicy(policy.id, policy.policy_number);
                          setChatOpen(true);
                        }}
                        className="inline-flex h-8 items-center justify-center gap-2 rounded-md bg-white/5 border-white/10 px-3 text-xs font-medium text-secondary-foreground shadow-sm transition-colors hover:bg-secondary hover:text-white"
                        title="Ask AI about this policy"
                      >
                        <MessageSquare className="h-3.5 w-3.5" />
                        Ask AI
                      </button>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}

        {/* Pagination */}
        <Pagination
          currentPage={currentPage}
          totalPages={totalPages}
          totalItems={totalItems}
          pageSize={pageSize}
          onPageChange={setPage}
          onPageSizeChange={setPageSize}
        />
      </div>

      {/* Dynamic Customer Modal */}
      <CustomerModal 
        customerId={selectedCustomerId} 
        onClose={() => setSelectedCustomerId(null)} 
      />
    </div>
  );
}
