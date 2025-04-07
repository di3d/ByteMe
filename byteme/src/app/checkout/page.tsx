'use client'

import { useEffect, useState, useRef } from 'react';
import { samplePCBuilds, calculateBuildTotal, getBuildById, PCBuild } from '@/data/sample-pc-build';
import { Select, SelectContent, SelectGroup, SelectItem, SelectLabel, SelectTrigger, SelectValue } from "@/components/ui/select";
import { Card, CardContent, CardDescription, CardFooter, CardHeader, CardTitle } from "@/components/ui/card";
import { ScrollArea } from "@/components/ui/scroll-area";
import { useAuth } from '@/lib/auth-context'; // Add useAuth hook at top

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

const fetchUserRecommendations = async (setRecommendations: React.Dispatch<React.SetStateAction<PCBuild[]>>) => {
  if (!currentUserId) {
    console.error("User is not authenticated.");
    return;
  }

  try {
    const apiUrl = process.env.NEXT_PUBLIC_RECOMMENDATIONS_API_URL || 'http://localhost:5004';
    const response = await fetch(`${apiUrl}/recommendation/customer/${currentUserId}`, {
      method: 'GET',
      headers: {
        'Content-Type': 'application/json',
      },
    });

    if (!response.ok) {
      const errorData = await response.json();
      console.error("Error fetching recommendations:", errorData.message || "Unknown error occurred.");
      return;
    }

    const data = await response.json();
    console.log("User recommendations:", data.data);

    // Fetch full part objects for each recommendation
    const transformedRecommendations = await Promise.all(
      data.data.map(async (rec: any) => {
        const partsList = await Promise.all(
          rec.parts_list.map(async (partId: number) => {
            const partResponse = await fetch(
              `https://personal-0careuf6.outsystemscloud.com/ByteMeComponentService/rest/ComponentAPI/GetComponentById?ComponentId=${partId}`
            );

            if (!partResponse.ok) {
              console.error(`Failed to fetch part with ID ${partId}`);
              return null; // Skip this part if the fetch fails
            }

            const part = await partResponse.json();

            // Map the retrieved part to the expected structure
            return {
              id: part.Id, // Map "Id" to "id"
              name: part.Name, // Map "Name" to "name"
              price: part.Price, // Map "Price" to "price"
              stock: part.Stock, // Include "Stock" if needed
              imageUrl: part.ImageUrl, // Include "ImageUrl" for display
              categoryId: part.CategoryId, // Include "CategoryId" for grouping
            };
          })
        );

        // Filter out any null parts (failed fetches)
        const validPartsList = partsList.filter((part) => part !== null);

        return {
          id: rec.recommendation_id, // Map recommendation_id to id
          name: rec.name,
          items: validPartsList, // Use the fetched part objects
          cost: rec.cost,
        };
      })
    );

    setRecommendations(transformedRecommendations); // Update the recommendations state
  } catch (error) {
    console.error("Failed to fetch recommendations:", error);
  }
};

const groupPartsByCategory = (partsList: any[]) => {
  return partsList.reduce((groups: Record<string, any[]>, part: any) => {
    const category = part.categoryId || "Uncategorized"; // Use "Uncategorized" if categoryId is missing
    if (!groups[category]) {
      groups[category] = [];
    }
    groups[category].push(part);
    return groups;
  }, {});
};

