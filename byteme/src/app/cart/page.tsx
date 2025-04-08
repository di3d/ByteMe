"use client";

import { useEffect, useState } from "react";
import axios from "axios";
import { useAuth } from "@/lib/auth-context";
import { CartDisplay } from "@/components/CartDisplay";

// Define TypeScript types
type CartItem = {
  cart_id: string;
  customer_id: string;
  name: string;
  parts_list: number[];
  total_cost: number;
};

type ApiResponse = {
  data: CartItem[];
  // Add other response fields if your API returns more
};

export default function Cart() {
  const { user, loading: authLoading } = useAuth();
  const [data, setData] = useState<ApiResponse | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (authLoading) {
      return;
    }

    if (!user) {
      setError("User is not logged in");
      setLoading(false);
      return;
    }

    const fetchData = async () => {
      const options = {
        method: "GET",
        url: `http://localhost:8000/cart/customer/${user.uid}`,
      };

      try {
        const response = await axios.request<ApiResponse>(options);
        setData(response.data);
      } catch (error) {
        if (axios.isAxiosError(error)) {
          setError(error.response?.data?.message || error.message);
        } else if (error instanceof Error) {
          setError(error.message);
        } else {
          setError("An unexpected error occurred");
        }
      } finally {
        setLoading(false);
      }
    };

    fetchData();
  }, [user, authLoading]);

  if (authLoading) return <div>Loading authentication...</div>;
  if (loading) return <div>Loading cart data...</div>;
  if (error) return <div>Error: {error}</div>;
  if (!data) return <div>No cart data available</div>;

  return (
    <div className="container mx-auto p-4">
      <h1 className="text-2xl font-bold mb-6">Your Carts</h1>
      {data.data.length === 0 ? (
        <div className="text-center py-8">
          <p className="text-muted-foreground">You have no shopping carts</p>
        </div>
      ) : (
        <div className="space-y-4">
          {data.data.map((cart) => (
            <CartDisplay key={cart.cart_id} cart={cart} />
          ))}
        </div>
      )}
    </div>
  );
}