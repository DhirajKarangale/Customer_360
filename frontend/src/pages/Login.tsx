import React from 'react';
import { useNavigate } from 'react-router-dom';
import { Card, CardContent, CardDescription, CardFooter, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Shield, Database } from 'lucide-react';

export default function Login() {
  const navigate = useNavigate();

  const handleLogin = (e) => {
    e.preventDefault();
    navigate('/home');
  };

  return (
    <div className="flex-1 flex items-center justify-center p-4">
      <div className="w-full max-w-md space-y-6">
        <div className="flex flex-col items-center space-y-2 text-center">
          <div className="p-3 bg-primary/10 rounded-full">
            <Database className="h-10 w-10 text-primary" />
          </div>
          <h1 className="text-2xl font-bold tracking-tight text-foreground">Customer 360</h1>
          <p className="text-sm text-muted-foreground">Powered by Snowflake Cortex</p>
        </div>
        
        <Card>
          <CardHeader>
            <CardTitle>Welcome back</CardTitle>
            <CardDescription>Enter your credentials to access the workspace.</CardDescription>
          </CardHeader>
          <form onSubmit={handleLogin}>
            <CardContent className="space-y-4">
              <div className="space-y-2">
                <label className="text-sm font-medium leading-none peer-disabled:cursor-not-allowed peer-disabled:opacity-70">
                  Email
                </label>
                <Input type="email" defaultValue="demo.user@snowflake.com" required />
              </div>
              <div className="space-y-2">
                <div className="flex items-center justify-between">
                  <label className="text-sm font-medium leading-none peer-disabled:cursor-not-allowed peer-disabled:opacity-70">
                    Password
                  </label>
                </div>
                <Input type="password" defaultValue="••••••••" required />
              </div>
            </CardContent>
            <CardFooter className="flex flex-col space-y-4">
              <Button type="submit" className="w-full">
                Launch Workspace
              </Button>
              <div className="flex items-center justify-center gap-2 text-xs text-muted-foreground w-full bg-secondary/50 p-2 rounded-md border">
                <Shield className="h-4 w-4 text-emerald-500" />
                Protected by Snowflake Dynamic Masking & RBAC
              </div>
            </CardFooter>
          </form>
        </Card>
      </div>
    </div>
  );
}
