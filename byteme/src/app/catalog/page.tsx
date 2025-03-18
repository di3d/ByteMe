"use client"

import { useState, useEffect } from "react";
import { Tabs, TabsList, TabsTrigger, TabsContent } from "@/components/ui/tabs";

const categories = [
  { id: 1, name: "CPU" },
  { id: 2, name: "GPU" },
  { id: 3, name: "Motherboard" },
  { id: 4, name: "RAM" },
  { id: 5, name: "Storage" },
  { id: 6, name: "PSU" },
  { id: 7, name: "Cooling" },
];

interface Part {
  Id: number;
  Name: string;
  Price: number;
  Stock: number;
  ImageUrl?: string;
  CategoryId: number;
}

export default function PCPartsBrowser() {
  const [selectedCategory, setSelectedCategory] = useState(categories[0].id);
  const [parts, setParts] = useState<Part[]>([]);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    async function fetchParts() {
      setLoading(true);
      try {
        const response = await fetch(
          `https://personal-0careuf6.outsystemscloud.com/ByteMeComponentService/rest/ComponentAPI/FilterComponentByCategory?category=${selectedCategory}`
        );
        const data = await response.json();
        
        // Adjusted mapping to match new API response format
        const formattedData = data.map((item: any) => ({
          Id: item.Component.Id,
          Name: item.Component.Name,
          Price: item.Component.Price ?? 0, // Default to 0 if undefined
          Stock: item.Component.Stock ?? 0,
          ImageUrl: item.Component.ImageUrl || "", // Ensure a fallback value
          CategoryId: item.Component.CategoryId,
        }));
        
        setParts(formattedData);
      } catch (error) {
        console.error("Error fetching parts:", error);
      } finally {
        setLoading(false);
      }
    }

    fetchParts();
  }, [selectedCategory]);

  return (
    <div className="p-4">
      <Tabs defaultValue={categories[0].id.toString()} onValueChange={(val) => setSelectedCategory(Number(val))}>
        <TabsList>
          {categories.map((category) => (
            <TabsTrigger key={category.id} value={category.id.toString()}>
              {category.name}
            </TabsTrigger>
          ))}
        </TabsList>
        <TabsContent key={selectedCategory} value={selectedCategory.toString()} className="flex flex-col items-center">
          {loading ? (
            <p>Loading...</p>
          ) : parts.length === 0 ? (
            <p>No parts available</p>
          ) : (
            <ul className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
              {parts.map((part) => (
                <li key={part.Id} className="border p-4 rounded-lg shadow-md flex flex-col items-center">
                  {part.ImageUrl && (
                    <img src={part.ImageUrl} alt={part.Name} className="w-40 h-40 object-cover mb-2" />
                  )}
                  <p className="font-semibold text-center">{part.Name}</p>
                  <p className="text-gray-700">${part.Price.toFixed(2)}</p>
                  <p className="text-sm text-gray-500">Stock: {part.Stock}</p>
                </li>
              ))}
            </ul>
          )}
        </TabsContent>
      </Tabs>
    </div>
  );
}