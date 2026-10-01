import React from 'react'

const Footer = () => {
  return (
    <footer className="w-full bg-background border-t border-border mt-auto">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8 flex flex-col md:flex-row justify-between items-center gap-4">
        <div className="flex flex-col items-center md:items-start">
          <span className="text-xl font-bold text-primary">Customer 360</span>
          <span className="text-sm text-muted-foreground mt-1">© 2026 Customer 360</span>
        </div>
        <div className="flex gap-6">
          <a href="/policies" className="text-sm text-muted-foreground hover:text-foreground transition-colors">Policies</a>
          <a href="/about" className="text-sm text-muted-foreground hover:text-foreground transition-colors">About Us</a>
          <a href="#" className="text-sm text-muted-foreground hover:text-foreground transition-colors">Contact</a>
        </div>
      </div>
    </footer>
  )
}

export default Footer
