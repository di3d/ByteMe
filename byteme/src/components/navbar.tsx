"use client";

import { useState } from "react";
import Link from "next/link";
import { Menu, X } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Sheet, SheetContent, SheetTrigger } from "@/components/ui/sheet";
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuTrigger,
  DropdownMenuItem,
} from "@/components/ui/dropdown-menu";

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
      { title: "Refund", href: "/refund" } // This is correctly set up already
    ],
  },
  {
    title: "About Us",
    href: "/about",
    submenu: [{ title: "Contact", href: "/contact" }],
  },
];

export default function Navbar() {
  const [mobileOpen, setMobileOpen] = useState(false);

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

        {/* Login Button (Desktop) */}
        <div className="hidden md:block">
          <Button asChild>
            <Link href="/login">Login</Link>
          </Button>
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
            <nav className="flex flex-col space-y-4 p-4">
              {navLinks.map((nav) => (
                <div key={nav.title}>
                  <span className="font-medium">{nav.title}</span>
                  <div className="flex flex-col pl-4 mt-1 space-y-2">
                    {nav.submenu.map((item) => (
                      <Link key={item.title} href={item.href} className="hover:underline">
                        {item.title}
                      </Link>
                    ))}
                  </div>
                </div>
              ))}

              {/* Login Button (Mobile) */}
              <Button asChild className="mt-4">
                <Link href="/login">Login</Link>
              </Button>
            </nav>
          </SheetContent>
        </Sheet>
      </div>
    </header>
  );
}
