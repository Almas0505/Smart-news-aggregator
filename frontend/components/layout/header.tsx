"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import { Newspaper, Search, Menu, X, Sun, Moon, User } from "lucide-react";
import { useState } from "react";
import { useTheme } from "next-themes";
import { cn } from "@/lib/utils";

const navigation = [
  { name: "Home", href: "/" },
  { name: "Latest", href: "/latest" },
  { name: "Categories", href: "/categories" },
  { name: "Trending", href: "/trending" },
  { name: "For You", href: "/for-you" },
];

export function Header() {
  const pathname = usePathname();
  const { theme, setTheme } = useTheme();
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false);
  const [searchOpen, setSearchOpen] = useState(false);

  return (
    <header className="sticky top-0 z-50 w-full border-b bg-background/95 backdrop-blur supports-[backdrop-filter]:bg-background/60">
      <nav className="container flex h-16 items-center justify-between">
        {/* Logo */}
        <Link href="/" className="flex items-center space-x-2">
          <div className="flex h-10 w-10 items-center justify-center rounded-lg bg-primary">
            <Newspaper className="h-6 w-6 text-primary-foreground" />
          </div>
          <span className="hidden font-bold sm:inline-block text-xl">
            Smart<span className="text-primary">News</span>
          </span>
        </Link>

        {/* Desktop Navigation */}
        <div className="hidden md:flex md:items-center md:space-x-1">
          {navigation.map((item) => (
            <Link
              key={item.name}
              href={item.href}
              className={cn(
                "rounded-md px-3 py-2 text-sm font-medium transition-colors hover:bg-accent hover:text-accent-foreground",
                pathname === item.href
                  ? "bg-accent text-accent-foreground"
                  : "text-muted-foreground"
              )}
            >
              {item.name}
            </Link>
          ))}
        </div>

        {/* Right Section */}
        <div className="flex items-center space-x-2">
          {/* Search Button */}
          <button
            onClick={() => setSearchOpen(!searchOpen)}
            className="flex h-10 w-10 items-center justify-center rounded-md hover:bg-accent"
            aria-label="Search"
          >
            <Search className="h-5 w-5" />
          </button>

          {/* Theme Toggle */}
          <button
            onClick={() => setTheme(theme === "dark" ? "light" : "dark")}
            className="flex h-10 w-10 items-center justify-center rounded-md hover:bg-accent"
            aria-label="Toggle theme"
          >
            <Sun className="h-5 w-5 rotate-0 scale-100 transition-all dark:-rotate-90 dark:scale-0" />
            <Moon className="absolute h-5 w-5 rotate-90 scale-0 transition-all dark:rotate-0 dark:scale-100" />
          </button>

          {/* User Profile */}
          <Link
            href="/profile"
            className="hidden sm:flex h-10 w-10 items-center justify-center rounded-md hover:bg-accent"
            aria-label="Profile"
          >
            <User className="h-5 w-5" />
          </Link>

          {/* Mobile Menu Toggle */}
          <button
            onClick={() => setMobileMenuOpen(!mobileMenuOpen)}
            className="flex md:hidden h-10 w-10 items-center justify-center rounded-md hover:bg-accent"
            aria-label="Toggle menu"
          >
            {mobileMenuOpen ? (
              <X className="h-6 w-6" />
            ) : (
              <Menu className="h-6 w-6" />
            )}
          </button>
        </div>
      </nav>

      {/* Mobile Menu */}
      {mobileMenuOpen && (
        <div className="md:hidden border-t">
          <div className="container space-y-1 py-4">
            {navigation.map((item) => (
              <Link
                key={item.name}
                href={item.href}
                onClick={() => setMobileMenuOpen(false)}
                className={cn(
                  "block rounded-md px-3 py-2 text-base font-medium transition-colors",
                  pathname === item.href
                    ? "bg-accent text-accent-foreground"
                    : "text-muted-foreground hover:bg-accent hover:text-accent-foreground"
                )}
              >
                {item.name}
              </Link>
            ))}
            <Link
              href="/profile"
              onClick={() => setMobileMenuOpen(false)}
              className="flex items-center space-x-2 rounded-md px-3 py-2 text-base font-medium text-muted-foreground hover:bg-accent hover:text-accent-foreground"
            >
              <User className="h-5 w-5" />
              <span>Profile</span>
            </Link>
          </div>
        </div>
      )}

      {/* Search Overlay */}
      {searchOpen && (
        <div className="border-t">
          <div className="container py-4">
            <div className="relative">
              <Search className="absolute left-3 top-1/2 h-5 w-5 -translate-y-1/2 text-muted-foreground" />
              <input
                type="search"
                placeholder="Search news..."
                className="w-full rounded-md border bg-background pl-10 pr-4 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-ring"
                autoFocus
                onKeyDown={(e) => {
                  if (e.key === "Escape") {
                    setSearchOpen(false);
                  }
                }}
              />
            </div>
          </div>
        </div>
      )}
    </header>
  );
}
