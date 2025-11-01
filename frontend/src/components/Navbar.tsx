// src/components/Navbar.tsx
import { useState } from "react";
import { Link, useLocation } from "react-router-dom";
import { Menu, X } from "lucide-react";
import { Button } from "@/components/ui/button";
import { cn } from "@/lib/utils"; // Pastikan Anda punya fungsi cn di utils.ts

export default function Navbar() {
  const [isMobileMenuOpen, setIsMobileMenuOpen] = useState(false);
  const location = useLocation();

  const toggleMobileMenu = () => setIsMobileMenuOpen(!isMobileMenuOpen);

  const navItems = [
    { to: "/", label: "Home" },
    { to: "/packages", label: "Paket" },
    { to: "/about", label: "Tentang Kami" },
    { to: "/contact", label: "Kontak" },
  ];

  return (
    <nav className="bg-background/80 backdrop-blur-md text-foreground shadow-md sticky top-0 z-40">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex justify-between h-16">
          {/* Logo */}
          <div className="flex items-center">
            <Link to="/" className="flex items-center">
              <img
                src="/logo-inara.png" // Pastikan file ini ada di folder /public
                alt="Inara Travel Logo"
                className="h-16 w-auto"
              />
            </Link>
          </div>

          {/* Desktop Menu */}
          <div className="hidden md:flex items-center space-x-8">
            {navItems.map((item) => (
              <Link
                key={item.to}
                to={item.to}
                className={cn(
                  "px-3 py-2 rounded-md text-sm font-medium transition-colors",
                  location.pathname === item.to
                    ? "text-primary bg-secondary"
                    : "hover:text-primary hover:bg-secondary/50"
                )}
              >
                {item.label}
              </Link>
            ))}
          </div>

          {/* Mobile menu button */}
          <div className="md:hidden flex items-center">
            <Button
              variant="ghost"
              size="sm"
              onClick={toggleMobileMenu}
              aria-label="Toggle menu"
            >
              {isMobileMenuOpen ? (
                <X className="h-6 w-6" />
              ) : (
                <Menu className="h-6 w-6" />
              )}
            </Button>
          </div>
        </div>
      </div>

      {/* Mobile Menu */}
      {isMobileMenuOpen && (
        <div className="md:hidden">
          <div className="px-2 pt-2 pb-3 space-y-1 sm:px-3 bg-background border-t">
            {navItems.map((item) => (
              <Link
                key={item.to}
                to={item.to}
                onClick={toggleMobileMenu} // Tutup menu setelah navigasi
                className={cn(
                  "block px-3 py-2 rounded-md text-base font-medium transition-colors",
                  location.pathname === item.to
                    ? "text-primary bg-secondary"
                    : "hover:text-primary hover:bg-secondary/50"
                )}
              >
                {item.label}
              </Link>
            ))}
          </div>
        </div>
      )}
    </nav>
  );
}
