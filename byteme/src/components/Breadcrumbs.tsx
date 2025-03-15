"use client";

import { usePathname } from "next/navigation";
import Link from "next/link";
import { ChevronRight } from "lucide-react";

export default function Breadcrumbs() {
  const pathname = usePathname();
  const pathSegments = pathname.split("/").filter(Boolean);

  return (
    <nav className="flex items-center space-x-2 text-sm text-muted-foreground">
      <Link href="/" className="hover:text-foreground">
        Home
      </Link>

      {pathSegments.length > 0 && (
        <>
          <ChevronRight className="w-4 h-4" />
          {pathSegments.map((segment, index) => {
            const href = "/" + pathSegments.slice(0, index + 1).join("/");
            const isLast = index === pathSegments.length - 1;
            return (
              <span key={href} className="flex items-center space-x-2">
                {index > 0 && <ChevronRight className="w-4 h-4" />}
                {!isLast ? (
                  <Link href={href} className="hover:text-foreground capitalize">
                    {decodeURIComponent(segment)}
                  </Link>
                ) : (
                  <span className="text-foreground font-medium capitalize">
                    {decodeURIComponent(segment)}
                  </span>
                )}
              </span>
            );
          })}
        </>
      )}
    </nav>
  );
}
