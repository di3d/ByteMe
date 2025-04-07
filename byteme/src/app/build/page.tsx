"use client";

import { useState, useEffect } from "react";
import {
  Select,
  SelectTrigger,
  SelectValue,
  SelectContent,
  SelectItem,
} from "@/components/ui/select";
import { Button } from "@/components/ui/button";
import { Card, CardHeader, CardTitle, CardContent } from "@/components/ui/card";
import { Skeleton } from "@/components/ui/skeleton";
import { Input } from "@/components/ui/input";

// Store and save the user's UID
import { auth } from "@/lib/firebase";
import { onAuthStateChanged } from "firebase/auth";

// Variable to store the user's UID
let currentUserId: string | null = null;

// Set up the auth state observer
const unsubscribe = onAuthStateChanged(auth, (user) => {
  if (user) {
    currentUserId = user.uid;
  } else {
    currentUserId = null;
  }
});

export function ComponentCardSkeleton() {
  return (
    <Card className="bg-gray-700 border-gray-600">
      <CardHeader>
        <Skeleton className="h-6 w-3/4 bg-gray-600" />
      </CardHeader>
      <CardContent>
        <Skeleton className="h-10 w-full bg-gray-600" />
      </CardContent>
    </Card>
  );
}

interface Component {
  Id: number;
  Name: string;
  Price: number;
  Stock: number;
  ImageUrl: string;
  CreatedAt: string;
  CategoryId: number;
}

interface Category {
  id: number;
  name: string;
}

const categories: Category[] = [
  { id: 1, name: "CPU" },
  { id: 2, name: "GPU" },
  { id: 3, name: "Motherboard" },
  { id: 4, name: "RAM" },
  { id: 5, name: "Storage" },
  { id: 6, name: "Case" },
  { id: 7, name: "Power Supply" },
  { id: 8, name: "Cooling" },
];

