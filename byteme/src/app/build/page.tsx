// app/pc-builder/page.tsx
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
let currentUserId : string | null = null;

// Set up the auth state observer
const unsubscribe = onAuthStateChanged(auth, (user) => {
  if (user) {
    currentUserId = user.uid; // Store the UID in the variable
  } else {
    currentUserId = null; // Clear the variable if user signs out
  }
});

export function ComponentCardSkeleton() {
  return (
    <div className="space-y-4">
      <Skeleton className="h-4 w-[250px]" />
      <Skeleton className="h-10 w-full" />
    </div>
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
      // Get the recommendation name from the input field
      const recommendationName = (
        document.getElementById("recommendation_name") as HTMLInputElement
      ).value;

      // Validate that the recommendation name is not empty
      if (!recommendationName.trim()) {
        alert("Please provide a name for your configuration.");
        return;
      }

      // Calculate the total cost of the selected parts
      const totalCost = calculateTotalPrice();

      // Prepare the data to send to the recommendation microservice
      const payload = {
        customer_id: currentUserId, // Replace with the actual customer ID
        name: recommendationName, // Include the recommendation name
        parts_list: selectedParts, // Send the selectedParts object directly
        cost: totalCost, // Include the total cost in the payload
      };

      // Make the POST request to the recommendation microservice
      const response = await fetch("http://localhost:5004/recommendation", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify(payload),
      });

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.message || "Failed to save recommendation");
      }

      const data = await response.json();
      console.log("Recommendation saved successfully:", data);

      alert("PC configuration saved!");
    } catch (error) {
      console.error("Error saving recommendation:", error);
      alert("Failed to save PC configuration. Please try again.");
    }
  };

  if (isLoading) {
    return (
      <div className="container mx-auto px-4 py-8">
        <Skeleton className="h-10 w-[200px] mb-8" />
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {[...Array(6)].map((_, i) => (
            <ComponentCardSkeleton key={i} />
          ))}
        </div>
      </div>
    );
  }
  if (error) {
    return (
      <div className="flex justify-center items-center h-screen text-red-500">
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
    <div className="container mx-auto px-4 py-8">
      <h1 className="text-3xl font-bold mb-8">PC Builder</h1>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        {categories.map((category) => {
          const categoryComponents = getComponentsByCategory(category.id);
          if (categoryComponents.length === 0) return null;

          return (
            <Card key={category.id} className="h-full">
              <CardHeader>
                <CardTitle>{category.name}</CardTitle>
              </CardHeader>
              <CardContent>
                <Select
                  onValueChange={(value) =>
                    handlePartSelect(category.id, value)
                  }
                  value={selectedParts[category.id]?.Id.toString() || ""}
                >
                  <SelectTrigger className="w-full">
                    <SelectValue placeholder={`Select ${category.name}`} />
                  </SelectTrigger>
                  <SelectContent>
                    {categoryComponents.map((component) => (
                      <SelectItem
                        key={component.Id}
                        value={component.Id.toString()}
                        disabled={component.Stock <= 0}
                      >
                        {component.Name} - ${component.Price.toFixed(2)}
                        {component.Stock <= 0 && " (Out of stock)"}
                      </SelectItem>
                    ))}
                  </SelectContent>
                </Select>

                {selectedParts[category.id] && (
                  <div className="mt-4 p-3 bg-gray-800 rounded-lg">
                    <p className="font-medium">
                      Selected: {selectedParts[category.id]?.Name}
                    </p>
                    <p>
                      Price: ${selectedParts[category.id]?.Price.toFixed(2)}
                    </p>
                    <p>Stock: {selectedParts[category.id]?.Stock}</p>
                  </div>
                )}
              </CardContent>
            </Card>
          );
        })}
      </div>

      <div className="grid grid-cols-1 gap-3 my-6">
        <div className="font-bold">Your Selection</div>
        {Object.entries(selectedParts)
          .filter(([_, component]) => component !== null)
          .map(([categoryId, component]) => (
            <div
              key={categoryId}
              className="flex items-center gap-4 p-3 border rounded-lg"
            >
              <div className="w-16 h-16 bg-gray-100 flex items-center justify-center rounded-md">
                <img
                  src={component?.ImageUrl}
                  alt={component?.Name}
                  className="max-w-full max-h-full object-contain p-1"
                />
              </div>
              <div className="flex-1 min-w-0">
                <h3 className="font-medium truncate">{component?.Name}</h3>
                <p className="text-sm text-muted-foreground">
                  {
                    categories.find((cat) => cat.id === parseInt(categoryId))
                      ?.name
                  }
                </p>
              </div>
              <div className="text-right">
                <p className="font-semibold">${component?.Price.toFixed(2)}</p>
                <button
                  className="text-sm text-red-500 hover:text-red-700"
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

      <div className="mt-8 p-6 bg-gray-800 rounded-lg">
        <div className="flex justify-between items-center">
          <div>
            <h2 className="text-xl font-bold">
              Total Price: ${calculateTotalPrice().toFixed(2)}
            </h2>
            <p className="text-sm text-gray-600">
              {Object.values(selectedParts).filter(Boolean).length} components
              selected
            </p>
          </div>
          <div className="flex space-x-2">
            <Input type="text" placeholder="My Configuration" id = "recommendation_name"/>
            <Button onClick={handleSave} className="px-8 py-4 text-lg">
              Save Configuration
            </Button>
          </div>
        </div>
      </div>
    </div>
  );
}
