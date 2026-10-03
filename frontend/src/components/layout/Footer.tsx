import { Link } from 'react-router-dom';
import { ShieldAlert, Mail, ArrowRight } from 'lucide-react';

const GithubIcon = ({ className }: { className?: string }) => (
  <svg className={className} fill="currentColor" viewBox="0 0 24 24">
    <path fillRule="evenodd" d="M12 2C6.477 2 2 6.484 2 12.017c0 4.425 2.865 8.18 6.839 9.504.5.092.682-.217.682-.483 0-.237-.008-.868-.013-1.703-2.782.605-3.369-1.343-3.369-1.343-.454-1.158-1.11-1.466-1.11-1.466-.908-.62.069-.608.069-.608 1.003.07 1.531 1.032 1.531 1.032.892 1.53 2.341 1.088 2.91.832.092-.647.35-1.088.636-1.338-2.22-.253-4.555-1.113-4.555-4.951 0-1.093.39-1.988 1.029-2.688-.103-.253-.446-1.272.098-2.65 0 0 .84-.27 2.75 1.026A9.564 9.564 0 0112 6.844c.85.004 1.705.115 2.504.337 1.909-1.296 2.747-1.027 2.747-1.027.546 1.379.202 2.398.1 2.651.64.7 1.028 1.595 1.028 2.688 0 3.848-2.339 4.695-4.566 4.943.359.309.678.92.678 1.855 0 1.338-.012 2.419-.012 2.747 0 .268.18.58.688.482A10.019 10.019 0 0022 12.017C22 6.484 17.522 2 12 2z" clipRule="evenodd" />
  </svg>
);

const TwitterIcon = ({ className }: { className?: string }) => (
  <svg className={className} fill="currentColor" viewBox="0 0 24 24">
    <path d="M23.953 4.57a10 10 0 01-2.825.775 4.958 4.958 0 002.163-2.723c-.951.555-2.005.959-3.127 1.184a4.92 4.92 0 00-8.384 4.482C7.69 8.095 4.067 6.13 1.64 3.162a4.822 4.822 0 00-.666 2.475c0 1.71.87 3.213 2.188 4.096a4.904 4.904 0 01-2.228-.616v.06a4.923 4.923 0 003.946 4.827 4.996 4.996 0 01-2.212.085 4.936 4.936 0 004.604 3.417 9.867 9.867 0 01-6.102 2.105c-.39 0-.779-.023-1.17-.067a13.995 13.995 0 007.557 2.209c9.053 0 13.998-7.496 13.998-13.985 0-.21 0-.42-.015-.63A9.935 9.935 0 0024 4.59z" />
  </svg>
);

const LinkedinIcon = ({ className }: { className?: string }) => (
  <svg className={className} fill="currentColor" viewBox="0 0 24 24">
    <path fillRule="evenodd" d="M19 0h-14c-2.761 0-5 2.239-5 5v14c0 2.761 2.239 5 5 5h14c2.762 0 5-2.239 5-5v-14c0-2.761-2.238-5-5-5zm-11 19h-3v-11h3v11zm-1.5-12.268c-.966 0-1.75-.79-1.75-1.764s.784-1.764 1.75-1.764 1.75.79 1.75 1.764-.783 1.764-1.75 1.764zm13.5 12.268h-3v-5.604c0-3.368-4-3.113-4 0v5.604h-3v-11h3v1.765c1.396-2.586 7-2.777 7 2.476v6.759z" clipRule="evenodd" />
  </svg>
);

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
