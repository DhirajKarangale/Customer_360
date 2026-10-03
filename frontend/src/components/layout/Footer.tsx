import { Link } from 'react-router-dom';
import { ShieldAlert, ArrowRight } from 'lucide-react';



export function Footer() {
  return (
    <footer className="relative mt-20 border-t border-white/10 bg-black/40 backdrop-blur-2xl">
      {/* Decorative gradient line */}
      <div className="absolute top-0 left-0 w-full h-[1px] bg-gradient-to-r from-transparent via-primary/50 to-transparent" />

      <div className="container mx-auto px-6 py-12">
        <div className="grid grid-cols-1 gap-12 md:grid-cols-2 lg:grid-cols-4">

          {/* Brand & Intro */}
          <div className="flex flex-col gap-4 lg:col-span-1">
            <Link to="/" className="flex items-center gap-2 transition-transform hover:scale-105 active:scale-95 w-fit">
              <div className="flex h-10 w-10 items-center justify-center rounded-xl bg-gradient-to-br from-indigo-500 to-purple-600 shadow-[0_0_15px_rgba(99,102,241,0.5)]">
                <ShieldAlert className="h-5 w-5 text-white" />
              </div>
              <span className="bg-gradient-to-r from-white to-white/60 bg-clip-text text-xl font-bold text-transparent">
                Cust360.ai
              </span>
            </Link>
            <p className="mt-2 text-sm leading-relaxed text-white/60">
              Empowering insurance agents with AI-driven insights, seamless portfolio management, and real-time customer intelligence.
            </p>
          </div>

          {/* Quick Links */}
          <div className="flex flex-col gap-4">
            <h3 className="text-sm font-semibold uppercase tracking-wider text-white">Platform</h3>
            <ul className="flex flex-col gap-3">
              <li>
                <Link to="/" className="group flex items-center text-sm text-white/60 transition-colors hover:text-primary">
                  <ArrowRight className="mr-2 h-3 w-3 opacity-0 transition-all group-hover:opacity-100 group-hover:translate-x-1" />
                  Dashboard
                </Link>
              </li>
              <li>
                <Link to="/policies" className="group flex items-center text-sm text-white/60 transition-colors hover:text-primary">
                  <ArrowRight className="mr-2 h-3 w-3 opacity-0 transition-all group-hover:opacity-100 group-hover:translate-x-1" />
                  Policies
                </Link>
              </li>
              <li>
                <Link to="/customers" className="group flex items-center text-sm text-white/60 transition-colors hover:text-primary">
                  <ArrowRight className="mr-2 h-3 w-3 opacity-0 transition-all group-hover:opacity-100 group-hover:translate-x-1" />
                  Customers
                </Link>
              </li>
            </ul>
          </div>

          {/* Connect 
          <div className="flex flex-col gap-4">
            <h3 className="text-sm font-semibold uppercase tracking-wider text-white">Connect</h3>
            <div className="flex items-center gap-4">
              <a href="#" className="flex h-10 w-10 items-center justify-center rounded-full bg-white/5 text-white/60 transition-all hover:bg-primary hover:text-white hover:scale-110 hover:shadow-[0_0_15px_rgba(99,102,241,0.5)]">
                <GithubIcon className="h-5 w-5" />
              </a>
              <a href="#" className="flex h-10 w-10 items-center justify-center rounded-full bg-white/5 text-white/60 transition-all hover:bg-[#1DA1F2] hover:text-white hover:scale-110 hover:shadow-[0_0_15px_rgba(29,161,242,0.5)]">
                <TwitterIcon className="h-5 w-5" />
              </a>
              <a href="#" className="flex h-10 w-10 items-center justify-center rounded-full bg-white/5 text-white/60 transition-all hover:bg-[#0A66C2] hover:text-white hover:scale-110 hover:shadow-[0_0_15px_rgba(10,102,194,0.5)]">
                <LinkedinIcon className="h-5 w-5" />
              </a>
              <a href="#" className="flex h-10 w-10 items-center justify-center rounded-full bg-white/5 text-white/60 transition-all hover:bg-emerald-500 hover:text-white hover:scale-110 hover:shadow-[0_0_15px_rgba(16,185,129,0.5)]">
                <Mail className="h-5 w-5" />
              </a>
            </div>
            <p className="mt-4 text-xs text-white/40">
              Ready to transform your agency? Reach out to our team today.
            </p>
          </div>
          */}

        </div>

        {/* Bottom Bar */}
        <div className="mt-12 flex flex-col items-center justify-between border-t border-white/10 pt-8 sm:flex-row gap-4 text-center sm:text-left">
          <p className="text-sm text-white/50">
            &copy; {new Date().getFullYear()} Customer 360 AI Platform. All rights reserved.
          </p>
          <div className="flex gap-6 text-sm text-white/50">
            <Link to="/privacy" className="hover:text-white transition-colors">Privacy Policy</Link>
            <Link to="/terms" className="hover:text-white transition-colors">Terms of Service</Link>
            <Link to="/cookies" className="hover:text-white transition-colors">Cookie Policy</Link>
          </div>
        </div>
      </div>
    </footer>
  );
}
