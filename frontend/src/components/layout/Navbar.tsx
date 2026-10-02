import { NavLink, Link } from 'react-router-dom';
import { UserCircle } from 'lucide-react';
import { useAuthStore } from '../../store/useAuthStore';

export function Navbar() {
  const agent = useAuthStore((state) => state.agent);

  const navItems = [
    { name: 'Customer 360', path: '/' },
    { name: 'Policies', path: '/policies' },
    { name: 'Customers', path: '/customers' },
    { name: 'About', path: '/about' },
  ];

  return (
    <header className="sticky top-0 z-50 w-full border-b border-border bg-background/95 backdrop-blur supports-[backdrop-filter]:bg-background/60">
      <div className="container mx-auto flex h-16 items-center justify-between px-4">
        
        {/* Navigation Links */}
        <nav className="flex items-center gap-6">
          {navItems.map((item) => (
            <NavLink
              key={item.path}
              to={item.path}
              className={({ isActive }) =>
                `text-sm font-medium transition-colors hover:text-primary ${
                  isActive ? 'text-primary' : 'text-muted-foreground'
                }`
              }
            >
              {item.name}
            </NavLink>
          ))}
        </nav>

        {/* Profile Button */}
        <div className="flex items-center gap-4">
          <Link to="/profile">
            <button className="flex items-center gap-2 rounded-full border border-border px-4 py-1.5 text-sm font-medium text-foreground transition-colors hover:bg-muted">
              {agent?.profile_image_url ? (
                <img 
                  src={agent.profile_image_url} 
                  alt={agent.name} 
                  className="h-5 w-5 rounded-full object-cover" 
                />
              ) : (
                <UserCircle className="h-5 w-5 text-muted-foreground" />
              )}
              <span>{agent?.name || 'Profile'}</span>
            </button>
          </Link>
        </div>
      </div>
    </header>
  );
}
