// app/pc-builder/page.tsx
"use client";

import { useState, useEffect } from 'react';
import { Select, SelectTrigger, SelectValue, SelectContent, SelectItem } from '@/components/ui/select';
import { Button } from '@/components/ui/button';
import { Card, CardHeader, CardTitle, CardContent } from '@/components/ui/card';

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
  { id: 1, name: 'CPU' },
  { id: 2, name: 'GPU' },
  { id: 3, name: 'Motherboard' },
  { id: 4, name: 'RAM' },
  { id: 5, name: 'Storage' },
  { id: 6, name: 'Case' },
  { id: 7, name: 'Power Supply' },
  { id: 8, name: 'Cooling' },
];

export default function PCBuilder() {
  const [components, setComponents] = useState<Component[]>([]);
  const [selectedParts, setSelectedParts] = useState<Record<number, Component | null>>({});
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const fetchComponents = async () => {
      try {
        const response = await fetch('http://localhost:8000/components');
        if (!response.ok) {
          throw new Error('Failed to fetch components');
        }
        const data = await response.json();
        setComponents(data);
      } catch (err) {
        setError(err instanceof Error ? err.message : 'An unknown error occurred');
      } finally {
        setIsLoading(false);
      }
    };

    fetchComponents();
  }, []);

  const handlePartSelect = (categoryId: number, componentId: string) => {
    const selectedComponent = components.find(comp => comp.Id === parseInt(componentId));
    setSelectedParts(prev => ({
      ...prev,
      [categoryId]: selectedComponent || null
    }));
  };

  const handleSave = () => {
    console.log('Selected parts:', selectedParts);
    // Here you would typically send the selected parts to your backend
    alert('PC configuration saved!');
  };

  if (isLoading) {
    return <div className="flex justify-center items-center h-screen">Loading...</div>;
  }

  if (error) {
    return <div className="flex justify-center items-center h-screen text-red-500">{error}</div>;
  }

  const getComponentsByCategory = (categoryId: number) => {
    return components.filter(comp => comp.CategoryId === categoryId);
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
        {categories.map(category => {
          const categoryComponents = getComponentsByCategory(category.id);
          if (categoryComponents.length === 0) return null;

          return (
            <Card key={category.id} className="h-full">
              <CardHeader>
                <CardTitle>{category.name}</CardTitle>
              </CardHeader>
              <CardContent>
                <Select
                  onValueChange={(value) => handlePartSelect(category.id, value)}
                  value={selectedParts[category.id]?.Id.toString() || ''}
                >
                  <SelectTrigger className="w-full">
                    <SelectValue placeholder={`Select ${category.name}`} />
                  </SelectTrigger>
                  <SelectContent>
                    {categoryComponents.map(component => (
                      <SelectItem
                        key={component.Id}
                        value={component.Id.toString()}
                        disabled={component.Stock <= 0}
                      >
                        {component.Name} - ${component.Price.toFixed(2)}
                        {component.Stock <= 0 && ' (Out of stock)'}
                      </SelectItem>
                    ))}
                  </SelectContent>
                </Select>
                
                {selectedParts[category.id] && (
                  <div className="mt-4 p-3 bg-gray-800 rounded-lg">
                    <p className="font-medium">Selected: {selectedParts[category.id]?.Name}</p>
                    <p>Price: ${selectedParts[category.id]?.Price.toFixed(2)}</p>
                    <p>Stock: {selectedParts[category.id]?.Stock}</p>
                  </div>
                )}
              </CardContent>
            </Card>
          );
        })}
      </div>

      <div className="mt-8 p-6 bg-gray-800 rounded-lg">
        <div className="flex justify-between items-center">
          <div>
            <h2 className="text-xl font-bold">Total Price: ${calculateTotalPrice().toFixed(2)}</h2>
            <p className="text-sm text-gray-600">
              {Object.values(selectedParts).filter(Boolean).length} components selected
            </p>
          </div>
          <Button onClick={handleSave} className="px-8 py-4 text-lg">
            Save Configuration
          </Button>
        </div>
      </div>
    </div>
  );
}