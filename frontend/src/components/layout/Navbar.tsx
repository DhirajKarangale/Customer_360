import { memo, useState } from 'react';
import { NavLink, Link } from 'react-router-dom';
import { UserCircle } from 'lucide-react';
import { useAuthStore } from '../../store/useAuthStore';


export const Navbar = memo(function Navbar() {
  const agent = useAuthStore((state) => state.agent);
  const [imgError, setImgError] = useState(false);

  const navItems = [
    { name: 'Customer 360', path: '/' },
    { name: 'Policies', path: '/policies' },
    { name: 'Customers', path: '/customers' },
    { name: 'About', path: '/about' },
  ];

  return (
    <header className="sticky top-0 z-50 w-full border-b border-white/5 bg-transparent/95 backdrop-blur supports-[backdrop-filter]:bg-transparent/60">
      <div className="container mx-auto flex h-16 items-center justify-between px-4">


        <nav className="flex items-center gap-6">
          {navItems.map((item) => (
            <NavLink
              key={item.path}
              to={item.path}
              className={({ isActive }) =>
                `text-sm font-medium transition-colors hover:text-primary ${
                  isActive ? 'text-primary' : 'text-white/70'
                }`
              }
            >
              {item.name}
            </NavLink>
          ))}
        </nav>


        <div className="flex items-center gap-4">
          <Link 
            to="/profile"
            className="flex items-center gap-2 rounded-full border border-white/5 px-4 py-1.5 text-sm font-medium text-white transition-colors hover:bg-white/5 text-white"
          >
            {!imgError && agent?.profile_image_url ? (
              <img 
                src={agent.profile_image_url} 
                alt={agent.name} 
                className="h-6 w-6 rounded-full object-cover object-top"
                onError={() => setImgError(true)}
              />
            ) : (
              <UserCircle className="h-5 w-5 text-white/70" />
            )}
            <span>{agent?.name || 'Profile'}</span>
          </Link>
        </div>
      </div>
    </header>
  );
});
