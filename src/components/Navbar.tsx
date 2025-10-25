// src/components/Navbar.tsx
'use client';

import * as NavigationMenu from '@/components/ui/navigation-menu';
import { Link } from 'react-router-dom'; // Jika pakai React Router

export default function Navbar() {
  return (
    <nav className="bg-cream text-gray-800 shadow-md">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex justify-between h-16">
          <div className="flex">
            <div className="flex-shrink-0 flex items-center">
              <Link to="/" className="flex items-center">
            <img
              src="/logo-inara.png" // Simpan di public/logo-inara.png
              alt="Inara Travel"
              className="h-16 w-auto"
            />
          </Link>
            </div>
            <div className="hidden sm:ml-6 sm:flex sm:items-center sm:space-x-8">
              <NavigationMenu.NavigationMenu>
                <NavigationMenu.NavigationMenuList className="flex space-x-8">
                  <NavigationMenu.NavigationMenuItem>
                    <NavigationMenu.NavigationMenuLink asChild>
                      <Link to="/" className="px-3 py-2 rounded-md text-sm font-medium hover:bg-secondary">Home</Link>
                    </NavigationMenu.NavigationMenuLink>
                  </NavigationMenu.NavigationMenuItem>
                  <NavigationMenu.NavigationMenuItem>
                    <NavigationMenu.NavigationMenuLink asChild>
                      <Link to="/packages" className="px-3 py-2 rounded-md text-sm font-medium hover:bg-secondary">Paket</Link>
                    </NavigationMenu.NavigationMenuLink>
                  </NavigationMenu.NavigationMenuItem>
                  <NavigationMenu.NavigationMenuItem>
                    <NavigationMenu.NavigationMenuLink asChild>
                      <Link to="/about" className="px-3 py-2 rounded-md text-sm font-medium hover:bg-secondary">Tentang Kami</Link>
                    </NavigationMenu.NavigationMenuLink>
                  </NavigationMenu.NavigationMenuItem>

                  <NavigationMenu.NavigationMenuItem>
                    <NavigationMenu.NavigationMenuLink asChild>
                      <Link to="/contact" className="px-3 py-2 rounded-md text-sm font-medium hover:bg-secondary">Kontak</Link>
                    </NavigationMenu.NavigationMenuLink>
                  </NavigationMenu.NavigationMenuItem>
                </NavigationMenu.NavigationMenuList>
              </NavigationMenu.NavigationMenu>
            </div>
          </div>
          {/* Mobile menu toggle */}
          <div className="-mr-2 flex sm:hidden">
            <button
              onClick={() => {}}
              className="inline-flex items-center justify-center p-2 rounded-md text-white hover:bg-secondary focus:outline-none"
            >
              <svg className={`block h-6 w-6`} fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 6h16M4 12h16M4 18h16" />
              </svg>
            </button>
          </div>
        </div>
      </div>

      {/* Mobile menu */}
      <div className="sm:hidden">
        <div className="pt-2 pb-3 space-y-1">
          <Link to="/" className="block px-3 py-2 rounded-md text-base font-medium hover:bg-secondary">Home</Link>
          <Link to="/packages" className="block px-3 py-2 rounded-md text-base font-medium hover:bg-secondary">Paket</Link>
          <Link to="/about" className="block px-3 py-2 rounded-md text-base font-medium hover:bg-secondary">Tentang Kami</Link>
          <Link to="/contact" className="block px-3 py-2 rounded-md text-base font-medium hover:bg-secondary">Kontak</Link>
        </div>
      </div>
    </nav>
  );
}