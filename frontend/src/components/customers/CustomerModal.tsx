import { useEffect, useMemo } from 'react';
import { createPortal } from 'react-dom';
import { X, Loader2, CalendarDays, ShieldAlert, ArrowRight } from 'lucide-react';
import { usePoliciesQuery } from '../../api/policies';
import { useCustomersQuery } from '../../api/customers';
import { useAuthStore } from '../../store/useAuthStore';
import { useCustomersStore } from '../../store/useCustomersStore';
import { getRandomMessage } from '../../utils/messages';
import { LoadingState, EmptyState } from '../ui/StateFeedback';

interface CustomerModalProps {
  customerId: string | null;
  onClose: () => void;
}

export function CustomerModal({ customerId, onClose }: CustomerModalProps) {
  const agent = useAuthStore((state) => state.agent);
  const { customersMap, mergeCustomers } = useCustomersStore();


  const localCustomer = useMemo(() => {
    if (!customerId) return null;
    return customersMap[customerId] || null;
  }, [customerId, customersMap]);


  const shouldFetch = !!customerId && !localCustomer && !!agent?.id;

  const { data: customerData, isLoading: customerLoading } = useCustomersQuery({
    insurance_agent_id: agent?.id || '',
    search_term: customerId || '',
    page: 1,
    page_size: 1,
  }, shouldFetch);


  useEffect(() => {
    if (customerData?.items && customerData.items.length > 0) {
      mergeCustomers(customerData.items);
    }
  }, [customerData, mergeCustomers]);

  const customer = localCustomer || (customerData?.items?.[0] ?? null);

  const { data: policiesData, isLoading: policiesLoading } = usePoliciesQuery({
    insurance_agent_id: agent?.id || '',
    customer_id: customer?.id || '',
    page: 1,
    page_size: 100,
  }, !!customer && !!agent?.id);

  useEffect(() => {
    if (customer || (shouldFetch && customerLoading)) {
      document.body.style.overflow = 'hidden';
    } else {
      document.body.style.overflow = 'unset';
    }
    return () => {
      document.body.style.overflow = 'unset';
    };
  }, [customer, shouldFetch, customerLoading]);

  if (!customerId) return null;

  if (shouldFetch && customerLoading && !customer) {
    return typeof document !== 'undefined' ? createPortal(
      <div className="fixed inset-0 z-50 flex items-center justify-center p-4">
        <div className="fixed inset-0 bg-transparent/80 backdrop-blur-sm transition-opacity" onClick={onClose} />
        <div className="relative flex flex-col items-center justify-center gap-4 rounded-xl border border-white/5 bg-black/40 backdrop-blur-xl border border-white/10 shadow-2xl p-12 shadow-2xl">
          <Loader2 className="h-8 w-8 animate-spin text-primary" />
          <p className="text-white/70 font-medium">{getRandomMessage('loadingProfile')}</p>
        </div>
      </div>
    , document.body) : null;
  }

  if (!customer) return null;

  return typeof document !== 'undefined' ? createPortal(
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 sm:p-6">

      <div 
        className="fixed inset-0 bg-transparent/80 backdrop-blur-sm transition-opacity" 
        onClick={onClose}
      />


      <div className="relative flex w-full max-w-4xl max-h-[90vh] flex-col overflow-hidden rounded-xl bg-black/40 backdrop-blur-xl border border-white/10 shadow-2xl">


        <div className="flex items-center justify-between border-b border-white/5 bg-muted/30 px-6 py-4">
          <div>
            <h2 className="text-xl font-semibold tracking-tight text-white">{customer.name}</h2>
            <p className="text-sm text-white/70">Customer Profile & Policies</p>
          </div>
          <button 
            onClick={onClose}
            className="rounded-full p-2 text-white/70 hover:bg-white/5 text-white hover:text-white transition-colors"
          >
            <X className="h-5 w-5" />
          </button>
        </div>


        <div className="flex-1 overflow-y-auto p-6">


          <div className="mb-8 grid gap-6 sm:grid-cols-2 lg:grid-cols-4">
            <div className="space-y-1">
              <span className="text-xs font-medium text-white/70 uppercase tracking-wider">Email</span>
              <p className="text-sm font-medium text-white">{customer.email}</p>
            </div>
            <div className="space-y-1">
              <span className="text-xs font-medium text-white/70 uppercase tracking-wider">Phone</span>
              <p className="text-sm font-medium text-white">{customer.phone_number}</p>
            </div>
            <div className="space-y-1">
              <span className="text-xs font-medium text-white/70 uppercase tracking-wider">Date of Birth</span>
              <p className="text-sm font-medium text-white">
                {new Date(customer.date_of_birth).toLocaleDateString(undefined, { month: 'long', day: 'numeric', year: 'numeric' })}
              </p>
            </div>
            <div className="space-y-1">
              <span className="text-xs font-medium text-white/70 uppercase tracking-wider">Address</span>
              <p className="text-sm font-medium text-white">{customer.address}</p>
            </div>
          </div>


          <div>
            <h3 className="mb-4 text-lg font-semibold tracking-tight text-white flex items-center gap-2">
              <ShieldAlert className="h-5 w-5 text-primary" />
              Active Policies
            </h3>

            <div className="rounded-xl border border-white/5 overflow-hidden shadow-sm">
              {policiesLoading ? (
                <LoadingState message={getRandomMessage('loadingPolicies')} />
              ) : !policiesData?.items || policiesData.items.length === 0 ? (
                <EmptyState 
                  icon={ShieldAlert} 
                  title={getRandomMessage('emptyPolicies')} 
                  description="This customer does not have any active policies." 
                />
              ) : (
                <div className="overflow-auto max-h-[50vh]">
                  <table className="w-full text-left text-sm relative">
                    <thead className="bg-muted/90 backdrop-blur-sm border-b border-white/5 sticky top-0 z-10 shadow-sm">
                      <tr>
                        <th className="px-6 py-4 font-medium text-white/70">Policy Number</th>
                        <th className="px-6 py-4 font-medium text-white/70">Type</th>
                        <th className="px-6 py-4 font-medium text-white/70">Status</th>
                        <th className="px-6 py-4 font-medium text-white/70">Premium</th>
                        <th className="px-6 py-4 font-medium text-white/70">Coverage</th>
                        <th className="px-6 py-4 font-medium text-white/70">Dates</th>
                      </tr>
                    </thead>
                    <tbody className="divide-y divide-border">
                      {policiesData.items.map((policy) => (
                        <tr key={policy.id} className="hover:bg-white/5 transition-colors">
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
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              )}
            </div>
          </div>
        </div>

      </div>
    </div>
  , document.body) : null;
}
