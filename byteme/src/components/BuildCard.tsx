"use client";

import {
  Card,
  CardContent,
  CardFooter,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";

export default function BuildCard(
  {
    title,
    totalPrice,
    infoRows,
  }: {
    title: string;
    totalPrice: number;
    infoRows: { label: string; value: string }[];
  },
  
) {
  return (
    <Card className="w-full max-w-md mx-auto rounded-2xl shadow-md">
      <CardHeader>
        <CardTitle className="text-xl font-semibold">{title}</CardTitle>
      </CardHeader>
      <CardContent className="space-y-2">
        {infoRows.map((row, index) => (
          <div
            key={index}
            className="flex justify-between items-center border-b pb-1 last:border-none"
          >
            <span className="text-muted-foreground">{row.label}</span>
            <span className="font-medium">{row.value}</span>
          </div>
        ))}
      </CardContent>
      <CardFooter>
        <div>Total Price: ${String(totalPrice)}</div>
      </CardFooter>
    </Card>
  );
}
