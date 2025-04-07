"use client";

import { useState } from "react";
import Link from "next/link";
import { Menu, X, User, LogOut } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Sheet, SheetContent, SheetTrigger } from "@/components/ui/sheet";
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuTrigger,
  DropdownMenuItem,
  DropdownMenuSeparator,
} from "@/components/ui/dropdown-menu";
import { useAuth } from "@/lib/auth-context";
import { Avatar, AvatarFallback, AvatarImage } from "@/components/ui/avatar";

const navLinks = [
  {
    title: "Home",
    href: "/",
    submenu: [
      { title: "My Account", href: "/account" },
      { title: "Recommendations", href: "/recommendations" },
    ],
  },
  {
    title: "Build Your PC",
    href: "/build",
    submenu: [
      { title: "Browse", href: "/browse"},
      { title: "Build", href: "/build" },
      { title: "Checkout", href: "/checkout" }, // Added checkout as a purchase option
      { title: "Upgrade", href: "/upgrade" },
      { title: "Catalog", href: "/catalog" },
    ],
  },
  {
    title: "Support",
    href: "/support",
    submenu: [
      { title: "Refund", href: "/orders" } // This is correctly set up already
    ],
  },
  {
    title: "About Us",
    href: "/about",
    submenu: [{ title: "The Team", href: "/about" }],
  },
];

export default function Navbar() {
  const [mobileOpen, setMobileOpen] = useState(false);
  const { user, signOut } = useAuth();

  const handleSignOut = async () => {
    await signOut();
    // No need to redirect, the auth state change will trigger UI updates
  };

  // Get user initials for avatar fallback
  const getUserInitials = () => {
    if (!user) return "?";
    if (user.displayName) {
      return user.displayName
        .split(" ")
        .map(name => name[0])
        .join("")
        .toUpperCase();
    }
    return user.email ? user.email[0].toUpperCase() : "U";
  };

  return (
    <header className="w-full border-b bg-background">
      <div className="max-w-6xl mx-auto px-4 flex items-center justify-between h-16">
        {/* Logo */}
        <Link href="/" className="text-lg font-semibold">
          ByteMe
        </Link>

        {/* Desktop Navigation */}
        <nav className="hidden md:flex space-x-6">
          {navLinks.map((nav) => (
            <DropdownMenu key={nav.title}>
              <DropdownMenuTrigger asChild>
                <Button variant="ghost">{nav.title}</Button>
              </DropdownMenuTrigger>
              <DropdownMenuContent align="start">
                {nav.submenu.map((item) => (
                  <DropdownMenuItem key={item.title}>
                    <Link href={item.href} className="w-full">
                      {item.title}
                    </Link>
                  </DropdownMenuItem>
                ))}
              </DropdownMenuContent>
            </DropdownMenu>
          ))}
        </nav>

        {/* User Menu or Login Button (Desktop) */}
        <div className="hidden md:block">
          {user ? (
            <DropdownMenu>
              <DropdownMenuTrigger asChild>
                <Button variant="ghost" className="flex items-center gap-2">
                  <Avatar className="h-8 w-8">
                    <AvatarImage src={user.photoURL || ""} />
                    <AvatarFallback>{getUserInitials()}</AvatarFallback>
                  </Avatar>
                  <span className="max-w-[100px] truncate">
                    {user.displayName || user.email?.split('@')[0]}
                  </span>
                </Button>
              </DropdownMenuTrigger>
              <DropdownMenuContent align="end">
                <DropdownMenuItem>
                  <Link href="/account" className="flex items-center w-full">
                    <User className="mr-2 h-4 w-4" />
                    <span>My Account</span>
                  </Link>
                </DropdownMenuItem>
                <DropdownMenuSeparator />
                <DropdownMenuItem onClick={handleSignOut} className="text-red-500">
                  <LogOut className="mr-2 h-4 w-4" />
                  <span>Sign Out</span>
                </DropdownMenuItem>
              </DropdownMenuContent>
            </DropdownMenu>
          ) : (
            <Button asChild>
              <Link href="/login">Login</Link>
            </Button>
          )}
        </div>

        {/* Mobile Menu Button */}
        <Sheet open={mobileOpen} onOpenChange={setMobileOpen}>
          <SheetTrigger asChild>
            <Button variant="ghost" className="md:hidden">
              <Menu className="w-6 h-6" />
            </Button>
          </SheetTrigger>
          <SheetContent side="left" className="w-64">
            <div className="flex justify-between items-center p-4">
              <span className="text-lg font-semibold">Menu</span>
              <Button variant="ghost" size="icon" onClick={() => setMobileOpen(false)}>
                <X className="w-5 h-5" />
              </Button>
            </div>
            
            {/* User info in mobile menu */}
            {user && (
              <div className="p-4 border-b">
                <div className="flex items-center gap-3">
                  <Avatar className="h-10 w-10">
                    <AvatarImage src={user.photoURL || ""} />
                    <AvatarFallback>{getUserInitials()}</AvatarFallback>
                  </Avatar>
                  <div className="flex flex-col">
                    <span className="font-medium">
                      {user.displayName || user.email?.split('@')[0]}
                    </span>
                    {user.email && <span className="text-sm text-muted-foreground">{user.email}</span>}
                  </div>
                </div>
              </div>
            )}
            
            <nav className="flex flex-col space-y-4 p-4">
              {navLinks.map((nav) => (
                <div key={nav.title}>
                  <span className="font-medium">{nav.title}</span>
                  <div className="flex flex-col pl-4 mt-1 space-y-2">
                    {nav.submenu.map((item) => (
                      <Link 
                        key={item.title} 
                        href={item.href} 
                        className="hover:underline"
                        onClick={() => setMobileOpen(false)}
                      >
                        {item.title}
                      </Link>
                    ))}
                  </div>
                </div>
              ))}

              {/* Login/Logout Button (Mobile) */}
              {user ? (
                <Button 
                  variant="destructive" 
                  className="mt-4"
                  onClick={() => {
                    handleSignOut();
                    setMobileOpen(false);
                  }}
                >
                  <LogOut className="mr-2 h-4 w-4" />
                  Sign Out
                </Button>
              ) : (
                <Button asChild className="mt-4">
                  <Link href="/login" onClick={() => setMobileOpen(false)}>Login</Link>
                </Button>
              )}
            </nav>
          </SheetContent>
        </Sheet>
      </div>
    </header>
  );
}