export default function PCBuilder() {
  const [components, setComponents] = useState<Component[]>([]);
  const [selectedParts, setSelectedParts] = useState<
    Record<number, Component | null>
  >({});
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const fetchComponents = async () => {
      try {
        const response = await fetch("http://localhost:8000/components");
        if (!response.ok) {
          throw new Error("Failed to fetch components");
        }
        const data = await response.json();
        setComponents(data);
      } catch (err) {
        setError(
          err instanceof Error ? err.message : "An unknown error occurred"
        );
      } finally {
        setIsLoading(false);
      }
    };

    fetchComponents();
  }, []);

  const handlePartSelect = (categoryId: number, componentId: string) => {
    const selectedComponent = components.find(
      (comp) => comp.Id === parseInt(componentId)
    );
    setSelectedParts((prev) => ({
      ...prev,
      [categoryId]: selectedComponent || null,
    }));
  };

  const handleSave = async () => {
    try {
      const recommendationName = (
        document.getElementById("recommendation_name") as HTMLInputElement
      ).value;

      if (!recommendationName.trim()) {
        alert("Please provide a name for your configuration.");
        return;
      }

      const totalCost = calculateTotalPrice();

      const payload = {
        customer_id: currentUserId,
        name: recommendationName,
        parts_list: selectedParts,
        cost: totalCost,
      };

      const response = await fetch(
        "http://localhost:8000/recommendation-route/recommendation",
        {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
          },
          body: JSON.stringify(payload),
        }
      );

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.message || "Failed to save recommendation");
      }

      const data = await response.json();
      console.log("Recommendation saved successfully:", data);
      alert("PC configuration saved to the community!");
    } catch (error) {
      console.error("Error saving recommendation:", error);
      alert("Failed to save PC configuration. Please try again.");
    }
  };

  if (isLoading) {
    return (
      <div className="container mx-auto px-4 py-8  min-h-screen">
        <div className="w-full bg-gradient-to-r from-blue-800 via-purple-800 to-pink-800 py-12 px-6 rounded-xl mb-8">
          <h1 className="text-4xl font-extrabold mb-4">Community PC Builder</h1>
          <p className="text-lg">
            Build your perfect PC with recommendations from our community of
            enthusiasts
          </p>
        </div>
        <Skeleton className="h-10 w-[200px] mb-8 bg-gray-700" />
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {[...Array(8)].map((_, i) => (
            <ComponentCardSkeleton key={i} />
          ))}
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="flex justify-center items-center h-screen bg-gray-900 text-red-500">
        {error}
      </div>
    );
  }

  const getComponentsByCategory = (categoryId: number) => {
    return components.filter((comp) => comp.CategoryId === categoryId);
  };

  const calculateTotalPrice = () => {
    return Object.values(selectedParts).reduce(
      (total, component) => total + (component?.Price || 0),
      0
    );
  };

  return (
    <div className="container mx-auto px-4 py-8  min-h-screen text-white">
      <div className="w-full bg-gradient-to-r from-blue-800 via-purple-800 to-pink-800 py-12 px-6 rounded-xl mb-8">
        <h1 className="text-4xl font-extrabold mb-4">Community PC Builder</h1>
        <p className="text-lg">
          Build your perfect PC with recommendations from our community of
          enthusiasts
        </p>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        {categories.map((category) => {
          const categoryComponents = getComponentsByCategory(category.id);
          if (categoryComponents.length === 0) return null;

          return (
            <Card
              key={category.id}
              className="h-full bg-gray-800 border-gray-700"
            >
              <CardHeader>
                <CardTitle className="text-white">{category.name}</CardTitle>
              </CardHeader>
              <CardContent>
                <Select
                  onValueChange={(value) =>
                    handlePartSelect(category.id, value)
                  }
                  value={selectedParts[category.id]?.Id.toString() || ""}
                >
                  <SelectTrigger className="w-full bg-gray-700 border-gray-600 text-white">
                    <SelectValue placeholder={`Select ${category.name}`} />
                  </SelectTrigger>
                  <SelectContent className="bg-gray-800 border-gray-700 text-white">
                    {categoryComponents.map((component) => (
                      <SelectItem
                        key={component.Id}
                        value={component.Id.toString()}
                        disabled={component.Stock <= 0}
                        className="hover:bg-gray-700"
                      >
                        {component.Name} - ${component.Price.toFixed(2)}
                        {component.Stock <= 0 && " (Out of stock)"}
                      </SelectItem>
                    ))}
                  </SelectContent>
                </Select>

                {selectedParts[category.id] && (
                  <div className="mt-4 p-3 bg-gray-700 rounded-lg border border-gray-600">
                    <p className="font-medium text-white">
                      Selected: {selectedParts[category.id]?.Name}
                    </p>
                    <p className="text-gray-300">
                      Price: ${selectedParts[category.id]?.Price.toFixed(2)}
                    </p>
                    <p className="text-gray-300">
                      Stock: {selectedParts[category.id]?.Stock}
                    </p>
                  </div>
                )}
              </CardContent>
            </Card>
          );
        })}
      </div>

      <div className="my-8">
        <h2 className="text-2xl font-bold mb-4 text-white">
          Your Configuration
        </h2>
        {Object.entries(selectedParts)
          .filter(([_, component]) => component !== null)
          .map(([categoryId, component]) => (
            <div
              key={categoryId}
              className="flex items-center gap-4 p-4 bg-gray-800 rounded-lg border border-gray-700 mb-3"
            >
              <div className="w-16 h-16 bg-gray-700 flex items-center justify-center rounded-md">
                <img
                  src={component?.ImageUrl}
                  alt={component?.Name}
                  className="max-w-full max-h-full object-contain p-1"
                />
              </div>
              <div className="flex-1 min-w-0">
                <h3 className="font-medium text-white truncate">
                  {component?.Name}
                </h3>
                <p className="text-sm text-gray-400">
                  {
                    categories.find((cat) => cat.id === parseInt(categoryId))
                      ?.name
                  }
                </p>
              </div>
              <div className="text-right">
                <p className="font-semibold text-white">
                  ${component?.Price.toFixed(2)}
                </p>
                <button
                  className="text-sm text-pink-500 hover:text-pink-400"
                  onClick={() =>
                    setSelectedParts((prev) => ({
                      ...prev,
                      [categoryId]: null,
                    }))
                  }
                >
                  Remove
                </button>
              </div>
            </div>
          ))}
      </div>

      <div className="mt-8 p-6 bg-gradient-to-r from-blue-800/80 to-pink-800/80 rounded-lg border border-gray-700">
        <div className="flex flex-col md:flex-row justify-between items-center gap-4">
          <div>
            <h2 className="text-xl font-bold text-white">
              Total Price: ${calculateTotalPrice().toFixed(2)}
            </h2>
            <p className="text-sm text-gray-300">
              {Object.values(selectedParts).filter(Boolean).length} components
              selected
            </p>
          </div>
          <div className="flex flex-col md:flex-row w-full md:w-auto gap-3">
            <Input
              type="text"
              placeholder="Name your build (e.g. 'Gaming Beast')"
              id="recommendation_name"
              className="bg-gray-800 border-gray-700 text-white placeholder-gray-400"
            />
            <Button
              onClick={handleSave}
              className="px-8 py-4 text-lg bg-white text-blue-600 hover:bg-gray-200"
            >
              Share With Community
            </Button>
          </div>
        </div>
      </div>

      <div className="mt-8 p-6 bg-gray-800 rounded-lg border border-gray-700">
        <h2 className="text-xl font-bold mb-4 text-white">Community Tips</h2>
        <p className="text-gray-300">
          Share your build with the community to help others! Your
          recommendations will appear in our public database where other
          builders can discover and learn from your configurations.
        </p>
      </div>
    </div>
  );
}
