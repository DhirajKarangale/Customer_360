import React, { useState } from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Activity, AlertTriangle, CheckCircle2, ChevronDown, Clock, ShieldAlert, Sparkles, TrendingDown, Users, LineChart as LineChartIcon, Bot, MessageSquare } from 'lucide-react';
import { MOCK_CUSTOMERS } from '@/data/mockData';
import ChatAgent from '@/components/ChatAgent';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from 'recharts';
import { useNavigate } from 'react-router-dom';

export default function Home() {
  const navigate = useNavigate();
  const [selectedCustomerId, setSelectedCustomerId] = useState("CUST-101");
  const [offerDispatched, setOfferDispatched] = useState(false);
  const customer = MOCK_CUSTOMERS[selectedCustomerId as keyof typeof MOCK_CUSTOMERS];

  const handleCustomerChange = (e: React.ChangeEvent<HTMLSelectElement>) => {
    setSelectedCustomerId(e.target.value);
    setOfferDispatched(false);
  };

  const handleDispatch = () => {
    setOfferDispatched(true);
  };

  return (
    <div className="p-6 max-w-[1600px] mx-auto w-full space-y-6">
      {/* Header & Selector */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
        <div>
          <h2 className="text-3xl font-bold tracking-tight">Customer 360 Workspace</h2>
          <p className="text-muted-foreground">Unified view and Next Best Action engine powered by Cortex.</p>
        </div>
        <div className="flex items-center gap-2">
          <span className="text-sm font-medium">Select Customer:</span>
          <div className="relative">
            <select 
              className="appearance-none bg-background border border-input text-foreground text-sm rounded-md focus:ring-primary focus:border-primary block w-full p-2.5 pr-8"
              value={selectedCustomerId}
              onChange={handleCustomerChange}
            >
              <option value="CUST-101">CUST-101 (Marcus Vance)</option>
              <option value="CUST-102">CUST-102 (Elena Rostova)</option>
            </select>
            <ChevronDown className="absolute right-2 top-3 h-4 w-4 text-muted-foreground pointer-events-none" />
          </div>
        </div>
      </div>

      <div className="space-y-6">
        {/* KPI Cards */}
        <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
          <Card>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">Annual Premium</CardTitle>
              <TrendingDown className="h-4 w-4 text-muted-foreground" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">{customer.annualPremium}</div>
            </CardContent>
          </Card>
          <Card>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">Tenure</CardTitle>
              <Clock className="h-4 w-4 text-muted-foreground" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">{customer.tenure}</div>
            </CardContent>
          </Card>
          <Card>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">Call Sentiment</CardTitle>
              <Users className="h-4 w-4 text-muted-foreground" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">{customer.sentiment}</div>
            </CardContent>
          </Card>
          <Card>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">Churn Propensity</CardTitle>
              <Activity className="h-4 w-4 text-muted-foreground" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">{customer.churnPropensity}%</div>
              <p className="text-xs text-muted-foreground mt-1">
                {customer.churnPropensity > 50 ? (
                  <span className="text-destructive font-semibold">Critical Risk</span>
                ) : (
                  <span className="text-success font-semibold">Stable</span>
                )}
              </p>
            </CardContent>
          </Card>
        </div>

        {/* Say-vs-Do Alert */}
        {customer.churnPropensity > 50 && (
          <Card className="border-destructive shadow-[0_0_15px_rgba(225,29,72,0.15)] bg-destructive/5 overflow-hidden">
            <div className="bg-destructive/10 p-4 border-b border-destructive/20 flex items-center gap-3">
              <ShieldAlert className="h-6 w-6 text-destructive" />
              <h3 className="text-lg font-bold text-destructive">Say-vs-Do Contradiction Detected</h3>
            </div>
            <CardContent className="p-6 grid md:grid-cols-2 gap-6">
              <div className="space-y-2">
                <h4 className="text-sm font-semibold uppercase tracking-wider text-muted-foreground">What They Said (Audio Transcript)</h4>
                <p className="text-sm p-4 bg-background border rounded-lg italic">"{customer.sayVsDo.whatTheySaid}"</p>
              </div>
              <div className="space-y-2">
                <h4 className="text-sm font-semibold uppercase tracking-wider text-muted-foreground">What They Did (Database Ledger)</h4>
                <p className="text-sm p-4 bg-background border rounded-lg font-medium text-destructive">"{customer.sayVsDo.whatTheyDid}"</p>
              </div>
            </CardContent>
          </Card>
        )}

        {/* Chart Section */}
        <Card>
          <CardHeader>
            <div className="flex items-center gap-2">
              <LineChartIcon className="h-5 w-5 text-primary" />
              <CardTitle>Historical Churn Propensity</CardTitle>
            </div>
            <CardDescription>6-month trend analysis generated by Snowflake Cortex</CardDescription>
          </CardHeader>
          <CardContent>
            <div className="h-[250px] w-full mt-4">
              <ResponsiveContainer width="100%" height="100%">
                <LineChart data={customer.history} margin={{ top: 5, right: 20, bottom: 5, left: 0 }}>
                  <CartesianGrid strokeDasharray="3 3" vertical={false} stroke="hsl(var(--border))" />
                  <XAxis 
                    dataKey="month" 
                    axisLine={false} 
                    tickLine={false} 
                    tick={{ fill: 'hsl(var(--muted-foreground))', fontSize: 12 }} 
                    dy={10}
                  />
                  <YAxis 
                    axisLine={false} 
                    tickLine={false} 
                    tick={{ fill: 'hsl(var(--muted-foreground))', fontSize: 12 }}
                    dx={-10}
                  />
                  <Tooltip 
                    contentStyle={{ backgroundColor: 'hsl(var(--card))', borderColor: 'hsl(var(--border))', borderRadius: '8px' }}
                    itemStyle={{ color: 'hsl(var(--foreground))' }}
                  />
                  <Line 
                    type="monotone" 
                    dataKey="propensity" 
                    stroke="hsl(var(--primary))" 
                    strokeWidth={3}
                    dot={{ r: 4, fill: 'hsl(var(--primary))', strokeWidth: 0 }}
                    activeDot={{ r: 6, strokeWidth: 0 }}
                  />
                </LineChart>
              </ResponsiveContainer>
            </div>
          </CardContent>
        </Card>

        <div className="grid gap-6 md:grid-cols-2">
          {/* Next Best Action */}
          <Card className="flex flex-col">
            <CardHeader>
              <div className="flex items-center gap-2">
                <Sparkles className="h-5 w-5 text-primary" />
                <CardTitle>Next Best Action</CardTitle>
              </div>
              <CardDescription>Cortex AI Recommended Intervention</CardDescription>
            </CardHeader>
            <CardContent className="flex-1 space-y-6">
              <div className="p-4 bg-primary/10 border border-primary/20 rounded-lg">
                <h4 className="font-semibold text-primary mb-2">Recommended Offer:</h4>
                <p className="text-lg font-bold">{customer.nextBestAction.offer}</p>
              </div>
              
              <div className="space-y-3">
                <h4 className="text-sm font-medium text-muted-foreground uppercase tracking-wider">Compliance Checks</h4>
                <div className="space-y-2">
                  {customer.nextBestAction.complianceChecks.map((check, i) => (
                    <div key={i} className="flex items-center justify-between p-2 bg-secondary/50 rounded border">
                      <span className="text-sm">{check.name}</span>
                      <Badge variant="success" className="gap-1"><CheckCircle2 className="h-3 w-3" /> Passed</Badge>
                    </div>
                  ))}
                </div>
              </div>
            </CardContent>
            <div className="p-6 pt-0 mt-auto">
              {!offerDispatched ? (
                <Button onClick={handleDispatch} className="w-full gap-2">
                  <Sparkles className="h-4 w-4" /> Approve & Dispatch Offer
                </Button>
              ) : (
                <Button variant="outline" className="w-full gap-2 border-success text-success hover:bg-success/10 cursor-default" disabled>
                  <CheckCircle2 className="h-4 w-4" /> Offer Dispatched Successfully
                </Button>
              )}
            </div>
          </Card>

          {/* Interaction Logs */}
          <Card>
            <CardHeader>
              <CardTitle>Enriched Interaction Logs</CardTitle>
              <CardDescription>Summaries generated by Cortex LLMs</CardDescription>
            </CardHeader>
            <CardContent className="space-y-4">
              {customer.interactions.map((interaction) => (
                <div key={interaction.id} className="relative pl-6 pb-4 border-l border-border last:border-0 last:pb-0">
                  <div className="absolute left-[-5px] top-1 h-2.5 w-2.5 rounded-full bg-primary border-2 border-background"></div>
                  <div className="space-y-1">
                    <p className="text-xs font-medium text-muted-foreground">{interaction.time}</p>
                    <p className="text-sm bg-secondary/30 p-3 rounded-md border">{interaction.summary}</p>
                  </div>
                </div>
              ))}
            </CardContent>
          </Card>
        </div>

        {/* Big Horizontal Chat Box Banner */}
        <div 
          onClick={() => navigate('/chat')}
          className="w-full mt-8 p-6 bg-secondary/30 hover:bg-secondary/50 border border-primary/20 rounded-xl cursor-pointer transition-all duration-300 flex items-center justify-between group shadow-sm hover:shadow-md"
        >
          <div className="flex items-center gap-4">
            <div className="p-3 bg-primary/10 rounded-full text-primary">
              <Bot className="h-8 w-8" />
            </div>
            <div>
              <h3 className="text-xl font-bold text-foreground">Have a question about this customer?</h3>
              <p className="text-muted-foreground mt-1">Click here to start a chat with the Cortex AI Agent for deep-dive analysis.</p>
            </div>
          </div>
          <div className="hidden md:flex items-center gap-2 px-6 py-3 bg-primary text-primary-foreground rounded-lg font-semibold group-hover:bg-primary/90 transition-colors">
            Start Chatting <MessageSquare className="h-4 w-4 ml-1" />
          </div>
        </div>
      </div>
    </div>
  );
}
