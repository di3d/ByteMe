"use client"

import { useState, useEffect } from "react";
import { Tabs, TabsList, TabsTrigger, TabsContent } from "@/components/ui/tabs";

const categories = ["CPU", "GPU", "RAM", "Storage", "Motherboard", "PSU", "Cooling"];

interface Part {
  id: string;
  name: string;
  price: number;
}

export default function PCPartsBrowser() {
  const [selectedCategory, setSelectedCategory] = useState(categories[0]);
  const [parts, setParts] = useState<Part[]>([]);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    async function fetchParts() {
      setLoading(true);
      try {
        const response = await fetch(`https://your-outsysterms-api.com/parts?category=${selectedCategory}`);
        const data: Part[] = await response.json(); // Explicitly type API response
        setParts(data);
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
      <Tabs defaultValue={categories[0]} onValueChange={setSelectedCategory}>
        <TabsList>
          {categories.map((category) => (
            <TabsTrigger key={category} value={category}>
              {category}
            </TabsTrigger>
          ))}
        </TabsList>
        {categories.map((category) => (
          <TabsContent key={category} value={category}>
            {loading ? (
              <p>Loading...</p>
            ) : (
              <ul>
                {parts.map((part) => (
                  <li key={part.id}>{part.name} - ${part.price}</li>
                ))}
              </ul>
            )}
          </TabsContent>
        ))}
      </Tabs>
    </div>
  );
}
