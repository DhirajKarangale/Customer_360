import { useState, useEffect, useMemo } from 'react';
import { StaggerContainer, StaggerItem } from '../components/layout/PageWrapper';
import { useAuthStore } from '../store/useAuthStore';
import { usePoliciesQuery } from '../api/policies';
import { useSuggestionsQuery } from '../api/agents';
import {
  ShieldAlert,
  Wallet,
  Users,
  Clock,
  Sparkles,
  Loader2,
  TrendingUp,
  AlertTriangle
} from 'lucide-react';
import {
  PieChart,
  Pie,
  Cell,
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  Legend
} from 'recharts';
import { getRandomMessage } from '../utils/messages';


const CHART_COLORS = ['#3b82f6', '#10b981', '#f59e0b', '#ef4444', '#8b5cf6'];

export default function Customer360Page() {
  const agent = useAuthStore((state) => state.agent);



  const { data: policiesData, isLoading: policiesLoading } = usePoliciesQuery(
    {
      insurance_agent_id: agent?.id || '',
      page: 1,
      page_size: 100,
    },
    !!agent?.id
  );


  const { data: suggestionsData, isLoading: suggestionsLoading } = useSuggestionsQuery(
    agent?.id || '',
    !!agent?.id
  );


  const [liveSuggestionText, setLiveSuggestionText] = useState<string>('');
  const [isGenerating, setIsGenerating] = useState(false);

  useEffect(() => {

    if (suggestionsData?.message) {

      setLiveSuggestionText(suggestionsData.message);
      if (suggestionsData.message.length < 150 && !suggestionsData.message.includes('\n')) {
        setIsGenerating(true);
      } else {
        setIsGenerating(false);
      }
    }
  }, [suggestionsData]);


  useEffect(() => {
    const handleSuggestionUpdate = (e: Event) => {
      const customEvent = e as CustomEvent<{ jobId: string; content: string }>;
      const { content } = customEvent.detail;

      if (content) {
        setLiveSuggestionText(content.replace(/\[DONE\]/g, ''));
        setIsGenerating(false); 
      }
    };

    window.addEventListener('agent_suggestions_updated', handleSuggestionUpdate);
    return () => {
      window.removeEventListener('agent_suggestions_updated', handleSuggestionUpdate);
    };
  }, []);


  const metrics = useMemo(() => {
    if (!policiesData?.items) return null;

    const policies = policiesData.items;

    let activePremium = 0;
    let totalCoverage = 0;
    let expiringSoonCount = 0;
    const uniqueCustomers = new Set<string>();

    const now = new Date();
    const thirtyDaysFromNow = new Date();
    thirtyDaysFromNow.setDate(now.getDate() + 30);


    const typeDistribution: Record<string, number> = {};
    const renewalsByMonth: Record<string, number> = {};

    policies.forEach(p => {
      if (p.status === 'Active') {
        activePremium += Number(p.premium_amount) || 0;
        totalCoverage += Number(p.coverage_amount) || 0;
        uniqueCustomers.add(p.customer_id);


        const endDate = new Date(p.end_date);
        if (endDate >= now && endDate <= thirtyDaysFromNow) {
          expiringSoonCount++;
        }


        typeDistribution[p.policy_type] = (typeDistribution[p.policy_type] || 0) + Number(p.premium_amount);


        const monthKey = endDate.toLocaleString('default', { month: 'short', year: 'numeric' });

        if (endDate >= now) {
          renewalsByMonth[monthKey] = (renewalsByMonth[monthKey] || 0) + 1;
        }
      }
    });

    const crossSellRatio = uniqueCustomers.size > 0 
      ? (policies.filter(p => p.status === 'Active').length / uniqueCustomers.size).toFixed(1) 
      : '0.0';


    const pieData = Object.entries(typeDistribution).map(([name, value]) => ({ name, value })).sort((a, b) => b.value - a.value);


    const barData = Object.entries(renewalsByMonth)
      .map(([name, count]) => ({ name, count }))
      .sort((a, b) => new Date(`1 ${a.name}`).getTime() - new Date(`1 ${b.name}`).getTime())
      .slice(0, 5); 

    return {
      activePremium,
      totalCoverage,
      expiringSoonCount,
      crossSellRatio,
      pieData,
      barData
    };
  }, [policiesData]);


  const formatCurrency = (val: number) => `$${val.toLocaleString(undefined, { maximumFractionDigits: 0 })}`;

  return (
    <div className="space-y-6">


      <div className="flex flex-col gap-1">
        <h1 className="text-2xl font-bold tracking-tight text-white">Welcome back, {agent?.name?.split(' ')[0] || 'Agent'}</h1>
        <p className="text-white/70">Here is your portfolio overview and smart suggestions for today.</p>
      </div>

      <div className="grid grid-cols-1 gap-6 xl:grid-cols-3">


        <div className="flex flex-col gap-6 xl:col-span-2">


          {policiesLoading ? (
            <div className="flex h-32 items-center justify-center rounded-xl border border-white/5 bg-black/40 backdrop-blur-xl border border-white/10 shadow-2xl shadow-sm">
               <Loader2 className="h-6 w-6 animate-spin text-primary" />
            </div>
          ) : (
            <StaggerContainer className="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-4">

              <StaggerItem className="flex flex-col gap-2 rounded-xl border border-white/5 bg-black/40 backdrop-blur-xl border border-white/10 shadow-2xl p-5 shadow-sm transition-all hover:shadow-md">
                <div className="flex items-center gap-2 text-white/70">
                  <Wallet className="h-4 w-4 text-emerald-500" />
                  <span className="text-sm font-medium">Active Premium</span>
                </div>
                <div className="text-2xl font-bold text-white">
                  {metrics ? formatCurrency(metrics.activePremium) : '$0'}
                </div>
              </StaggerItem>

              <StaggerItem className="flex flex-col gap-2 rounded-xl border border-white/5 bg-black/40 backdrop-blur-xl border border-white/10 shadow-2xl p-5 shadow-sm transition-all hover:shadow-md">
                <div className="flex items-center gap-2 text-white/70">
                  <ShieldAlert className="h-4 w-4 text-blue-500" />
                  <span className="text-sm font-medium">Total Coverage</span>
                </div>
                <div className="text-2xl font-bold text-white">
                  {metrics ? formatCurrency(metrics.totalCoverage) : '$0'}
                </div>
              </StaggerItem>

              <StaggerItem className="flex flex-col gap-2 rounded-xl border border-white/5 bg-black/40 backdrop-blur-xl border border-white/10 shadow-2xl p-5 shadow-sm transition-all hover:shadow-md">
                <div className="flex items-center gap-2 text-white/70">
                  <AlertTriangle className="h-4 w-4 text-amber-500" />
                  <span className="text-sm font-medium">Expiring Soon (30d)</span>
                </div>
                <div className="text-2xl font-bold text-white">
                  {metrics?.expiringSoonCount || 0}
                  <span className="ml-2 text-xs font-normal text-white/70">policies</span>
                </div>
              </StaggerItem>

              <StaggerItem className="flex flex-col gap-2 rounded-xl border border-white/5 bg-black/40 backdrop-blur-xl border border-white/10 shadow-2xl p-5 shadow-sm transition-all hover:shadow-md">
                <div className="flex items-center gap-2 text-white/70">
                  <Users className="h-4 w-4 text-purple-500" />
                  <span className="text-sm font-medium">Cross-Sell Ratio</span>
                </div>
                <div className="text-2xl font-bold text-white">
                  {metrics?.crossSellRatio || '0.0'}
                  <span className="ml-2 text-xs font-normal text-white/70">per client</span>
                </div>
              </StaggerItem>

            </StaggerContainer>
          )}


          <StaggerContainer delay={0.2} className="grid grid-cols-1 gap-6 lg:grid-cols-2">


            <StaggerItem className="flex min-h-[350px] flex-col rounded-xl border border-white/5 bg-black/40 backdrop-blur-xl border border-white/10 shadow-2xl p-6 shadow-sm">
              <h3 className="mb-6 font-semibold tracking-tight flex items-center gap-2 text-white">
                <TrendingUp className="h-4 w-4 text-primary" />
                Revenue by Policy Type
              </h3>
              <div className="flex-1 w-full relative">
                {policiesLoading || !metrics ? (
                  <div className="absolute inset-0 flex items-center justify-center"><Loader2 className="h-6 w-6 animate-spin text-white/40" /></div>
                ) : metrics.pieData.length === 0 ? (
                  <div className="absolute inset-0 flex items-center justify-center text-sm text-white/70 px-4 text-center">{getRandomMessage('emptyPolicies')}</div>
                ) : (
                  <ResponsiveContainer width="100%" height={260}>
                    <PieChart>
                      <Pie
                        data={metrics.pieData}
                        cx="50%"
                        cy="50%"
                        innerRadius={60}
                        outerRadius={90}
                        paddingAngle={5}
                        dataKey="value"
                      >
                        {metrics.pieData.map((_, index) => (
                          <Cell key={`cell-${index}`} fill={CHART_COLORS[index % CHART_COLORS.length]} />
                        ))}
                      </Pie>
                      <Tooltip 
                        formatter={(value: any) => formatCurrency(Number(value))}
                        contentStyle={{ borderRadius: '8px', border: '1px solid #27272a', backgroundColor: '#09090b', color: '#fafafa' }}
                        itemStyle={{ color: '#fafafa' }}
                      />
                      <Legend verticalAlign="bottom" height={36} iconType="circle" />
                    </PieChart>
                  </ResponsiveContainer>
                )}
              </div>
            </StaggerItem>


            <StaggerItem className="flex min-h-[350px] flex-col rounded-xl border border-white/5 bg-black/40 backdrop-blur-xl border border-white/10 shadow-2xl p-6 shadow-sm">
              <h3 className="mb-6 font-semibold tracking-tight flex items-center gap-2 text-white">
                <Clock className="h-4 w-4 text-amber-500" />
                Upcoming Renewals Pipeline
              </h3>
              <div className="flex-1 w-full relative">
                {policiesLoading || !metrics ? (
                  <div className="absolute inset-0 flex items-center justify-center"><Loader2 className="h-6 w-6 animate-spin text-white/40" /></div>
                ) : metrics.barData.length === 0 ? (
                  <div className="absolute inset-0 flex items-center justify-center text-sm text-white/70 px-4 text-center">{getRandomMessage('emptyPolicies')}</div>
                ) : (
                  <ResponsiveContainer width="100%" height={260}>
                    <BarChart data={metrics.barData} margin={{ top: 10, right: 10, left: -20, bottom: 0 }}>
                      <CartesianGrid strokeDasharray="3 3" vertical={false} stroke="#27272a" opacity={0.5} />
                      <XAxis dataKey="name" axisLine={false} tickLine={false} tick={{ fontSize: 12, fill: '#a1a1aa' }} dy={10} />
                      <YAxis axisLine={false} tickLine={false} tick={{ fontSize: 12, fill: '#a1a1aa' }} />
                      <Tooltip 
                        cursor={{ fill: '#27272a' }}
                        contentStyle={{ borderRadius: '8px', border: '1px solid #27272a', backgroundColor: '#09090b', color: '#fafafa' }}
                        itemStyle={{ color: '#fafafa' }}
                      />
                      <Bar dataKey="count" fill="#3b82f6" radius={[4, 4, 0, 0]} barSize={40} name="Policies Expiring" />
                    </BarChart>
                  </ResponsiveContainer>
                )}
              </div>
            </StaggerItem>

          </StaggerContainer>
        </div>


        <div className="relative xl:col-span-1 h-[400px] xl:h-auto">
          <div className="flex flex-col rounded-xl border border-white/10 bg-black/40 backdrop-blur-xl shadow-2xl overflow-hidden h-full xl:absolute xl:inset-0">
            <div className="flex items-center justify-between border-b border-white/10 bg-white/5 px-6 py-4">
              <div className="flex items-center gap-2">
                <Sparkles className="h-5 w-5 text-indigo-500" />
                <h2 className="text-lg font-semibold tracking-tight text-white">Today's Suggestions</h2>
              </div>
              {isGenerating && <Loader2 className="h-4 w-4 animate-spin text-indigo-500" />}
            </div>

          <div className="flex-1 overflow-y-auto p-6 scroll-smooth">
            {suggestionsLoading && !liveSuggestionText ? (
              <div className="flex flex-col items-center justify-center h-full gap-4 text-white/70 opacity-70">
                <Loader2 className="h-6 w-6 animate-spin text-indigo-500" />
                <p className="text-sm text-center px-4">{getRandomMessage('aiSuggestionsLoading')}</p>
              </div>
            ) : (
              <div className="w-full space-y-4">
                {liveSuggestionText ? (
                  <div className="text-sm text-white">
                    {/<[a-z][\s\S]*>/i.test(liveSuggestionText) ? (
                      <div className="llm-content" dangerouslySetInnerHTML={{ __html: liveSuggestionText.replace(/\[DONE\]/g, '') }} />
                    ) : (
                      <div className="whitespace-pre-wrap">{liveSuggestionText.replace(/\[DONE\]/g, '')}</div>
                    )}
                    {isGenerating && (
                      <span className="inline-block w-2 h-4 ml-1 bg-indigo-500 animate-pulse align-middle rounded-full"></span>
                    )}
                  </div>
                ) : (
                  <div className="text-center text-white/70 pt-10 px-4">
                    {getRandomMessage('aiSuggestionsEmpty')}
                  </div>
                )}
              </div>
            )}
          </div>
        </div>
        </div>

      </div>
    </div>
  );
}
