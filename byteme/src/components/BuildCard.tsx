"use client";

import { useEffect, useState } from "react";
import {
  Card,
  CardContent,
  CardFooter,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";

type PartDetail = {
  Id: number;
  Name: string;
  Price: number;
  Stock: number;
  ImageUrl: string;
  CreatedAt: string;
  CategoryId: number;
};

export default function BuildCard({
  title,
  totalPrice,
  infoRows,
}: {
  title: string;
  totalPrice: number;
  infoRows: number[];
}) {
  const [parts, setParts] = useState<PartDetail[]>([]);

  useEffect(() => {
    async function fetchParts() {
      const fetchedParts = await Promise.all(
        infoRows.map(async (id) => {
          const res = await fetch(
            `https://personal-0careuf6.outsystemscloud.com/ByteMeComponentService/rest/ComponentAPI/GetComponentById?ComponentId=${id}`
          );
          if (!res.ok) return null;
          return res.json();
        })
      );
      setParts(fetchedParts.filter(Boolean));
    }

    fetchParts();
  }, [infoRows]);

  return (
    <Card className="w-full max-w-md mx-auto rounded-2xl shadow-md">
      <CardHeader>
        <CardTitle className="text-xl font-semibold">{title}</CardTitle>
      </CardHeader>

      <CardContent className="space-y-4">
        {parts.length === 0 ? (
          <p className="text-sm text-muted-foreground">Loading parts...</p>
        ) : (
          parts.map((part) => (
            <div key={part.Id} className="flex items-center gap-4">
              <img
                src={part.ImageUrl}
                alt={part.Name}
                className="w-12 h-12 rounded object-contain"
              />
              <div className="flex-1">
                <div className="text-sm font-medium">{part.Name}</div>
                <div className="text-xs text-muted-foreground">
                  ${part.Price.toFixed(2)}
                </div>
              </div>
            </div>
          ))
        )}
      </CardContent>

      <CardFooter className="pt-4">
        <div className="text-sm font-semibold">
          Total Price: ${totalPrice.toFixed(2)}
        </div>
      </CardFooter>
    </Card>
  );
}
