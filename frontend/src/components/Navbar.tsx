import React from 'react';
import { Link, useLocation } from 'react-router-dom';
import { Activity, UserCircle } from 'lucide-react';

export default function Navbar() {
  const location = useLocation();
  if (location.pathname === '/login' || location.pathname === '/') return null;

  return (
    <nav className="border-b bg-card text-card-foreground">
      <div className="flex h-16 items-center px-4 md:px-6 max-w-7xl mx-auto w-full">
        <Link to="/home" className="flex items-center gap-2 font-semibold">
          <Activity className="h-6 w-6 text-primary" />
          <span className="text-lg tracking-tight">Customer 360</span>
        </Link>
        <div className="ml-auto flex items-center space-x-6">
          <Link to="/policies" className="text-sm font-medium text-muted-foreground hover:text-foreground transition-colors">
            Policies
          </Link>
          <Link to="/about" className="text-sm font-medium text-muted-foreground hover:text-foreground transition-colors">
            About
          </Link>
          <Link to="/profile" className="text-primary hover:text-primary/80 transition-colors flex items-center justify-center p-2 rounded-full bg-primary/10">
            <UserCircle className="h-6 w-6" />
          </Link>
        </div>
      </div>
    </nav>
  );
}