export default function Checkout() {
  const { user } = useAuth(); // Add useAuth hook at top
  const [selectedBuildId, setSelectedBuildId] = useState(samplePCBuilds[0].id);
  const [selectedBuild, setSelectedBuild] = useState<PCBuild>(samplePCBuilds[0]);
  const [recommendations, setRecommendations] = useState<PCBuild[]>([]); // State for recommendations
  const [groupedComponents, setGroupedComponents] = useState<Record<string, any[]>>({});
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [checkoutUrl, setCheckoutUrl] = useState('');
  const hasCreatedSession = useRef(false);
  
  // Fetch recommendations on component mount
  useEffect(() => {
    fetchUserRecommendations(setRecommendations);
  }, []);

  // Update the selected build when the dropdown changes
  useEffect(() => {
    const build = recommendations.find((rec) => rec.id === selectedBuildId) || getBuildById(selectedBuildId);
    if (build) {
      setSelectedBuild(build);

      if (build.items && build.items.length > 0) {
        setGroupedComponents(groupPartsByCategory(build.items)); // Group parts by category using items
      } else {
        console.warn("Selected build has no items:", build);
        setGroupedComponents({}); // Set to an empty object if items are undefined or empty
      }

      setCheckoutUrl('');
      setError('');
      hasCreatedSession.current = false;
    }
  }, [selectedBuildId, recommendations]);

  // Format amount for display
  const formatAmount = (amount: number) => {
    return new Intl.NumberFormat('en-SG', {
      style: 'currency',
      currency: 'SGD'
    }).format(amount);
  };

  // Create and initialize checkout session
  const initializeCheckout = async () => {
    setLoading(true);
    hasCreatedSession.current = true;
    
    const totalAmount = calculateBuildTotal(selectedBuild);
    const stripeApiUrl = process.env.NEXT_PUBLIC_STRIPE_API_URL || 'http://127.0.0.1:5000';

    try {
      const response = await fetch(`${stripeApiUrl}/create-checkout-session`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          amount: totalAmount,
          customer_email: user?.email,
          currency: 'sgd',
          product_name: selectedBuild.name,
          metadata: {
            build_name: selectedBuild.name
          },
          success_url: `${window.location.origin}/success?session_id={CHECKOUT_SESSION_ID}`,
          cancel_url: `${window.location.origin}/checkout?canceled=true`
        })
      });
      
      const data = await response.json();
      
      if (data.error) {
        console.error("Error from server:", data.error);
        setError(data.error);
        setLoading(false);
        return;
      }

      if (!data.url) {
        console.error("No checkout URL received from the server");
        setError('No checkout URL received from the server');
        setLoading(false);
        return;
      }
      
      console.log("Checkout session created, URL:", data.url);
      setCheckoutUrl(data.url);
      setLoading(false);
    } catch (error: any) {
      console.error('Error during session creation:', error);
      setError('Checkout initialization failed: ' + error.message);
      setLoading(false);
    }
  };

  const redirectToCheckout = () => {
    if (checkoutUrl) {
      window.location.href = checkoutUrl;
    }
  };

  const totalAmount = calculateBuildTotal(selectedBuild);

  return (
    <div className="container mx-auto py-10 px-4 max-w-4xl">
      <h1 className="text-3xl font-bold text-center mb-6">Complete Your Purchase</h1>
      <p className="text-gray-500 text-center mb-10">Select a PC build configuration and proceed to checkout</p>
      
      <div className="grid grid-cols-1 gap-8">
        {/* Build Selection */}
        <Card>
          <CardHeader>
            <CardTitle>Select Your PC Build</CardTitle>
            <CardDescription>Choose from our pre-configured custom PC builds</CardDescription>
          </CardHeader>
          <CardContent>
            <Select 
              value={selectedBuildId} 
              onValueChange={(value) => setSelectedBuildId(value)}
            >
              <SelectTrigger className="w-full">
                <SelectValue placeholder="Select a PC build" />
              </SelectTrigger>
              <SelectContent>
                <SelectGroup>
                  <SelectLabel>Recommended Builds</SelectLabel>
                  {recommendations.map((build) => {
                    // Validate the structure of the build object
                    if (!build || !build.cost || !build.name) {
                      console.error("Invalid build structure:", build);
                      return null; // Skip invalid builds
                    }

                    return (
                      <SelectItem key={build.id} value={build.id}>
                        {build.name} - {formatAmount(build.cost)} {/* Use cost directly */}
                      </SelectItem>
                    );
                  })}
                </SelectGroup>
              </SelectContent>
            </Select>
          </CardContent>
        </Card>

        {/* Build Details */}
        <Card>
          <CardHeader>
            <CardTitle>{selectedBuild.name}</CardTitle>
            <CardDescription>{selectedBuild.description || "Detailed configuration of your selected build."}</CardDescription>
          </CardHeader>
          <CardContent>
            <ScrollArea className="h-[300px] pr-4">
              {Object.keys(groupedComponents).map((category) => (
                <div key={category} className="mb-6">
                  <h3 className="font-medium text-lg mb-2">{category}</h3>
                  <ul className="space-y-2">
                    {groupedComponents[category].map((item) => (
                      <li key={item.id} className="flex justify-between items-center border-b pb-2">
                        <div className="flex items-center space-x-4">
                          {item.imageUrl && (
                            <img
                              src={item.imageUrl}
                              alt={item.name || "Part Image"}
                              className="w-12 h-12 object-cover rounded-md"
                            />
                          )}
                          <p className="font-medium">{item.name || "Unnamed Part"}</p>
                        </div>
                        <span className="font-medium">
                          {item.price ? formatAmount(item.price) : "Price Unavailable"}
                        </span>
                      </li>
                    ))}
                  </ul>
                </div>
              ))}
            </ScrollArea>
          </CardContent>
          <CardFooter className="flex justify-between border-t pt-4">
            <div>
              <p className="font-bold text-lg">Total</p>
            </div>
            <p className="font-bold text-lg">{formatAmount(totalAmount)}</p>
          </CardFooter>
        </Card>

        {/* Checkout Actions */}
        <Card>
          <CardContent className="pt-6">
            {loading ? (
              <div className="text-center py-4">
                <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary mx-auto mb-4"></div>
                <p className="text-gray-500">Processing your request...</p>
              </div>
            ) : error ? (
              <div className="text-center py-4">
                <p className="text-red-500 mb-4">{error}</p>
                <button 
                  onClick={() => {
                    setError('');
                    hasCreatedSession.current = false;
                  }}
                  className="px-4 py-2 bg-gray-600 text-white rounded-md hover:bg-gray-500"
                >
                  Try Again
                </button>
              </div>
            ) : checkoutUrl ? (
              <div className="space-y-6">
                <div className="bg-green-50 border border-green-200 rounded-md p-4 text-center">
                  <p className="text-green-800 mb-2 font-medium">Your order is ready for payment</p>
                  <p className="text-sm text-green-600">Click the button below to proceed to our secure checkout</p>
                </div>
                
                <button
                  onClick={redirectToCheckout}
                  className="w-full py-2.5 px-4 bg-blue-600 text-white font-medium rounded-md hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2"
                >
                  Proceed to Secure Checkout
                </button>
              </div>
            ) : (
              <button
                onClick={initializeCheckout}
                className="w-full py-2.5 px-4 bg-blue-600 text-white font-medium rounded-md hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2"
              >
                Continue to Payment
              </button>
            )}
          </CardContent>
        </Card>
      </div>
    </div>
  );
}