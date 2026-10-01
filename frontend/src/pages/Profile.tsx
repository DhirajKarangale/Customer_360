import React from 'react';
import { useNavigate } from 'react-router-dom';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Database, ShieldCheck, User, Moon, Sun, LogOut, Settings } from 'lucide-react';
import { useAppStore } from '../store/useAppStore';

export default function Profile() {
  const navigate = useNavigate();
  const { theme, toggleTheme, logout } = useAppStore();

  const handleLogout = () => {
    logout();
    navigate('/login');
  };

  return (
    <div className="p-6 max-w-7xl mx-auto space-y-6 w-full">
      <div>
        <h2 className="text-3xl font-bold tracking-tight">Operator Profile</h2>
        <p className="text-muted-foreground">Session and context details for the current user.</p>
      </div>
      
      <div className="grid gap-6 md:grid-cols-2">
        <Card>
          <CardHeader>
            <div className="flex items-center gap-2">
              <User className="h-5 w-5 text-primary" />
              <CardTitle>Operator Information</CardTitle>
            </div>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="space-y-1">
              <p className="text-sm font-medium text-muted-foreground">Name</p>
              <p className="font-semibold">Sarah Connor</p>
            </div>
            <div className="space-y-1">
              <p className="text-sm font-medium text-muted-foreground">Role / Title</p>
              <p className="font-semibold">Senior Retention Specialist</p>
            </div>
            <div className="space-y-1">
              <p className="text-sm font-medium text-muted-foreground">Employee ID</p>
              <p className="font-semibold text-primary">OP-9942</p>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <div className="flex items-center gap-2">
              <Database className="h-5 w-5 text-primary" />
              <CardTitle>Snowflake Session Context</CardTitle>
            </div>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="grid grid-cols-2 gap-4">
              <div className="p-3 bg-secondary/50 rounded-md border">
                <p className="text-xs font-medium text-muted-foreground uppercase tracking-wider">Active Role</p>
                <p className="text-sm font-bold mt-1">RETENTION_SPECIALIST_ROLE</p>
              </div>
              <div className="p-3 bg-secondary/50 rounded-md border">
                <p className="text-xs font-medium text-muted-foreground uppercase tracking-wider">Target Schema</p>
                <p className="text-sm font-bold mt-1">CHURN360_DB.PUBLIC</p>
              </div>
            </div>
            <div className="flex items-center justify-between p-3 border rounded-md border-primary/20 bg-primary/5">
              <div className="flex items-center gap-2">
                <ShieldCheck className="h-4 w-4 text-emerald-500" />
                <span className="text-sm font-medium">Dynamic Masking</span>
              </div>
              <span className="text-xs font-bold text-emerald-500">ACTIVE PII HIDING</span>
            </div>
          </CardContent>
        </Card>

        <Card className="md:col-span-2">
          <CardHeader>
            <div className="flex items-center gap-2">
              <Settings className="h-5 w-5 text-primary" />
              <CardTitle>Application Settings</CardTitle>
            </div>
          </CardHeader>
          <CardContent className="flex flex-col sm:flex-row gap-4 items-center justify-between">
            <div className="flex flex-col">
              <span className="font-semibold">Theme Preference</span>
              <span className="text-sm text-muted-foreground">Toggle between day and night mode</span>
            </div>
            <div className="flex gap-4">
              <Button variant="outline" onClick={toggleTheme} className="flex items-center gap-2">
                {theme === 'dark' ? <Sun className="h-4 w-4" /> : <Moon className="h-4 w-4" />}
                {theme === 'dark' ? 'Light Mode' : 'Dark Mode'}
              </Button>
              <Button variant="destructive" onClick={handleLogout} className="flex items-center gap-2">
                <LogOut className="h-4 w-4" />
                Logout
              </Button>
            </div>
          </CardContent>
        </Card>
      </div>
    </div>
  );
}
