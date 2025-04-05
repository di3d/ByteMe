"use client"

import { useState, useEffect } from "react"
import { Tabs, TabsList, TabsTrigger, TabsContent } from "@/components/ui/tabs"
import { Skeleton } from "@/components/ui/skeleton"
import { Card, CardHeader, CardContent, CardFooter } from "@/components/ui/card"
import { Badge } from "@/components/ui/badge"

const categories = [
  { id: 1, name: "Processors" },
  { id: 2, name: "Graphics Cards" },
  { id: 3, name: "Motherboards" },
  { id: 4, name: "Memory" },
  { id: 5, name: "Storage" },
  { id: 6, name: "Power Supplies" },
  { id: 7, name: "Cooling" },
]

interface Part {
  Id: number
  Name: string
  Price: number
  Stock: number
  ImageUrl?: string
  CategoryId: number
}

export default function PCPartsBrowser() {
  const [selectedCategory, setSelectedCategory] = useState(categories[0].id)
  const [parts, setParts] = useState<Part[]>([])
  const [loading, setLoading] = useState(false)

  useEffect(() => {
    const fetchParts = async () => {
      setLoading(true)
      try {
        const response = await fetch(
          `https://personal-0careuf6.outsystemscloud.com/ByteMeComponentService/rest/ComponentAPI/FilterComponentByCategory?category=${selectedCategory}`
        )
        const data = await response.json()
        
        const formattedData = data.map((item: any) => ({
          Id: item.Component.Id,
          Name: item.Component.Name,
          Price: item.Component.Price ?? 0,
          Stock: item.Component.Stock ?? 0,
          ImageUrl: item.Component.ImageUrl || "/placeholder-part.png",
          CategoryId: item.Component.CategoryId,
        }))
        
        setParts(formattedData)
      } catch (error) {
        console.error("Error fetching parts:", error)
      } finally {
        setLoading(false)
      }
    }

    fetchParts()
  }, [selectedCategory])

  return (
    <div className="container mx-auto px-4 py-8">
      <div className="mb-8 text-center">
        <h1 className="text-3xl font-bold tracking-tight">PC Component Explorer</h1>
        <p className="text-muted-foreground mt-2">
          Browse and select components for your custom build
        </p>
      </div>

      <Tabs 
        defaultValue={categories[0].id.toString()} 
        onValueChange={(val) => setSelectedCategory(Number(val))}
        className="w-full"
      >
        <TabsList className="grid w-full grid-cols-2 sm:grid-cols-3 md:grid-cols-4 lg:grid-cols-7 h-auto">
          {categories.map((category) => (
            <TabsTrigger 
              key={category.id} 
              value={category.id.toString()}
              className="py-2 text-sm md:text-base"
            >
              {category.name}
            </TabsTrigger>
          ))}
        </TabsList>

        <TabsContent 
          value={selectedCategory.toString()} 
          className="mt-6"
        >
          {loading ? (
            <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-6">
              {Array.from({ length: 8 }).map((_, i) => (
                <Card key={i} className="h-full">
                  <CardHeader>
                    <Skeleton className="h-40 w-full rounded-lg" />
                  </CardHeader>
                  <CardContent className="space-y-2 mt-4">
                    <Skeleton className="h-5 w-3/4" />
                    <Skeleton className="h-4 w-1/2" />
                    <Skeleton className="h-4 w-1/3" />
                  </CardContent>
                </Card>
              ))}
            </div>
          ) : parts.length === 0 ? (
            <div className="flex flex-col items-center justify-center py-12">
              <div className="text-muted-foreground text-center">
                <svg
                  xmlns="http://www.w3.org/2000/svg"
                  width="48"
                  height="48"
                  viewBox="0 0 24 24"
                  fill="none"
                  stroke="currentColor"
                  strokeWidth="2"
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  className="mx-auto mb-4"
                >
                  <path d="M22 16.92v3a2 2 0 0 1-2.18 2 19.79 19.79 0 0 1-8.63-3.07 19.5 19.5 0 0 1-6-6 19.79 19.79 0 0 1-3.07-8.67A2 2 0 0 1 4.11 2h3a2 2 0 0 1 2 1.72 12.84 12.84 0 0 0 .7 2.81 2 2 0 0 1-.45 2.11L8.09 9.91a16 16 0 0 0 6 6l1.27-1.27a2 2 0 0 1 2.11-.45 12.84 12.84 0 0 0 2.81.7A2 2 0 0 1 22 16.92z" />
                </svg>
                <h3 className="text-lg font-medium">No parts available</h3>
                <p className="mt-1">Please check back later or try another category</p>
              </div>
            </div>
          ) : (
            <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-6">
              {parts.map((part) => (
                <Card key={part.Id} className="hover:shadow-lg transition-shadow">
                  <CardHeader className="p-0">
                    <div className="relative aspect-square overflow-hidden rounded-t-lg">
                      <img
                        src={part.ImageUrl}
                        alt={part.Name}
                        className="object-cover w-full h-full transition-all hover:scale-105"
                        onError={(e) => {
                          const target = e.target as HTMLImageElement
                          target.src = "/placeholder-part.png"
                        }}
                      />
                      {part.Stock <= 0 && (
                        <div className="absolute inset-0 bg-black bg-opacity-50 flex items-center justify-center">
                          <Badge variant="destructive" className="text-sm">
                            Out of Stock
                          </Badge>
                        </div>
                      )}
                    </div>
                  </CardHeader>
                  <CardContent className="p-4">
                    <h3 className="font-semibold text-lg line-clamp-2">{part.Name}</h3>
                    <div className="flex items-center justify-between mt-3">
                      <span className="font-bold text-primary">
                        ${part.Price.toFixed(2)}
                      </span>
                      <Badge
                        variant={part.Stock > 5 ? "default" : part.Stock > 0 ? "secondary" : "destructive"}
                      >
                        {part.Stock > 0 ? `${part.Stock} in stock` : "Sold out"}
                      </Badge>
                    </div>
                  </CardContent>
                  <CardFooter className="p-4 pt-0">
                    <button
                      className="w-full bg-primary hover:bg-primary/90 text-primary-foreground py-2 rounded-md transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
                      disabled={part.Stock <= 0}
                    >
                      {part.Stock > 0 ? "Add to Build" : "Notify Me"}
                    </button>
                  </CardFooter>
                </Card>
              ))}
            </div>
          )}
        </TabsContent>
      </Tabs>
    </div>
  )
}